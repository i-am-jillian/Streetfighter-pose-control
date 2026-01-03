import pygame
from fighters import Fighter #importing class from the fighter.py file
from actions import Actions #importing class from the actions.py file
from input_keyboard import get_actions_player1 #importing function from input_keyboard.py file

pygame.init() #initialized pygame

#create game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #create window with set dimensions
pygame.display.set_caption("StreetFighter Pose Control") #set window title

#set framerate
clock = pygame.time.Clock()
FPS = 60

#load backgroung image
background_image = pygame.image.load("assets/backgrounds/background.jpg").convert_alpha()

#function to draw background
def draw_background():
    scaled_background = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_background, (0, 0)) #draw background at top-left corner

#create fighter instance
fighter1 = Fighter(200, 310)
fighter2 = Fighter(700, 310)

#main game loop
run = True
while run:
    clock.tick(FPS)

    #draw background
    draw_background()

    #create action instances for each player
    actions_p1 = get_actions_player1()
    #move fighters
    fighter1.movex(actions_p1)

    #draw fighters
    fighter1.draw(screen)
    fighter2.draw(screen)

    #event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False


    #update display
    pygame.display.update()

#exit pygame
pygame.quit()