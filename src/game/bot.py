import random
import time

from fighters import IDLE, PUNCH, KICK, Fighter
from actions import Actions

class FighterAI(Fighter):
    def __init__(self, x, y):
        super().__init__(x,y, variant="bot")
        self.last_move_time = time.time()
        self.last_attack_time = time.time()
        self.attack_cooldown = 0
        self.attack_delay = 0

    def getActions(self, target: Fighter) -> Actions:
        actions = Actions()
        distance = target.rect.centerx - self.rect.centerx
        d = abs(distance)

        if self.attacking or self.attack_timer > 0:
            actions.movex = 0
        else:
            desired = 170
            tooClose = 120
            if d > desired:
                actions.movex = 1 if distance > 0 else -1
            elif d < tooClose:
                actions.movex = -1 if distance > 0 else 1
            else:
                actions.movex = 0
        
        attackRange = 180
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.attack_delay > 0:
            self.attack_delay -= 1
            if self.attack_delay == 0:
                if random.random() < 0.5:
                    actions.punch = True
                    print("BOT PUNCH!")
                else:
                    actions.kick = True
                    print("BOT KICK!")
                actions.movex = 0

        if d < attackRange and self.attack_cooldown == 0 and not self.attacking and self.attack_delay == 0:
            if random.random() < 0.15:  
                self.attack_delay = 5 
                self.attack_cooldown = 60 
                print(f"BOT queuing attack! Distance: {d}")
        
        return actions


    def random_movement(self):
        if time.time() - self.last_move_time > random.uniform(0.5, 1.5):
            direction = random.choice([-1, 1]) #`-1 for left, 1 for right
            self.rect.x += direction * self.speed
            self.last_move_time = time.time()

    def random_attack(self):
        if time.time() - self.last_attack_time > random.uniform(1.5, 3):
            attack_type = random.choice([PUNCH, KICK, IDLE])
            self.set_action(attack_type)
            self.attack_timer = random.randint(10, 20)
            self.attacking = True
            self.last_attack_time = time.time()

    def move_towards_target(self, target: Fighter):
        if target.rect.centerx < self.rect.centerx:
            self.rect.x -= self.speed
        elif target.rect.centerx > self.rect.centerx:
            self.rect.x += self.speed

    def smart_attack(self, target: Fighter):
        if abs(self.rect.centerx - target.rect.centerx) < 150:
            attack_type = random.choice([PUNCH, KICK])
            self.set_action(attack_type)
            self.attack_timer = random.randint(10, 20)
            self.attacking = True

    def update(self, target: Fighter):
        self.random_movement()
        self.random_attack()
        self.move_towards_target(target)
        self.smart_attack(target)
