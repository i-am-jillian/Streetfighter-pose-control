import pygame
from actions import Actions

def get_actions_player1() -> Actions:
    key = pygame.key.get_pressed()

        #movement
    #movement
    movex = 0
    if key[pygame.K_LEFT]:
        movex = -1
    elif key[pygame.K_RIGHT]:
        movex = 1

    return Actions(movex=movex)