from matplotlib import scale
import pygame
from actions import Actions

GRAVITY = 2 
JUMP_VELOCITY = -30
FLOOR_TOP_Y = 310

IDLE = 0
PUNCH = 1
KICK = 2
WIN = 3
DEAD = 4

class Fighter():
    def __init__(self, x, y, variant="player"):
        self.variant = variant #player or bot

        self.flip = False
        self.rect = pygame.Rect(x, y, 130, 180)
        self.speed = 20
        self.vel_y = 0
        self.health = 100

        self.attacking = False
        self.attack_timer = 0
        self.hit_applied = False

        self.action = IDLE
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.animation_cooldown = 100

        self.animations = []
        self.load_images()

        self.play_once = False

    def set_action(self, new_action, play_once=False):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            self.play_once = play_once

    def load_images(self):
        self.animations = [None] * 5

        if self.variant == "bot":
            paths = {
                IDLE: "assets/sprites/Fighter2/Bot-IDLE.png",
                PUNCH: "assets/sprites/Fighter2/Bot-punch.png",
                KICK: "assets/sprites/Fighter2/Bot-kick.png",
                WIN: "assets/sprites/Fighter1/Shinchan-win.png",
                DEAD: "assets/sprites/Fighter2/Bot-over.png",
            }
        else:
            paths = {
                IDLE: "assets/sprites/Fighter1/Shinchan-idle.png",
                PUNCH: "assets/sprites/Fighter1/Shinchan-punch.png",
                KICK: "assets/sprites/Fighter1/Shinchan-kick.png",
                WIN: "assets/sprites/Fighter1/Shinchan-win.png",
                DEAD: "assets/sprites/Fighter1/Shinchan-over.png",
            }

        #IDLE (3 frames)
        self.animations[IDLE] = self.load_idle_sheet(paths[IDLE], frames = 3, scale=(150,220))

        #PUNCH (1)
        punch = pygame.image.load(paths[PUNCH]).convert_alpha()
        punch = pygame.transform.scale(punch, (200, 200))
        self.animations[PUNCH] = [punch]

        #KICK (2)
        kick = pygame.image.load(paths[KICK]).convert_alpha()
        kick = pygame.transform.scale(kick, (200, 200))
        self.animations[KICK] = [kick]


        #WIN (3)
        self.animations[WIN] = self.load_idle_sheet(paths[WIN], frames = 3, scale=(150,220))

        #DEAD (4)
        dead = pygame.image.load(paths[DEAD]).convert_alpha()
        dead = pygame.transform.scale(dead, (260, 260))
        self.animations[DEAD] = [dead]


    def load_idle_sheet(self, path, frames, scale):
        sheet = pygame.image.load(path).convert_alpha()
        frame_width = sheet.get_width()//frames
        frame_height = sheet.get_height()

        animation = []
        for i in range(frames):
            frame = sheet.subsurface(i * frame_width, 0, frame_width, frame_height)
            frame = pygame.transform.scale(frame, scale)
            animation.append(frame)
        return animation
    
    def update_animation(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.update_time > self.animation_cooldown:
            self.update_time = current_time
            self.frame_index += 1

            if self.frame_index >= len(self.animations[self.action]):
                if self.play_once:
                    self.frame_index = len(self.animations[self.action]) - 1
                else:
                    self.frame_index = 0


    def movey(self, actions: Actions):
        if self.action in (DEAD, WIN) or self.health <= 0:
            return
        
            # Apply gravity
        onGround = self.rect.y >= FLOOR_TOP_Y
        if actions.jump and onGround and not self.attacking:
            self.vel_y = JUMP_VELOCITY

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y

        # Prevent falling below the floor
        if self.rect.y > FLOOR_TOP_Y:
            self.rect.y = FLOOR_TOP_Y
            self.vel_y = 0
    

    def movex(self, actions: Actions, target):
        if self.action in (DEAD, WIN):
            return

        prev_x = self.rect.x
        
        self.rect.x += actions.movex * self.speed
        
        # Keep fighter within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 1000:
            self.rect.right = 1000
        
        #detect if on ground
        self_feet_y = self.rect.bottom
        target_feet_y = target.rect.bottom

        FEET_TOLERSNCE = 25

        same_level = abs(self_feet_y - target_feet_y) < FEET_TOLERSNCE
        
        if same_level and self.rect.colliderect(target.rect):
            self.rect.x = prev_x

        # Flip fighter based on movement direction
        self.flip = target.rect.centerx < self.rect.centerx

    def attack(self, surface, target):
        if self.health <= 0 or not self.attacking:
            return
        
        # Define attack hitbox
        hitbox_width = 30
        hitbox_height = 30

        target_left = target.rect.centerx < self.rect.centerx
        hitbox_x = (self.rect.left - hitbox_width) if target_left else (self.rect.right)
        
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

        #knockback effect
            knockback_force = 20
            if self.flip:
                target.rect.x -= knockback_force
            else:
                target.rect.x += knockback_force

            target.vel_y = -5

        #pygame.draw.rect(surface, (0, 255, 0), attacking_rect, 2)

    def handle_attack(self, actions: Actions):
        if self.action in (DEAD, WIN):
            return
        
        if self.health <= 0:
            return
        #if already attacking, count down
        if self.attack_timer > 0:
            self.attack_timer -= 1
        
            if self.attack_timer == 0:
                self.attacking = False
                self.set_action(IDLE)
            return
        
        #start new attack
        if actions.punch:
            self.attack_timer = 5
            self.attacking = True
            self.hit_applied = False
            self.set_action(PUNCH)

        elif actions.kick:
            self.attack_timer = 7
            self.attacking = True
            self.hit_applied = False 
            self.set_action(KICK)


    def draw(self, surface):
        if self.action != DEAD:
            self.update_animation()
        else:
            self.frame_index = 0

        image = self.animations[self.action][self.frame_index]
        if self.flip:
            image = pygame.transform.flip(image, True, False)

        surface.blit(image, self.rect)