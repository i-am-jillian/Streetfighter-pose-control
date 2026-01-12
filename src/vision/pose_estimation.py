import cv2 #importing open cv library
import mediapipe as mp #importing mediapipe library
import numpy as np #importing numpy library for numerical operations
mp_drawing = mp.solutions.drawing_utils #drawing utilities for visualizing the pose
mp_pose = mp.solutions.pose #pose estimation model from mediapipe

#video
cap = cv2.VideoCapture(0) #capturing video from the default camera
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened(): #checking if the camera is opened successfully
        ret, frame = cap.read() #reading a frame from the camera

        #recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #converting the frame from BGR to RGB
        image.flags.writeable = False #setting the image to non-writeable to improve performance

        #make detection
        results = pose.process(image)

        #recolor back to BGR
        image.flags.writeable = True #setting the image back to writeable
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) #converting the image back to BGR

        #extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
        except:
            pass

        #render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), #color for the points
                                  mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2) #color for the lines 
                                ) #drawing the pose landmarks on the image

        cv2.imshow("MediaPipe Feed", image) #pop up on the screen showing the frame

        if cv2.waitKey(10) & 0xFF == ord("q"): #exist if 'q' is pressed
            break
    cap.release() #releasing the camera
    cv2.destroyAllWindows() #closing all the windows opened by opencv



