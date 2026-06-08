from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time
import sys

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
GRAVITY = 2.5
JUMP_FORCE = 300
PLAYER_SPEED = 20
PLAYER_SIZE = 30
PLATFORM_HEIGHT = 10
PLATFORM_DEPTH = 50
BULLET_SPEED = 120
GRENADE_SPEED = 40
WEAPON_LIFETIME = 30
BLAST_RADIUS = 300
MAX_HEALTH = 100
ENEMY_SPAWN_RATE = 3
ENEMY_SPEED = 10
ENEMY_DAMAGE = 5
ENEMY_JUMP_CHANCE = 0.02
ARENA_WIDTH = 1000
ARENA_HEIGHT = 600

# Game states
MENU = 0
SINGLE_PLAYER = 1
MULTI_PLAYER = 2
GAME_OVER = 3

# Weapon types
NO_WEAPON = 0
SWORD = 1
GUN = 2
GRENADE = 3

class Player:
    def __init__(self, x, y, player_id=1):
        self.x = x
        self.y = y
        self.z = 0
        self.vx = 0
        self.vy = 0
        self.health = MAX_HEALTH
        self.weapon = NO_WEAPON
        self.weapon_time = 0
        self.facing_right = True
        self.player_id = player_id
        self.sword_swinging = False
        self.swing_angle = 0
        self.swing_direction = 1
        self.is_jumping = False
        self.on_ground = False
        self.last_shot = 0
        self.shot_delay = 0.2
        self.color = (0.8, 0.2, 0.2) if player_id == 1 else (0.2, 0.2, 0.8)
        self.hit_effect = 0
    
    def update(self, dt, platforms):
        self.vy -= GRAVITY
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Reduce hit effect over time
        if self.hit_effect > 0:
            self.hit_effect = max(0, self.hit_effect - dt * 5)
        
        self.on_ground = False
        for platform in platforms:
            if (self.x + PLAYER_SIZE/2 > platform.x - platform.width/2 and 
                self.x - PLAYER_SIZE/2 < platform.x + platform.width/2):
                if (self.y - PLAYER_SIZE/2 <= platform.y + PLATFORM_HEIGHT/2 and 
                    self.y - PLAYER_SIZE/2 >= platform.y - PLATFORM_HEIGHT/2 and 
                    self.vy < 0):
                    self.y = platform.y + PLATFORM_HEIGHT/2 + PLAYER_SIZE/2
                    self.vy = 0
                    self.on_ground = True
                    self.is_jumping = False
        
        if self.sword_swinging:
            self.swing_angle += 30 * self.swing_direction  # Increased swing speed
            if abs(self.swing_angle) > 90:
                self.swing_direction *= -1
            if abs(self.swing_angle) < 5 and self.swing_direction == -1:
                self.sword_swinging = False
                self.swing_angle = 0
        
        if self.weapon != NO_WEAPON:
            self.weapon_time += dt
            if self.weapon_time > WEAPON_LIFETIME:
                self.weapon = NO_WEAPON
                self.weapon_time = 0
    
    def jump(self):
        if self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False
            self.is_jumping = True
    
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        self.hit_effect = 1.0  # Trigger hit effect
        return self.health <= 0

    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        # Apply hit effect (red flash)
        if self.hit_effect > 0:
            glColor3f(1.0, 0.5 * self.hit_effect, 0.5 * self.hit_effect)
        else:
            glColor3f(*self.color)
            
        glBegin(GL_QUADS)
        # Front
        glVertex3f(-PLAYER_SIZE/2, -PLAYER_SIZE/2, -PLAYER_SIZE/2)
        glVertex3f(PLAYER_SIZE/2, -PLAYER_SIZE/2, -PLAYER_SIZE/2)
        glVertex3f(PLAYER_SIZE/2, PLAYER_SIZE/2, -PLAYER_SIZE/2)
        glVertex3f(-PLAYER_SIZE/2, PLAYER_SIZE/2, -PLAYER_SIZE/2)
        # Back
        glVertex3f(-PLAYER_SIZE/2, -PLAYER_SIZE/2, PLAYER_SIZE/2)
        glVertex3f(PLAYER_SIZE/2, -PLAYER_SIZE/2, PLAYER_SIZE/2)
        glVertex3f(PLAYER_SIZE/2, PLAYER_SIZE/2, PLAYER_SIZE/2)
        glVertex3f(-PLAYER_SIZE/2, PLAYER_SIZE/2, PLAYER_SIZE/2)
        # Left
        glVertex3f(-PLAYER_SIZE/2, -PLAYER_SIZE/2, -PLAYER_SIZE/2)
        glVertex3f(-PLAYER_SIZE/2, PLAYER_SIZE/2, -PLAYER_SIZE/2)
        glVertex3f(-PLAYER_SIZE/2, PLAYER_SIZE/2, PLAYER_SIZE/2)
        glVertex3f(-PLAYER_SIZE/2, -PLAYER_SIZE/2, PLAYER_SIZE/2)
        # Right
        glVertex3f(PLAYER_SIZE/2, -PLAYER_SIZE/2, -PLAYER_SIZE/2)
        glVertex3f(PLAYER_SIZE/2, PLAYER_SIZE/2, -PLAYER_SIZE/2)
        glVertex3f(PLAYER_SIZE/2, PLAYER_SIZE/2, PLAYER_SIZE/2)
        glVertex3f(PLAYER_SIZE/2, -PLAYER_SIZE/2, PLAYER_SIZE/2)
        # Top
        glVertex3f(-PLAYER_SIZE/2, PLAYER_SIZE/2, -PLAYER_SIZE/2)
        glVertex3f(PLAYER_SIZE/2, PLAYER_SIZE/2, -PLAYER_SIZE/2)
        glVertex3f(PLAYER_SIZE/2, PLAYER_SIZE/2, PLAYER_SIZE/2)
        glVertex3f(-PLAYER_SIZE/2, PLAYER_SIZE/2, PLAYER_SIZE/2)
        # Bottom
        glVertex3f(-PLAYER_SIZE/2, -PLAYER_SIZE/2, -PLAYER_SIZE/2)
        glVertex3f(PLAYER_SIZE/2, -PLAYER_SIZE/2, -PLAYER_SIZE/2)
        glVertex3f(PLAYER_SIZE/2, -PLAYER_SIZE/2, PLAYER_SIZE/2)
        glVertex3f(-PLAYER_SIZE/2, -PLAYER_SIZE/2, PLAYER_SIZE/2)
        glEnd()
        
        # Head
        glColor3f(0.9, 0.7, 0.7)
        glTranslatef(0, PLAYER_SIZE/2 + PLAYER_SIZE/4, 0)
        glutSolidSphere(PLAYER_SIZE/4, 10, 10)
        
        # Weapon
        if self.weapon == SWORD:
            glPushMatrix()
            if self.sword_swinging:
                glRotatef(self.swing_angle if self.facing_right else -self.swing_angle, 0, 0, 1)
            glTranslatef(PLAYER_SIZE/2 if self.facing_right else -PLAYER_SIZE/2, -PLAYER_SIZE/4, 0)
            
            # Sword handle
            glColor3f(0.5, 0.3, 0.1)
            glBegin(GL_QUADS)
            glVertex3f(0, -5, -3)
            glVertex3f(10 if self.facing_right else -10, -5, -3)
            glVertex3f(10 if self.facing_right else -10, 5, -3)
            glVertex3f(0, 5, -3)
            glVertex3f(0, -5, 3)
            glVertex3f(10 if self.facing_right else -10, -5, 3)
            glVertex3f(10 if self.facing_right else -10, 5, 3)
            glVertex3f(0, 5, 3)
            glEnd()
            
            # Sword blade (only when swinging or holding)
            if self.sword_swinging or not self.sword_swinging:
                glColor3f(0.9, 0.9, 0.9)
                glBegin(GL_QUADS)
                glVertex3f(10 if self.facing_right else -10, -3, -2)
                glVertex3f(30 if self.facing_right else -30, -3, -2)
                glVertex3f(30 if self.facing_right else -30, 3, -2)
                glVertex3f(10 if self.facing_right else -10, 3, -2)
                glVertex3f(10 if self.facing_right else -10, -3, 2)
                glVertex3f(30 if self.facing_right else -30, -3, 2)
                glVertex3f(30 if self.facing_right else -30, 3, 2)
                glVertex3f(10 if self.facing_right else -10, 3, 2)
                glEnd()
                
                # Sword tip
                glColor3f(0.8, 0.8, 0.8)
                glBegin(GL_TRIANGLES)
                glVertex3f(30 if self.facing_right else -30, -3, -2)
                glVertex3f(40 if self.facing_right else -40, 0, -2)
                glVertex3f(30 if self.facing_right else -30, 3, -2)
                glVertex3f(30 if self.facing_right else -30, -3, 2)
                glVertex3f(40 if self.facing_right else -40, 0, 2)
                glVertex3f(30 if self.facing_right else -30, 3, 2)
                glEnd()
            glPopMatrix()
        elif self.weapon == GUN:
            glPushMatrix()
            glTranslatef(PLAYER_SIZE/2 if self.facing_right else -PLAYER_SIZE/2, -PLAYER_SIZE/4, 0)
            
            # Gun body
            glColor3f(0.4, 0.4, 0.4)
            glBegin(GL_QUADS)
            # Main body
            glVertex3f(0, -6, -4)
            glVertex3f(20 if self.facing_right else -20, -6, -4)
            glVertex3f(20 if self.facing_right else -20, 6, -4)
            glVertex3f(0, 6, -4)
            glVertex3f(0, -6, 4)
            glVertex3f(20 if self.facing_right else -20, -6, 4)
            glVertex3f(20 if self.facing_right else -20, 6, 4)
            glVertex3f(0, 6, 4)
            
            # Barrel
            glVertex3f(20 if self.facing_right else -20, -4, -3)
            glVertex3f(30 if self.facing_right else -30, -4, -3)
            glVertex3f(30 if self.facing_right else -30, 4, -3)
            glVertex3f(20 if self.facing_right else -20, 4, -3)
            glVertex3f(20 if self.facing_right else -20, -4, 3)
            glVertex3f(30 if self.facing_right else -30, -4, 3)
            glVertex3f(30 if self.facing_right else -30, 4, 3)
            glVertex3f(20 if self.facing_right else -20, 4, 3)
            
            # Grip
            glVertex3f(5 if self.facing_right else -5, -6, -6)
            glVertex3f(15 if self.facing_right else -15, -6, -6)
            glVertex3f(15 if self.facing_right else -15, -2, -6)
            glVertex3f(5 if self.facing_right else -5, -2, -6)
            glVertex3f(5 if self.facing_right else -5, -6, 6)
            glVertex3f(15 if self.facing_right else -15, -6, 6)
            glVertex3f(15 if self.facing_right else -15, -2, 6)
            glVertex3f(5 if self.facing_right else -5, -2, 6)
            glEnd()
            
            # Gun details
            glColor3f(0.2, 0.2, 0.2)
            glBegin(GL_LINES)
            # Sights
            glVertex3f(25 if self.facing_right else -25, 5, 0)
            glVertex3f(25 if self.facing_right else -25, 7, 0)
            glVertex3f(0, 5, 0)
            glVertex3f(0, 7, 0)
            glEnd()
            glPopMatrix()
        elif self.weapon == GRENADE:
            glPushMatrix()
            glTranslatef(PLAYER_SIZE/2 if self.facing_right else -PLAYER_SIZE/2, -PLAYER_SIZE/4, 0)
            glColor3f(0.9, 0.2, 0.2)
            glutSolidSphere(PLAYER_SIZE/4, 10, 10)
            glPopMatrix()
        
        glPopMatrix()

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = random.uniform(-20, 20)
        self.vx = random.choice([-1, 1]) * ENEMY_SPEED
        self.vy = 0
        self.health = 1
        self.size = 25
        self.color = (0.8, 0.8, 0.2)
        self.attack_cooldown = 0
        self.on_ground = False
        self.wing_phase = random.uniform(0, 2*math.pi)
        self.body_angle = 0
        self.eye_offset = random.uniform(0, 2*math.pi)
    
    def update(self, dt, platforms, player):
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            dx /= distance
            dy /= distance
        
        self.vx = dx * ENEMY_SPEED * (0.8 + 0.4 * random.random())
        self.vy = dy * ENEMY_SPEED * 0.5
        self.vy -= GRAVITY * 0.5
        
        if distance < 200 and self.on_ground and random.random() < ENEMY_JUMP_CHANCE:
            self.vy = JUMP_FORCE * 0.7
            self.on_ground = False
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.body_angle += dt * 30
        
        if self.x < -ARENA_WIDTH/2:
            self.x = -ARENA_WIDTH/2
        elif self.x > ARENA_WIDTH/2:
            self.x = ARENA_WIDTH/2
        
        if self.y < -ARENA_HEIGHT/2 + 50:
            self.y = -ARENA_HEIGHT/2 + 50
        elif self.y > ARENA_HEIGHT/2 - 50:
            self.y = ARENA_HEIGHT/2 - 50
        
        self.on_ground = False
        for platform in platforms:
            if (self.x + self.size/2 > platform.x - platform.width/2 and 
                self.x - self.size/2 < platform.x + platform.width/2):
                if (self.y - self.size/2 <= platform.y + PLATFORM_HEIGHT/2 and 
                    self.y - self.size/2 >= platform.y - PLATFORM_HEIGHT/2 and 
                    self.vy < 0):
                    self.y = platform.y + PLATFORM_HEIGHT/2 + self.size/2
                    self.vy = 0
                    self.on_ground = True
        
        if distance < self.size + PLAYER_SIZE:
            if self.attack_cooldown <= 0:
                player.take_damage(ENEMY_DAMAGE)
                self.attack_cooldown = 1.0
            else:
                self.attack_cooldown -= dt
        
        self.wing_phase += dt * 10
        self.eye_offset += dt * 2
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        # Body
        glColor3f(*self.color)
        glRotatef(self.body_angle, 0, 1, 0)
        glutSolidSphere(self.size/2, 10, 10)
        
        # Eyes
        glColor3f(0, 0, 0)
        eye_x = self.size/4 * math.cos(self.eye_offset)
        eye_z = self.size/4 * math.sin(self.eye_offset)
        glPushMatrix()
        glTranslatef(eye_x, 0, eye_z + self.size/4)
        glutSolidSphere(self.size/8, 8, 8)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-eye_x, 0, eye_z + self.size/4)
        glutSolidSphere(self.size/8, 8, 8)
        glPopMatrix()
        
        # Wings
        glColor4f(0.8, 0.8, 1.0, 0.6)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        wing_offset = math.sin(self.wing_phase) * 5
        
        glBegin(GL_TRIANGLES)
        # Left wing
        glVertex3f(0, 0, 0)
        glVertex3f(-self.size, self.size/2 + wing_offset, 5)
        glVertex3f(-self.size, -self.size/2 + wing_offset, 5)
        
        # Right wing
        glVertex3f(0, 0, 0)
        glVertex3f(self.size, self.size/2 + wing_offset, 5)
        glVertex3f(self.size, -self.size/2 + wing_offset, 5)
        glEnd()
        
        glDisable(GL_BLEND)
        
        glPopMatrix()

class Platform:
    def __init__(self, x, y, width):
        self.x = x
        self.y = y
        self.z = 0
        self.width = width
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        glColor3f(0.3, 0.6, 0.3)
        glBegin(GL_QUADS)
        # Top
        glVertex3f(-self.width/2, PLATFORM_HEIGHT/2, -PLATFORM_DEPTH/2)
        glVertex3f(self.width/2, PLATFORM_HEIGHT/2, -PLATFORM_DEPTH/2)
        glVertex3f(self.width/2, PLATFORM_HEIGHT/2, PLATFORM_DEPTH/2)
        glVertex3f(-self.width/2, PLATFORM_HEIGHT/2, PLATFORM_DEPTH/2)
        # Bottom
        glVertex3f(-self.width/2, -PLATFORM_HEIGHT/2, -PLATFORM_DEPTH/2)
        glVertex3f(self.width/2, -PLATFORM_HEIGHT/2, -PLATFORM_DEPTH/2)
        glVertex3f(self.width/2, -PLATFORM_HEIGHT/2, PLATFORM_DEPTH/2)
        glVertex3f(-self.width/2, -PLATFORM_HEIGHT/2, PLATFORM_DEPTH/2)
        # Front
        glVertex3f(-self.width/2, -PLATFORM_HEIGHT/2, PLATFORM_DEPTH/2)
        glVertex3f(self.width/2, -PLATFORM_HEIGHT/2, PLATFORM_DEPTH/2)
        glVertex3f(self.width/2, PLATFORM_HEIGHT/2, PLATFORM_DEPTH/2)
        glVertex3f(-self.width/2, PLATFORM_HEIGHT/2, PLATFORM_DEPTH/2)
        # Back
        glVertex3f(-self.width/2, -PLATFORM_HEIGHT/2, -PLATFORM_DEPTH/2)
        glVertex3f(self.width/2, -PLATFORM_HEIGHT/2, -PLATFORM_DEPTH/2)
        glVertex3f(self.width/2, PLATFORM_HEIGHT/2, -PLATFORM_DEPTH/2)
        glVertex3f(-self.width/2, PLATFORM_HEIGHT/2, -PLATFORM_DEPTH/2)
        # Left
        glVertex3f(-self.width/2, -PLATFORM_HEIGHT/2, -PLATFORM_DEPTH/2)
        glVertex3f(-self.width/2, PLATFORM_HEIGHT/2, -PLATFORM_DEPTH/2)
        glVertex3f(-self.width/2, PLATFORM_HEIGHT/2, PLATFORM_DEPTH/2)
        glVertex3f(-self.width/2, -PLATFORM_HEIGHT/2, PLATFORM_DEPTH/2)
        # Right
        glVertex3f(self.width/2, -PLATFORM_HEIGHT/2, -PLATFORM_DEPTH/2)
        glVertex3f(self.width/2, PLATFORM_HEIGHT/2, -PLATFORM_DEPTH/2)
        glVertex3f(self.width/2, PLATFORM_HEIGHT/2, PLATFORM_DEPTH/2)
        glVertex3f(self.width/2, -PLATFORM_HEIGHT/2, PLATFORM_DEPTH/2)
        glEnd()
        
        glPopMatrix()

class Weapon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = random.uniform(-5, 5)
        self.type = random.choice([SWORD, GUN, GRENADE])
        self.spawn_time = time.time()
        self.pulse = 0
        self.growing = True
        self.rotation = 0
    
    def is_active(self):
        return time.time() - self.spawn_time < WEAPON_LIFETIME
    
    def update(self, dt):
        if self.growing:
            self.pulse += dt * 2
            if self.pulse >= 0.2:
                self.growing = False
        else:
            self.pulse -= dt * 2
            if self.pulse <= 0:
                self.growing = True
        self.rotation += dt * 45
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glScalef(1 + self.pulse, 1 + self.pulse, 1 + self.pulse)
        glRotatef(self.rotation, 0, 1, 0)
        
        if self.type == SWORD:
            #blade
            glColor3f(0.9, 0.9, 0.1)
            glRotatef(45, 0, 0, 1)
            glBegin(GL_QUADS)
            glVertex3f(-20, -5, -2)
            glVertex3f(20, -5, -2)
            glVertex3f(20, 5, -2)
            glVertex3f(-20, 5, -2)
            glVertex3f(-20, -5, 2)
            glVertex3f(20, -5, 2)
            glVertex3f(20, 5, 2)
            glVertex3f(-20, 5, 2)
            glEnd()
            #tip
            glColor3f(0.5, 0.3, 0.1)
            glBegin(GL_QUADS)
            glVertex3f(-10, -7, -3)
            glVertex3f(-5, -7, -3)
            glVertex3f(-5, 7, -3)
            glVertex3f(-10, 7, -3)
            glVertex3f(-10, -7, 3)
            glVertex3f(-5, -7, 3)
            glVertex3f(-5, 7, 3)
            glVertex3f(-10, 7, 3)
            glEnd()
        elif self.type == GUN:
            glColor3f(0.4, 0.4, 0.4)
            glBegin(GL_QUADS)
            # Main body
            glVertex3f(-15, -8, -5)
            glVertex3f(15, -8, -5)
            glVertex3f(15, 8, -5)
            glVertex3f(-15, 8, -5)
            glVertex3f(-15, -8, 5)
            glVertex3f(15, -8, 5)
            glVertex3f(15, 8, 5)
            glVertex3f(-15, 8, 5)
            
            # Barrel
            glVertex3f(15, -4, -3)
            glVertex3f(25, -4, -3)
            glVertex3f(25, 4, -3)
            glVertex3f(15, 4, -3)
            glVertex3f(15, -4, 3)
            glVertex3f(25, -4, 3)
            glVertex3f(25, 4, 3)
            glVertex3f(15, 4, 3)
            
            # Grip
            glVertex3f(-5, -8, -7)
            glVertex3f(5, -8, -7)
            glVertex3f(5, -4, -7)
            glVertex3f(-5, -4, -7)
            glVertex3f(-5, -8, 7)
            glVertex3f(5, -8, 7)
            glVertex3f(5, -4, 7)
            glVertex3f(-5, -4, 7)
            glEnd()
            
            # Details
            glColor3f(0.2, 0.2, 0.2)
            glBegin(GL_LINES)
            # Sights
            glVertex3f(20, 6, 0)
            glVertex3f(20, 8, 0)
            glVertex3f(-5, 6, 0)
            glVertex3f(-5, 8, 0)
            glEnd()
            
        elif self.type == GRENADE:
            glColor3f(0.9, 0.2, 0.2)
            glutSolidSphere(12, 10, 10)
            
            glColor3f(0.8, 0.8, 0.8)
            glBegin(GL_LINES)
            glVertex3f(12, 5, 0)
            glVertex3f(18, 8, 0)
            glEnd()
        
        glPopMatrix()

class Bullet:
    def __init__(self, x, y, direction, owner_id):
        self.x = x
        self.y = y
        self.z = 0
        self.vx = direction * BULLET_SPEED
        self.owner_id = owner_id
        self.lifetime = 2.0
    
    def update(self, dt):
        self.x += self.vx * dt
        self.lifetime -= dt
        return self.lifetime > 0 and -ARENA_WIDTH/2 < self.x < ARENA_WIDTH/2
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glColor3f(1.0, 1.0, 0.0)
        glutSolidSphere(5, 10, 10)
        #tail
        glBegin(GL_LINES)
        glVertex3f(-10 if self.vx > 0 else 10, 0, 0)
        glVertex3f(0, 0, 0)
        glEnd()
        
        glPopMatrix()

class Grenade:
    def __init__(self, x, y, direction, owner_id):
        self.x = x
        self.y = y
        self.z = 0
        self.vx = direction * GRENADE_SPEED
        self.vy = 15
        self.owner_id = owner_id
        self.timer = 2.0
        self.exploded = False
        self.rotation = 0
    
    def update(self, dt, platforms):
        if self.exploded:
            return False
        
        self.timer -= dt
        self.rotation += dt * 360
        
        if self.timer <= 0:
            self.exploded = True
            return True
        
        self.vy -= GRAVITY * 2
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        for platform in platforms:
            if (self.x > platform.x - platform.width/2 and 
                self.x < platform.x + platform.width/2 and
                self.y - 8 <= platform.y + PLATFORM_HEIGHT/2 and 
                self.y - 8 >= platform.y - PLATFORM_HEIGHT/2 and 
                self.vy < 0):
                self.y = platform.y + PLATFORM_HEIGHT/2 + 8
                self.vy *= -0.6
                self.vx *= 0.8
        
        return -ARENA_WIDTH/2 < self.x < ARENA_WIDTH/2
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.rotation, 0, 0, 1)
        glColor3f(0.9, 0.2, 0.2)
        
        glutSolidSphere(8, 10, 10)
        
        glColor3f(0.7, 0.1, 0.1)
        #decorative lines
        for i in range(5):
            glBegin(GL_LINES)
            glVertex3f(8 * math.cos(i * math.pi/2.5), 8 * math.sin(i * math.pi/2.5), 0)
            glVertex3f(8 * math.cos((i+0.5) * math.pi/2.5), 8 * math.sin((i+0.5) * math.pi/2.5), 0)
            glEnd()
        #spark effect
        if self.timer < 0.5:
            glColor3f(1.0, 0.5, 0.0)
            glBegin(GL_LINES)
            glVertex3f(0, 8, 0)
            glVertex3f(random.uniform(-5, 5), random.uniform(8, 12), 0)
            glEnd()
        
        glPopMatrix()

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = 0
        self.radius = 5
        self.max_radius = BLAST_RADIUS
        self.growth_rate = 40  # Increased growth rate for faster explosion
        self.active = True
    
    def update(self, dt):
        self.radius += self.growth_rate * dt
        if self.radius >= self.max_radius:
            self.active = False
        return self.active
    
    def draw(self):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        # Main explosion sphere
        glColor4f(1.0, 0.5, 0.0, 0.7 * (1.0 - self.radius/self.max_radius))
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glutSolidSphere(self.radius, 20, 20)
        
        # Inner core
        glColor4f(1.0, 0.8, 0.0, 0.5 * (1.0 - self.radius/self.max_radius))
        glutSolidSphere(self.radius * 0.7, 20, 20)
        
        # Bright center
        glColor4f(1.0, 1.0, 0.0, 0.3 * (1.0 - self.radius/self.max_radius))
        glutSolidSphere(self.radius * 0.4, 20, 20)
        
        # Shockwave ring
        if self.radius > self.max_radius * 0.7:
            glColor4f(1.0, 1.0, 1.0, 0.2 * (1.0 - self.radius/self.max_radius))
            glutWireSphere(self.radius * 1.1, 16, 16)
        
        glDisable(GL_BLEND)
        glPopMatrix()

class Game:
    def __init__(self):
        self.game_state = MENU
        self.score = [0, 0]
        self.game_time = 0
        self.last_weapon_spawn = 0
        self.last_enemy_spawn = 0
        self.players = []
        self.enemies = []
        self.platforms = []
        self.weapons = []
        self.bullets = []
        self.grenades = []
        self.explosions = []
        self.camera_x = 0
        self.camera_y = 0
        self.setup_arena()
    
    def setup_arena(self):
        self.players = []
        self.enemies = []
        self.platforms = []
        self.weapons = []
        self.bullets = []
        self.grenades = []
        self.explosions = []
        
        ground_width = ARENA_WIDTH * 1.5
        self.platforms.append(Platform(0, -ARENA_HEIGHT/2 + 50, ground_width))
        
        platform_positions = [
            (-300, -100), (300, -100),
            (-400, 50), (400, 50),
            (0, 200), (-200, 200), (200, 200)
        ]
        
        for x, y in platform_positions:
            self.platforms.append(Platform(x, y, 200))
        
        self.players = [
            Player(-200, -ARENA_HEIGHT/2 + 100, 1)
        ]
        
        if self.game_state == MULTI_PLAYER:
            self.players.append(Player(200, -ARENA_HEIGHT/2 + 100, 2))
    
    def spawn_weapon(self):
        if time.time() - self.last_weapon_spawn > 5 and len(self.weapons) < 3:
            x = random.uniform(-ARENA_WIDTH/2 + 50, ARENA_WIDTH/2 - 50)
            y = random.uniform(-ARENA_HEIGHT/2 + 100, ARENA_HEIGHT/2 - 100)
            self.weapons.append(Weapon(x, y))
            self.last_weapon_spawn = time.time()
    
    def spawn_enemy(self):
        if self.game_state == SINGLE_PLAYER and time.time() - self.last_enemy_spawn > ENEMY_SPAWN_RATE:
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'left':
                x = -ARENA_WIDTH/2 - 50
                y = random.uniform(-ARENA_HEIGHT/2 + 100, ARENA_HEIGHT/2 - 100)
            elif side == 'right':
                x = ARENA_WIDTH/2 + 50
                y = random.uniform(-ARENA_HEIGHT/2 + 100, ARENA_HEIGHT/2 - 100)
            elif side == 'top':
                x = random.uniform(-ARENA_WIDTH/2 + 50, ARENA_WIDTH/2 - 50)
                y = ARENA_HEIGHT/2 + 50
            else:
                x = random.uniform(-ARENA_WIDTH/2 + 50, ARENA_WIDTH/2 - 50)
                y = -ARENA_HEIGHT/2 - 50
                
            self.enemies.append(Enemy(x, y))
            self.last_enemy_spawn = time.time()
    
    def check_collisions(self):
        for weapon in self.weapons[:]:
            weapon.update(1/60.0)
            if not weapon.is_active():
                self.weapons.remove(weapon)
                continue
                
            for player in self.players:
                dist = math.sqrt((player.x - weapon.x)**2 + (player.y - weapon.y)**2)
                if dist < PLAYER_SIZE and player.weapon == NO_WEAPON:
                    player.weapon = weapon.type
                    player.weapon_time = 0
                    self.weapons.remove(weapon)
                    break
        
        for player in self.players:
            if player.sword_swinging:
                for other in self.players:
                    if other != player:
                        dist = math.sqrt((player.x - other.x)**2 + (player.y - other.y)**2)
                        if dist < PLAYER_SIZE * 1.5 and abs(player.swing_angle) > 45:
                            if other.take_damage(5):
                                if self.game_state == SINGLE_PLAYER:
                                    self.score[0] += 10
                
                for enemy in self.enemies[:]:
                    dist = math.sqrt((player.x - enemy.x)**2 + (player.y - enemy.y)**2)
                    if dist < PLAYER_SIZE * 1.5 + enemy.size/2 and abs(player.swing_angle) > 45:
                        self.enemies.remove(enemy)
                        self.score[0] += 5
        
        for bullet in self.bullets[:]:
            if not bullet.update(1/60.0):
                self.bullets.remove(bullet)
                continue
                
            for player in self.players:
                if player.player_id != bullet.owner_id:
                    dist = math.sqrt((bullet.x - player.x)**2 + (bullet.y - player.y)**2)
                    if dist < PLAYER_SIZE:
                        if player.take_damage(5):
                            if self.game_state == SINGLE_PLAYER:
                                self.score[0] += 10
                        self.bullets.remove(bullet)
                        break
            
            if self.game_state == SINGLE_PLAYER:
                for enemy in self.enemies[:]:
                    dist = math.sqrt((bullet.x - enemy.x)**2 + (bullet.y - enemy.y)**2)
                    if dist < enemy.size/2 + 5:
                        self.enemies.remove(enemy)
                        self.score[0] += 5
                        self.bullets.remove(bullet)
                        break
        
        for grenade in self.grenades[:]:
            if not grenade.update(1/60.0, self.platforms):
                self.grenades.remove(grenade)
                continue
                
            if grenade.exploded:
                explosion = Explosion(grenade.x, grenade.y)
                self.explosions.append(explosion)
                
                # Check for hits immediately when explosion starts
                for player in self.players:
                    if player.player_id != grenade.owner_id:
                        dist = math.sqrt((grenade.x - player.x)**2 + (grenade.y - player.y)**2)
                        if dist < BLAST_RADIUS:
                            damage = int(25 * (1 - dist/BLAST_RADIUS))
                            if player.take_damage(damage):
                                if self.game_state == SINGLE_PLAYER:
                                    self.score[0] += 10
                
                if self.game_state == SINGLE_PLAYER:
                    for enemy in self.enemies[:]:
                        dist = math.sqrt((grenade.x - enemy.x)**2 + (grenade.y - enemy.y)**2)
                        if dist < BLAST_RADIUS:
                            self.enemies.remove(enemy)
                            self.score[0] += 10
                
                self.grenades.remove(grenade)
        
        for explosion in self.explosions[:]:
            if not explosion.update(1/60.0):
                self.explosions.remove(explosion)
                continue
    
    def update(self, dt):
            if self.game_state in [SINGLE_PLAYER, MULTI_PLAYER]:
                self.game_time += dt
                
                for player in self.players:
                    player.update(dt, self.platforms)
                
                if self.game_state == SINGLE_PLAYER:
                    self.spawn_enemy()
                    for enemy in self.enemies[:]:
                        enemy.update(dt, self.platforms, self.players[0])
                
                if random.random() < 0.01:
                    self.spawn_weapon()
                
                self.check_collisions()
                
                # Check for game over conditions
                if self.game_state == MULTI_PLAYER:
                    alive_players = [p for p in self.players if p.health > 0]
                    if len(alive_players) < 2:  # Game over
                        self.game_state = GAME_OVER
                        print(self.game_state)
                        if len(alive_players) == 1:
                            self.winner = alive_players[0].player_id
                            print("winner",self.winner)
                        else:
                            self.winner = 0  # Draw
                elif self.game_state == SINGLE_PLAYER and self.players[0].health <= 0:
                    self.game_state = GAME_OVER
                    self.winner = None  # No winner in single player
                
                # Update camera
                if self.players:
                    avg_x = sum(p.x for p in self.players) / len(self.players)
                    avg_y = sum(p.y for p in self.players) / len(self.players)
                    self.camera_x += (avg_x - self.camera_x) * dt * 2
                    self.camera_y += (avg_y - self.camera_y) * dt * 2
            
            
    def draw(self):
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45, SCREEN_WIDTH/SCREEN_HEIGHT, 0.1, 5000)
            
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            # Camera follows players with slight delay
            gluLookAt(
                self.camera_x, self.camera_y - 200, 800,
                self.camera_x, self.camera_y, 0,
                0, 1, 0
            )
            
            glEnable(GL_DEPTH_TEST)
            
            # Draw background (all blue)
            glBegin(GL_QUADS)
            glColor3f(0.1, 0.1, 0.5)  # Dark blue
            glVertex3f(-5000, -5000, -1000)
            glVertex3f(5000, -5000, -1000)
            glVertex3f(5000, 5000, -1000)
            glVertex3f(-5000, 5000, -1000)
            glEnd()
            
            if self.game_state == MENU:
                self.draw_menu()
            elif self.game_state == GAME_OVER:
                self.draw_game_over()
            else:
                for platform in self.platforms:
                    platform.draw()
                
                for weapon in self.weapons:
                    weapon.draw()
                
                for bullet in self.bullets:
                    bullet.draw()
                
                for grenade in self.grenades:
                    grenade.draw()
                
                for explosion in self.explosions:
                    explosion.draw()
                
                for enemy in self.enemies:
                    enemy.draw()
                
                for player in self.players:
                    player.draw()
                
                self.draw_hud()
            
            glutSwapBuffers()
        
    def draw_hud(self):
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            glDisable(GL_DEPTH_TEST)
            
            if self.game_state == SINGLE_PLAYER:
                glColor3f(1, 1, 1)
                self.draw_text(20, SCREEN_HEIGHT - 30, f"Score: {self.score[0]}")
            
            if len(self.players) > 0 and self.players[0].health > 0:
                weapon_text = "Weapon: "
                if self.players[0].weapon == NO_WEAPON:
                    weapon_text += "None"
                elif self.players[0].weapon == SWORD:
                    weapon_text += "Sword"
                elif self.players[0].weapon == GUN:
                    weapon_text += "Gun"
                elif self.players[0].weapon == GRENADE:
                    weapon_text += "Grenade"
                
                if self.players[0].weapon != NO_WEAPON:
                    weapon_text += f" ({WEAPON_LIFETIME - int(self.players[0].weapon_time)}s)"
                
                # Add health percentage below weapon info
                health_text = f"Health: {int(self.players[0].health)}%"
                self.draw_text(20, SCREEN_HEIGHT - 90, weapon_text)
                self.draw_text(20, SCREEN_HEIGHT - 120, health_text)
            
            if len(self.players) > 1 and self.players[1].health > 0:
                weapon_text = "Weapon: "
                if self.players[1].weapon == NO_WEAPON:
                    weapon_text += "None"
                elif self.players[1].weapon == SWORD:
                    weapon_text += "Sword"
                elif self.players[1].weapon == GUN:
                    weapon_text += "Gun"
                elif self.players[1].weapon == GRENADE:
                    weapon_text += "Grenade"
                
                if self.players[1].weapon != NO_WEAPON:
                    weapon_text += f" ({WEAPON_LIFETIME - int(self.players[1].weapon_time)}s)"
                
                # Add health percentage below weapon info
                health_text = f"Health: {int(self.players[1].health)}%"
                text_width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in weapon_text)
                self.draw_text(SCREEN_WIDTH - 20 - text_width, SCREEN_HEIGHT - 90, weapon_text)
                self.draw_text(SCREEN_WIDTH - 20 - text_width, SCREEN_HEIGHT - 120, health_text)
            
            self.draw_text(SCREEN_WIDTH/2 - 50, SCREEN_HEIGHT - 30, f"Time: {int(self.game_time)}s")
            
            if self.game_state == SINGLE_PLAYER:
                self.draw_text(20, 30, "WASD: Move | SPACE: Attack | R: Restart")
            else:
                self.draw_text(20, 30, "Player1: WASD | Player2: Arrows | SPACE/CTRL: Attack | R: Restart")
            
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            
            glEnable(GL_DEPTH_TEST)
        
    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):
            glRasterPos2f(x, y)
            for character in text:
                glutBitmapCharacter(font, ord(character))
        
    def draw_menu(self):
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            glDisable(GL_DEPTH_TEST)
            
            text = "B0T BRAWL"
            width = sum(glutBitmapWidth(GLUT_BITMAP_TIMES_ROMAN_24, ord(c)) for c in text)
            self.draw_text(SCREEN_WIDTH/2 - width/2, SCREEN_HEIGHT/2 + 150, text, GLUT_BITMAP_TIMES_ROMAN_24)
            
            glColor4f(0.2, 0.2, 0.3, 0.7)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glBegin(GL_QUADS)
            glVertex2f(SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT/2 + 70)
            glVertex2f(SCREEN_WIDTH/2 + 150, SCREEN_HEIGHT/2 + 70)
            glVertex2f(SCREEN_WIDTH/2 + 150, SCREEN_HEIGHT/2 - 100)
            glVertex2f(SCREEN_WIDTH/2 - 150, SCREEN_HEIGHT/2 - 100)
            glEnd()
            glDisable(GL_BLEND)
            
            glColor3f(1, 1, 1)
            self.draw_text(SCREEN_WIDTH/2 - 120, SCREEN_HEIGHT/2 + 40, "1. Single Player Mode")
            self.draw_text(SCREEN_WIDTH/2 - 120, SCREEN_HEIGHT/2, "2. Multiplayer Mode")
            self.draw_text(SCREEN_WIDTH/2 - 120, SCREEN_HEIGHT/2 - 40, "ESC - Quit Game")
            
            glColor3f(0.8, 0.8, 0.8)
            self.draw_text(SCREEN_WIDTH/2 - 300, SCREEN_HEIGHT/2 - 150, "Collect weapons (sword, gun, grenade) to fight enemies")
            self.draw_text(SCREEN_WIDTH/2 - 300, SCREEN_HEIGHT/2 - 180, "Survive as long as possible in single player mode")
            self.draw_text(SCREEN_WIDTH/2 - 300, SCREEN_HEIGHT/2 - 210, "Defeat your opponent in multiplayer mode")
            
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            
            glEnable(GL_DEPTH_TEST)
        
    def draw_game_over(self):
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            gluOrtho2D(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            glDisable(GL_DEPTH_TEST)
            
            # Dark overlay
            glColor4f(0.1, 0.1, 0.2, 0.8)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glBegin(GL_QUADS)
            glVertex2f(0, 0)
            glVertex2f(SCREEN_WIDTH, 0)
            glVertex2f(SCREEN_WIDTH, SCREEN_HEIGHT)
            glVertex2f(0, SCREEN_HEIGHT)
            glEnd()
            glDisable(GL_BLEND)
            
            # "GAME OVER" text
            text = "GAME OVER"
            width = sum(glutBitmapWidth(GLUT_BITMAP_TIMES_ROMAN_24, ord(c)) for c in text)
            glColor3f(1, 0.2, 0.2)
            self.draw_text(SCREEN_WIDTH/2 - width/2, SCREEN_HEIGHT/2 + 100, text, GLUT_BITMAP_TIMES_ROMAN_24)
            
            # Winner/Score text
            if self.winner:
                print("game_over_window",self.game_state)
                if hasattr(self, 'winner'):
                    if self.winner == 1:
                        text = "Player 1 Wins!"
                        color = (1.0, 0.2, 0.2)  # Red
                    elif self.winner == 2:
                        text = "Player 2 Wins!"
                        color = (0.2, 0.2, 1.0)  # Blue
                    elif self.winner == 0:
                        text = "Draw! Both players died!"
                        color = (1.0, 1.0, 1.0)  # White
                else:
                    text = "Game Over!"
                    color = (1.0, 1.0, 1.0)
            else:  # Single player
                text = f"Score: {self.score[0]}"
                color = (1.0, 1.0, 1.0)
            
            width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in text)
            glColor3f(*color)
            self.draw_text(SCREEN_WIDTH/2 - width/2, SCREEN_HEIGHT/2 + 40, text)
            
            # Rest of the game over text
            glColor3f(1, 1, 1)
            text = "Press R to return to menu"
            width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in text)
            self.draw_text(SCREEN_WIDTH/2 - width/2, SCREEN_HEIGHT/2 - 20, text)
            
            text = "Press ESC to quit"
            width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in text)
            self.draw_text(SCREEN_WIDTH/2 - width/2, SCREEN_HEIGHT/2 - 60, text)
            
            text = f"Time survived: {int(self.game_time)} seconds"
            width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in text)
            self.draw_text(SCREEN_WIDTH/2 - width/2, SCREEN_HEIGHT/2 - 100, text)
            
            if self.game_state == SINGLE_PLAYER:
                text = f"Enemies defeated: {self.score[0]//5}"
                width = sum(glutBitmapWidth(GLUT_BITMAP_HELVETICA_18, ord(c)) for c in text)
                self.draw_text(SCREEN_WIDTH/2 - width/2, SCREEN_HEIGHT/2 - 140, text)
            
            glPopMatrix()
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            
            glEnable(GL_DEPTH_TEST)

    def reset_game(self):
            self.score = [0, 0]
            self.game_time = 0
            self.last_weapon_spawn = 0
            self.last_enemy_spawn = 0
            self.camera_x = 0
            self.camera_y = 0
            self.winner = None  # Reset winner
            self.setup_arena()

game = Game()

def keyboard(key, x, y):
    key = key.decode('utf-8').lower()
    
    if game.game_state == MENU:
        if key == '1':
            game.game_state = SINGLE_PLAYER
            game.reset_game()
        elif key == '2':
            game.game_state = MULTI_PLAYER
            game.reset_game()
        elif key == '\x1b':
            glutLeaveMainLoop()
    
    elif game.game_state in [SINGLE_PLAYER, MULTI_PLAYER]:
        player = game.players[0]
        
        if key == 'a':
            player.vx = -PLAYER_SPEED
            player.facing_right = False
        elif key == 'd':
            player.vx = PLAYER_SPEED
            player.facing_right = True
        elif key == 'w':
            player.jump()
        elif key == ' ':
            if player.weapon == SWORD and not player.sword_swinging:
                player.sword_swinging = True
                player.swing_angle = 0
                player.swing_direction = 1
            elif player.weapon == GUN and time.time() - player.last_shot > player.shot_delay:
                direction = 1 if player.facing_right else -1
                game.bullets.append(Bullet(
                    player.x + direction * PLAYER_SIZE/2,
                    player.y,
                    direction,
                    player.player_id
                ))
                player.last_shot = time.time()
            elif player.weapon == GRENADE:
                direction = 1 if player.facing_right else -1
                game.grenades.append(Grenade(
                    player.x + direction * PLAYER_SIZE/2,
                    player.y,
                    direction,
                    player.player_id
                ))
                player.weapon = NO_WEAPON
                player.weapon_time = 0
        elif key == 'r':
            game.reset_game()
        elif key == '\x1b':
            game.game_state = MENU
    
    elif game.game_state == GAME_OVER:
        if key == 'r':
            game.game_state = MENU
            game.reset_game()
        elif key == '\x1b':
            glutLeaveMainLoop()

def keyboard_up(key, x, y):
    key = key.decode('utf-8').lower()
    if game.game_state in [SINGLE_PLAYER, MULTI_PLAYER]:
        player = game.players[0]
        if key == 'a' and player.vx < 0:
            player.vx = 0
        elif key == 'd' and player.vx > 0:
            player.vx = 0

def special_key(key, x, y):
    if game.game_state == MULTI_PLAYER and len(game.players) > 1:
        player = game.players[1]
        
        if key == GLUT_KEY_LEFT:
            player.vx = -PLAYER_SPEED
            player.facing_right = False
        elif key == GLUT_KEY_RIGHT:
            player.vx = PLAYER_SPEED
            player.facing_right = True
        elif key == GLUT_KEY_UP:
            player.jump()
        elif key == GLUT_KEY_DOWN:
            if player.weapon == SWORD and not player.sword_swinging:
                player.sword_swinging = True
                player.swing_angle = 0
                player.swing_direction = 1
            elif player.weapon == GUN and time.time() - player.last_shot > player.shot_delay:
                direction = 1 if player.facing_right else -1
                game.bullets.append(Bullet(
                    player.x + direction * PLAYER_SIZE/2,
                    player.y,
                    direction,
                    player.player_id
                ))
                player.last_shot = time.time()
            elif player.weapon == GRENADE:
                direction = 1 if player.facing_right else -1
                game.grenades.append(Grenade(
                    player.x + direction * PLAYER_SIZE/2,
                    player.y,
                    direction,
                    player.player_id
                ))
                player.weapon = NO_WEAPON
                player.weapon_time = 0

def special_key_up(key, x, y):
    if game.game_state == MULTI_PLAYER and len(game.players) > 1:
        player = game.players[1]
        if key == GLUT_KEY_LEFT and player.vx < 0:
            player.vx = 0
        elif key == GLUT_KEY_RIGHT and player.vx > 0:
            player.vx = 0

def mouse(button, state, x, y):
    if game.game_state in [SINGLE_PLAYER, MULTI_PLAYER]:
        player = game.players[0]
        if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
            if player.weapon == SWORD and not player.sword_swinging:
                player.sword_swinging = True
                player.swing_angle = 0
                player.swing_direction = 1
            elif player.weapon == GUN and time.time() - player.last_shot > player.shot_delay:
                direction = 1 if player.facing_right else -1
                game.bullets.append(Bullet(
                    player.x + direction * PLAYER_SIZE/2,
                    player.y,
                    direction,
                    player.player_id
                ))
                player.last_shot = time.time()
            elif player.weapon == GRENADE:
                direction = 1 if player.facing_right else -1
                game.grenades.append(Grenade(
                    player.x + direction * PLAYER_SIZE/2,
                    player.y,
                    direction,
                    player.player_id
                ))
                player.weapon = NO_WEAPON
                player.weapon_time = 0

def idle():
    game.update(1/60.0)
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(SCREEN_WIDTH, SCREEN_HEIGHT)
    glutCreateWindow(b"Bot Brawl 3D")
    
    glutDisplayFunc(game.draw)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyboard_up)
    glutSpecialFunc(special_key)
    glutSpecialUpFunc(special_key_up)
    glutMouseFunc(mouse)
    glutIdleFunc(idle)
    
    glClearColor(0.1, 0.1, 0.5, 1.0)  # Dark blue background
    
    glutMainLoop()

if __name__ == "__main__":
    main()