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

        self.cooldown = {"punch": 0, "kick": 0, "jump": 0, "move_left": 0, "move_right": 0}
    
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
        ELBOW_THRESHOLD = 155
        EXTENSION_MIN = 0.80
        VEL_MIN = 0.035

        def punch_detected(elbow_degree, extension, vx, wrist_pos, shoulder_pos):

            #print(f"Punch check - Elbow: {elbow_degree:.1f}°, Ext: {extension:.2f}, Vx: {vx:.3f}")

            if (elbow_degree < ELBOW_THRESHOLD):
                return False
            if (extension < EXTENSION_MIN):
                return False
            
            if abs(vx) < VEL_MIN:
                return False
            
            outward = (wrist_pos[0] - shoulder_pos[0])
            if outward * vx <= 0:
                return False
            
            wrist_shoulder_height_diff = abs(wrist_pos[1] - shoulder_pos[1])
            if wrist_shoulder_height_diff > 0.15:
                return False
            return True
        
        if self.cooldown["punch"] == 0:
            
            right_arm_punching = punch_detected(right_elbow_degree, right_extension, r_vx, rw, rs)
            left_arm_punching = punch_detected(left_elbow_degree, left_extension, l_vx, lw, ls)
            
            if right_arm_punching or left_arm_punching:
                
                if (right_arm_punching and r_vx > 0) or (left_arm_punching and l_vx > 0):
                    actions.append("PUNCH_RIGHT")
                
                elif (right_arm_punching and r_vx < 0) or (left_arm_punching and l_vx < 0):
                    actions.append("PUNCH_LEFT")
                else:
                    actions.append("PUNCH")
                
                self.cooldown["punch"] = 5

        #kick
        rk = xy(landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value])
        ra = xy(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value])
        self.ra_history.append(ra)

        lk = xy(landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value])
        la = xy(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value])
        self.la_history.append(la)

        #knee up check
        KNEE_LIFT = 0.05         # knee above hip by this margin
        KNEE_ANGLE_MAX = 90

        def kick_detected(hip_pos, knee_pos, ankle_pos):  # side = "right" or "left"
            lift_amount = hip_pos[1] - knee_pos[1]
            knee_lifted = lift_amount > KNEE_LIFT

            if not knee_lifted:
                return False
            
            knee_angle_val = angle(hip_pos, knee_pos, ankle_pos)

            if knee_angle_val > KNEE_ANGLE_MAX: 
                return False
            
            print(f"Kick check - Lift: {lift_amount:.3f}, Angle: {knee_angle_val:.1f}°")

            return True
            
        if self.cooldown["kick"] == 0:
            right_kick = kick_detected(rh, rk, ra)
            left_kick = kick_detected(lh, lk, la)
            
            if facing == "right":
                if right_kick or left_kick:
                    actions.append("KICK_RIGHT")
                    self.cooldown["kick"] = 6
            elif facing == "left":
                if left_kick or right_kick:
                    actions.append("KICK_LEFT")
                    self.cooldown["kick"] = 6
            else:
                if right_kick or left_kick:
                    actions.append("KICK")
                    self.cooldown["kick"] = 6


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
                    self.cooldown["jump"] = 5
                    print("jump detected")

        #Movement detection
        ls_landmark = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        rs_landmark = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        
        if self.cooldown["move_left"] == 0:
            if visible_enough([ls_landmark.visibility, l_w.visibility], threshold=0.5):
                left_hand_high = (l_w.y < ls[1] - 0.05)
                right_hand_low = (r_w.y > rs[1] + 0.02)
                
                if left_hand_high and right_hand_low:
                    actions.append("MOVE_LEFT")
                    self.cooldown["move_left"] = 1
                    print("MOVE_LEFT DETECTED")

        if self.cooldown["move_right"] == 0:
            if visible_enough([rs_landmark.visibility, r_w.visibility], threshold=0.5):
                right_hand_high = (r_w.y < rs[1] - 0.05)
                left_hand_low = (l_w.y > ls[1] + 0.02)
                
                if right_hand_high and left_hand_low:
                    actions.append("MOVE_RIGHT")
                    self.cooldown["move_right"] = 1
                    print("MOVE_RIGHT DETECTED")

        if actions:
            print(f"All detected actions: {actions}")

        self.cooldowns()
        return actions
    


