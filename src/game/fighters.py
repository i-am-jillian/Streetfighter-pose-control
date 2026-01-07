import pygame
from actions import Actions

GRAVITY = 2
JUMP_VELOCITY = -30
FLOOR_TOP_Y = 310
IDLE = 0
PUNCH = 1
KICK = 2

class Fighter():
    def __init__(self, x, y):
        self.flip = False
        self.rect = pygame.Rect(x, y, 130, 180)
        self.speed = 10
        self.vel_y = 0
        self.health = 100

        self.attacking = False
        self.attack_timer = 0
        self.hit_applied = False

        self.action = IDLE
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.animation_cooldown = 300

        self.animations = []
        self.load_images()


    def load_images(self):
        self.animations = []

        idle_frames = self.load_idle_sheet(
            "assets/sprites/Fighter1/Shinchan-idle.png", 3
        )

        self.animations.append(idle_frames)

        punch = pygame.image.load("assets/sprites/Fighter1/Shinchan-punch.png").convert_alpha()
        punch = pygame.transform.scale(punch, (180, 200))
        self.animations.append([punch])
        
        kick = pygame.image.load("assets/sprites/Fighter1/Shinchan-kick.png").convert_alpha()
        kick = pygame.transform.scale(kick, (180, 200))
        self.animations.append([kick])

    def load_idle_sheet(self, path, frames):
        sheet = pygame.image.load(path).convert_alpha()
        frame_width = sheet.get_width()//frames
        frame_height = sheet.get_height()

        animation = []
        for i in range(frames):
            frame = sheet.subsurface(i * frame_width, 0, frame_width, frame_height)
            frame = pygame.transform.scale(frame, (130, 220))
            animation.append(frame)
        return animation
    
    def set_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    
    def update_animation(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.update_time > self.animation_cooldown:
            self.update_time = current_time
            self.frame_index += 1

            if self.frame_index >= len(self.animations[self.action]):
                self.frame_index = 0


    def movey(self, actions: Actions):
        if self.attacking == False:
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

    def movex(self, actions: Actions, target):
        if self.attacking == False:
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

            #ensure players face each other
            #if target.rect.centerx > self.rect.centerx:
            #    self.flip = False
            #else:
             #   self.flip = True

            if actions.movex > 0:
                self.flip = False
            elif actions.movex < 0:
                self.flip = True

    def attack(self, surface, target):
        if not self.attacking:
            return
        
        # Define attack hitbox
        hitbox_width = 2
        hitbox_height = 60

        if self.flip:
            hitbox_x = self.rect.left - hitbox_width
        else:
            hitbox_x = self.rect.right
        
        attacking_rect = pygame.Rect(
            hitbox_x,
            self.rect.y + self.rect.height // 4,
            hitbox_width,
            hitbox_height
        )
        if attacking_rect.colliderect(target.rect) and not self.hit_applied:
            target.health -= 10
            target.health = max(0, target.health)
            self.hit_applied = True

        #pygame.draw.rect(surface, (0, 255, 0), attacking_rect, 2)

    def handle_attack(self, actions: Actions):
        #if already attacking, count down
        if self.attack_timer > 0:
            self.attack_timer -= 1
            return
        
        if self.attacking:
            self.attacking = False
            self.set_action(IDLE)
            return
        
        #start new attack
        if actions.punch:
            self.attack_timer = 12
            self.attacking = True
            self.hit_applied = False
            self.set_action(PUNCH)

        elif actions.kick:
            self.attack_timer = 16
            self.attacking = True
            self.hit_applied = False 
            self.set_action(KICK)
         

    def draw(self, surface):
        self.update_animation()
        image = self.animations[self.action][self.frame_index]
        if self.flip:
            image = pygame.transform.flip(image, True, False)

        surface.blit(image, self.rect)