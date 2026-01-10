import pygame
from fighters import IDLE, PUNCH, KICK, WIN, DEAD, Fighter
from actions import Actions #importing class from the actions.py file
from input_keyboard import get_actions_player1 #importing function from input_keyboard.py file
from bot import FighterAI

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

gameOver_img = pygame.image.load("assets/sprites/GameOver/GameOver.png").convert_alpha()
gameOver_img = pygame.transform.scale(gameOver_img, (400, 400))

winner_img = pygame.image.load("assets/sprites/GameOver/YouWin.png").convert_alpha()
winner_img = pygame.transform.scale(winner_img, (500, 300))

UI_X_WIN = SCREEN_WIDTH // 2 - 250
UI_Y_WIN = 10

UI_X_OVER = SCREEN_WIDTH // 2 - 200
UI_Y_OVER = -20

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
fighter1 = Fighter(200, 310)
fighter2 = FighterAI(700, 310)
game_state = PLAYING
winner = None

#main game loop

run = True
while run:
    clock.tick(FPS)

    #draw background
    draw_background()

    #show health bars
    draw_health_bar(fighter1.health, 20, 20)
    draw_health_bar(fighter2.health, 580, 20)

    if game_state == PLAYING:
        actions_p1 = get_actions_player1()

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

        #create action instances for each player

        #move fighters
    #fighter1.movex(actions_p1, fighter2)
    #fighter1.movey(actions_p1)

    #fighter1.handle_attack(actions_p1)
    #fighter1.attack(screen, fighter2)

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