import pygame
from actions import Actions

GRAVITY = 2
JUMP_VELOCITY = -30
FLOOR_TOP_Y = 310

class Fighter():
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 80, 180)
        self.speed = 10
        self.vel_y = 0
    
    def movey(self, actions: Actions):
        # Apply gravity
        onGround = self.rect.y >= FLOOR_TOP_Y
        if actions.jump and onGround:
            self.vel_y = JUMP_VELOCITY

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Prevent falling below the floor
        if self.rect.y > FLOOR_TOP_Y:
            self.rect.y = FLOOR_TOP_Y
            self.vel_y = 0

    def movex(self, actions: Actions):
        self.rect.x += actions.movex * self.speed
        
        # Keep fighter within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 1000:
            self.rect.right = 1000
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > 600:
            self.rect.bottom = 600

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 0, 0), self.rect)


    