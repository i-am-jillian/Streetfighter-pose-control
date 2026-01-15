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

        self.move_timer = 0
        self.current_move = 0
        self.jump_cooldown = 0
        self.last_jump_time = 0

        self.start_time = time.time()
        self.grace_period = 25.0
        
    def getActions(self, target: Fighter) -> Actions:
        actions = Actions()
        distance = target.rect.centerx - self.rect.centerx
        d = abs(distance)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        
        if self.move_timer > 0:
            self.move_timer -= 1

        grace_period_active = (time.time() - self.start_time) < self.grace_period

        if self.jump_cooldown == 0 and not self.attacking and random.random() < 0.002:
            actions.jump = True
            self.jump_cooldown = 60 

        #random jumping
        if self.jump_cooldown == 0 and not self.attacking and random.random() < 0.02:
            actions.jump = True
            self.jump_cooldown = 60 

        if self.attacking or self.attack_timer > 0:
            actions.movex = 0
        else:
            if self.move_timer > 0:
                actions.movex = self.current_move
            else:
                desired = 140
                tooClose = 50


                if d > desired:
                    direction = 1 if distance > 0 else -1
                    
                    if random.random() < 0.3:
                        self.current_move = direction
                        self.move_timer = random.randint(10, 25) 
                    else:
                        actions.movex = direction
                    
                elif d < tooClose:
                    direction = -1 if distance > 0 else 1
                    
                    if random.random() < 0.4:
                        self.current_move = direction
                        self.move_timer = random.randint(15, 30)
                    else:
                        actions.movex = direction
                
                else:
                    if random.random() < 0.05:
                        self.current_move = random.choice([-1, 1])
                        self.move_timer = random.randint(8, 15)
                    else:
                        actions.movex = 0


        attackRange = 180

        if not grace_period_active and d < attackRange and self.attack_cooldown == 0 and not self.attacking:
            attack_chance = 0.75 if d < 100 else 0.35
            if random.random() < attack_chance:  
                if random.random() < 0.60:
                    actions.punch = True
                else:
                    actions.kick = True
                
                self.attack_cooldown = 35
                actions.movex = 0
        
        return actions


   
