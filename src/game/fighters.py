import pygame
from actions import Actions

class Fighter():
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 80, 180)
        self.speed = 10

    def movex(self, actions: Actions):
        self.rect.x += actions.movex * self.speed
        
        # Keep fighter within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 1000:
            self.rect.right = 1000

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), self.rect)


    