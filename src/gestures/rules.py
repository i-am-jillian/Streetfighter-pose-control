from collections import deque
import mediapipe as mp
from pose_math import xy, distance, angle, avg, visible_enough

mp_pose = mp.solutions.pose

class ActionDetector:
    def __init__(self):
        self.rw_history = deque(maxlen = 6)
        self.lw_history = deque(maxlen = 6)
        self.ra_history = deque(maxlen = 6)
        self.la_history = deque(maxlen = 6)
        self.leaning_history = deque(maxlen = 8)

        self.cooldown = {"punch": 0, "kick": 0, "jump": 0, "move": 0}
    
    #cooldown
    def cooldowns(self):
        for key in self.cooldown:
            self.cooldown[key] = max(0, self.cooldown[key] - 1)

    def velocity(self, history):
        if len(history) < 2:
            return (0.0, 0.0)
        dx = history[-1][0] - history[0][0]
        dy = history[-1][1] - history[0][1]
        return (dx, dy)

    def update(self, landmarks, fighter2_x = None):

        actions = []

        # Compute scale based on shoulder width
        ls = xy(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value])
        rs = xy(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value])
        scale = distance(ls, rs) + 1e-6

        #centers for lean and facing
        lh = xy(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value])
        rh = xy(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value])
        hip_c = avg(lh, rh)
        sh_c = avg(ls, rs)

        #facing based on opponent
        if fighter2_x is not None:
            facing = "right" if fighter2_x > hip_c[0] else "left"
        else:
            facing = None

        #PUNCH
        #Right arm
        re = xy(landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value])
        rw = xy(landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value])
        self.rw_history.append(rw)

        #left arm
        le = xy(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value])
        lw = xy(landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value])
        self.lw_history.append(lw)

        right_elbow_degree = angle(rs, re, rw)
        left_elbow_degree = angle(ls, le, lw)

        right_extension = distance(rs, rw) / scale
        left_extension = distance(ls, lw) / scale

        r_vx, r_vy = self.velocity(self.rw_history)
        l_vx, l_vy = self.velocity(self.lw_history)

        #thesholds
        ELBOW_THRESHOLD = 150
        EXTENSION_MIN = 0.75
        VEL_MIN = 0.025

        def punch_detected(elbow_degree, extension, vx, wrist_pos, shoulder_pos):
            if (elbow_degree < ELBOW_THRESHOLD):
                return False
            if (extension < EXTENSION_MIN):
                return False
            
            if abs(vx) < VEL_MIN:
                return False
            
            outward = (wrist_pos[0] - shoulder_pos[0])
            if abs(vx) < VEL_MIN:
                return False
            if outward * vx <= 0:
                return False
            return True
        
        if self.cooldown["punch"] == 0:
            if facing == "right":
                r_right = (rw[0]>rs[0])
                l_right = (lw[0]>ls[0])

                if punch_detected(right_elbow_degree, right_extension, r_vx, rw, rs):
                    actions.append("PUNCH_RIGHT")
                    self.cooldown["punch"] = 10

                elif punch_detected(left_elbow_degree, left_extension, l_vx, lw, ls):
                    actions.append("PUNCH_RIGHT")
                    self.cooldown["punch"] = 10

            elif facing == "left":
                if punch_detected(left_elbow_degree, left_extension, l_vx, lw, ls):
                    actions.append("PUNCH_LEFT")
                    self.cooldown["punch"] = 10

                elif punch_detected(right_elbow_degree, right_extension, r_vx, rw, rs):
                    actions.append("PUNCH_LEFT")
                    self.cooldown["punch"] = 10

            else: 
                if punch_detected(right_elbow_degree, right_extension, r_vx, rw, rs) or punch_detected(left_elbow_degree, left_extension, l_vx, lw, ls):
                    actions.append("PUNCH")
                    self.cooldown["punch"] = 10

        #kick
        rk = xy(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value])
        ra = xy(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value])
        self.ra_history.append(ra)

        lk = xy(landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value])
        la = xy(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value])
        self.la_history.append(la)

        #knee up check
        KNEE_LIFT = 0.08         # knee above hip by this margin
        KNEE_ANGLE_MIN = 90

        def kick_detected(hip_pos, knee_pos, ankle_pos):  # side = "right" or "left"
            knee_lifted = (hip_pos[1] - knee_pos[1]) > KNEE_LIFT
            if not knee_lifted:
                return False
            
            knee_angle_val = angle(hip_pos, knee_pos, ankle_pos)
            if knee_angle_val > 160:  # Too straight, not a kick motion
                return False
            
            return True
            
        if self.cooldown["kick"] == 0:
            right_kick = kick_detected(rh, rk, ra)
            left_kick = kick_detected(lh, lk, la)
            
            if facing == "right":
                # Right kick for right-facing fighter
                if right_kick:
                    actions.append("KICK_RIGHT")
                    self.cooldown["kick"] = 15
                elif left_kick:
                    actions.append("KICK_RIGHT")
                    self.cooldown["kick"] = 15
            elif facing == "left":
                # Left kick for left-facing fighter
                if left_kick:
                    actions.append("KICK_LEFT")
                    self.cooldown["kick"] = 15
                elif right_kick:
                    actions.append("KICK_LEFT")
                    self.cooldown["kick"] = 15
            else:
                # No facing, detect any kick
                if right_kick or left_kick:
                    actions.append("KICK")
                    self.cooldown["kick"] = 15


        #jump
        nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
        r_w = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
        l_w = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]

        if self.cooldown["jump"] == 0:
            if visible_enough([nose.visibility, r_w.visibility, l_w.visibility], threshold=0.6):
                margin = 0.05
                both_hands_up = (r_w.y < nose.y - margin) and (l_w.y < nose.y - margin)
                if both_hands_up:
                    actions.append("JUMP")
                    self.cooldown["jump"] = 30

        lean = (sh_c[0] - hip_c[0]) / scale
        self.leaning_history.append(lean)
        lean_avg = sum(self.leaning_history) / len(self.leaning_history)

        LEAN_THRESHOLD = 0.08
        if self.cooldown["move"] == 0:
            if lean_avg > LEAN_THRESHOLD:
                actions.append("MOVE_RIGHT")
                self.cooldown["move"] = 6
            elif lean_avg < -LEAN_THRESHOLD:
                actions.append("MOVE_LEFT")
                self.cooldown["move"] = 6

        self.cooldowns()
        return actions
    


