import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)
sys.path.append(os.path.join(parent_dir, 'gestures'))

import cv2
import pygame
import mediapipe as mp
from fighters import IDLE, PUNCH, KICK, WIN, DEAD, Fighter
from actions import Actions #importing class from the actions.py file
from input_keyboard import get_actions_player1 #importing function from input_keyboard.py file
from bot import FighterAI
from gestures.rules import ActionDetector

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

pygame.init() #initialized pygame

#create game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
PLAYING = 0
GAME_OVER = 1

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #create window with set dimensions
pygame.display.set_caption("StreetFighter Pose Control") #set window title

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define colors
YELLOW = (255, 221, 38)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

#load backgroung image
background_image = pygame.image.load("assets/backgrounds/background.jpg").convert_alpha()

ko_img = pygame.image.load("assets/sprites/GameOver/KO.png").convert_alpha()
ko_img = pygame.transform.scale(ko_img, (150, 100))

gameOver_img = pygame.image.load("assets/sprites/GameOver/GameOver.png").convert_alpha()
gameOver_img = pygame.transform.scale(gameOver_img, (400, 400))

winner_img = pygame.image.load("assets/sprites/GameOver/YouWin.png").convert_alpha()
winner_img = pygame.transform.scale(winner_img, (500, 300))

UI_X_WIN = SCREEN_WIDTH // 2 - 250
UI_Y_WIN = 10

UI_X_OVER = SCREEN_WIDTH // 2 - 200
UI_Y_OVER = -20

KO_X = SCREEN_WIDTH // 2 - 65
KO_Y = -10
#function to draw background
def draw_background():
    scaled_background = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_background, (0, 0)) #draw background at top-left corner

#function to draw fighter health bars
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x-2, y-2, 404, 34)) #draw border
    pygame.draw.rect(screen, RED, (x, y, 400, 30)) #draw background bar
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30)) #draw background bar

def fighterOverlap(a,b):
    if not a.rect.colliderect(b.rect):
        return
    overlap_left = a.rect.right - b.rect.left
    overlap_right = b.rect.right - a.rect.left
    push = min(overlap_left, overlap_right)

    if a.rect.centerx < b.rect.centerx:
        a.rect.x -= push // 2
        b.rect.x += push - push // 2
    else:
        a.rect.x += push // 2
        b.rect.x -= push - push // 2

    a.rect.left = max(0, a.rect.left)
    a.rect.right = min(1000, a.rect.right)
    b.rect.left = max(0, b.rect.left)
    b.rect.right = min(1000, b.rect.right)

#create fighter instance
fighter1 = Fighter(200, 310, variant="player")
fighter2 = FighterAI(700, 310)
game_state = PLAYING
winner = None

#Initialize webcam detection
cap = cv2.VideoCapture(0) #capturing video from the default camera

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640) #setting width of the frame
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) #setting height of the frame
cap.set(cv2.CAP_PROP_FPS, 30) #setting frames per second

action_detector = ActionDetector()
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity = 0)

frame_count = 0
POSE_PROCESS_INTERVAL = 1  # Process every 2nd frame

#MAIN GAME LOOP
run = True
while run:
    clock.tick(FPS)

    actions_p1 = Actions()

    if frame_count % POSE_PROCESS_INTERVAL == 0:
        ret, frame = cap.read() #reading the frame from the webcam

        if ret:
            frame = cv2.flip(frame, 1) #flipping the frame horizontally for a mirror effect
            #recolor image to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #converting the frame from BGR to RGB
            image.flags.writeable = False #setting the image to non-writeable to improve performance
            #make detection
            results = pose.process(image)

            #recolor back to BGR
            image.flags.writeable = True #setting the image back to writeable
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
            
                detected_actions = action_detector.update(landmarks, fighter2.rect.centerx)

                #convert detected actions to Actions instance
                for action in detected_actions:
                    if action in ["PUNCH_RIGHT", "PUNCH_LEFT", "PUNCH"]:
                        actions_p1.punch = True
                    elif action in ["KICK_RIGHT", "KICK_LEFT", "KICK"]:
                        actions_p1.kick = True
                    elif action == "JUMP":
                        actions_p1.jump = True
                    elif action == "MOVE_LEFT":
                        actions_p1.movex = 1
                    elif action == "MOVE_RIGHT":
                        actions_p1.movex = -1
                

                mp_drawing.draw_landmarks(image, 
                                      results.pose_landmarks, 
                                      mp_pose.POSE_CONNECTIONS, 
                                      mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                      mp_drawing.DrawingSpec(color=(0,0,255), thickness=2, circle_radius=2))
            
            cv2.imshow("MediaPipe Feed", image) #pop up on the screen showing the frame

    frame_count += 1
    #draw background
    draw_background()

    #show health bars
    draw_health_bar(fighter1.health, 20, 20)
    draw_health_bar(fighter2.health, 580, 20)

    #show ko image
    screen.blit(ko_img, (KO_X, KO_Y))

    if game_state == PLAYING:
        #actions_p1 = get_actions_player1()

        fighter1.movex(actions_p1, fighter2)
        fighter1.movey(actions_p1)
        fighter1.handle_attack(actions_p1)
        fighter1.attack(screen, fighter2)

        #update bot fighter
        actions_p2 = fighter2.getActions(fighter1)
        fighter2.movex(actions_p2, fighter1)
        fighter2.movey(actions_p2)
        fighter2.handle_attack(actions_p2)
        fighter2.attack(screen, fighter1)

        fighterOverlap(fighter1, fighter2)

        #check game over
        if fighter1.health <= 0:
            game_state = GAME_OVER
            winner = "Player 2"
            fighter1.set_action(DEAD)
            fighter2.set_action(WIN)

        elif fighter2.health <= 0:
            game_state = GAME_OVER
            winner = "Player 1"
            fighter2.set_action(DEAD)
            fighter1.set_action(WIN)

    if game_state == GAME_OVER:
            if winner == "Player 1":
                screen.blit(winner_img, (UI_X_WIN, UI_Y_WIN))
            else:
                screen.blit(gameOver_img, (UI_X_OVER, UI_Y_OVER))


    #draw fighters
    fighter1.draw(screen)
    fighter2.draw(screen)

    #event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if cv2.waitKey(10) & 0xFF == ord("q"): #exist if 'q' is pressed
        break
    #update display
    pygame.display.update()

#exit pygame
cap.release()
cv2.destroyAllWindows()
pygame.quit()