import pygame
import time
from math import sqrt
import pathlib
resources_path = pathlib.Path().cwd() / 'resources'

# Classes 
class player_sprite(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()
        # Images
        scale = 0.65
        stand1 = pygame.image.load(resources_path / 'player/stand1.png')
        stand1 = pygame.transform.scale_by(stand1, scale)
        walk1 = pygame.image.load(resources_path / 'player/walk1.png')
        walk1 = pygame.transform.scale_by(walk1, scale)
        walk2 = pygame.image.load(resources_path / 'player/walk2.png')
        walk2 = pygame.transform.scale_by(walk2, scale)
        # Frames Setup
        self.player_frames = [stand1, walk1, walk2]
        self.player_index = 0
        self.lookn_right, self.lookn_left = True, False
        # Image and Rect
        self.image = self.player_frames[self.player_index]
        self.rect = self.image.get_rect()
        self.rect.center = (l//2,w//2)
        # Movement Vars
        self.accelerate = False
        self.last_dashed = time.perf_counter()
        self.dash_count = 0
    
    def move(self):
        move_speed = 8.5
        keys = pygame.key.get_pressed()
        # Bools
        any_wasd = keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]
        opposites_wasd = (keys[pygame.K_a] and keys[pygame.K_d]) or (keys[pygame.K_w] and keys[pygame.K_s])
        diagonals_wasd = (keys[pygame.K_w] and keys[pygame.K_d]) or (keys[pygame.K_w] and keys[pygame.K_a]) or (keys[pygame.K_s] and keys[pygame.K_d]) or (keys[pygame.K_s] and keys[pygame.K_a])

        # Speed Adjustment for Diagonal Movement
        if diagonals_wasd:
            move_speed = move_speed/sqrt(2)

        # Dash
        if any_wasd and keys[pygame.K_l] and (time.perf_counter() - self.last_dashed > 1) and dash_bar.hud_index < 3:
            self.accelerate = True
            self.last_dashed = time.perf_counter()
            self.dash_count += 1
            dash_bar.animation()
        if self.accelerate:
            t = (time.perf_counter() - self.last_dashed)
            acc_factor = (-1600/9)*((t-0.15)**2) + 5
            if t < 0.3:
                move_speed = move_speed*acc_factor
            else:    
                self.accelerate = False
                move_speed = move_speed
            
        # UP-LEFT-RIGHT-DOWN MOVEMENT
        if keys[pygame.K_w] and (not r1.top_collision):
            self.rect.y -= move_speed
        if keys[pygame.K_s] and (not r1.bottom_collision):
            self.rect.y += move_speed
        if keys[pygame.K_a] and (not r1.left_collision):
            self.rect.x -= move_speed
            # Orientation
            if self.lookn_right:
                for frame in self.player_frames:
                    self.player_frames[self.player_frames.index(frame)] = pygame.transform.flip(frame, 1, 0)
                self.lookn_right = False
                self.lookn_left = True
        if keys[pygame.K_d] and (not r1.right_collision):
            self.rect.x += move_speed
            # Orientation
            if self.lookn_left:
                for frame in self.player_frames:
                    self.player_frames[self.player_frames.index(frame)] = pygame.transform.flip(frame, 1, 0)
                self.lookn_left = False
                self.lookn_right = True
        
        # Animation
        if any_wasd and (not opposites_wasd):
            self.animation() 
        else:
            self.image = self.player_frames[0]
    
    def animation(self):
        player_fps = 0.13
        self.player_index = (self.player_index + player_fps) % (len(self.player_frames))
        self.image = self.player_frames[int(self.player_index)]

    def update(self):
        self.move()

class ball_projectile(pygame.sprite.Sprite):

    def __init__(self, x, y, radius, speed):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = radius
        self.image = pygame.Surface((radius*2,radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, "#9C0B0B", (radius, radius), self.radius)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.mx = 1
        self.my = 1
        self.speed = speed

    def move(self):
        # Move
        if self.rect.right >= l:
            self.mx = -1
        if self.rect.left <= 0:
            self.mx = 1
        if self.rect.bottom >= w:
            self.my = -1
        if self.rect.top <= 0:
            self.my = 1
        self.rect.x += self.mx*self.speed
        self.rect.y += self. my*self.speed

    def update(self):
        self.move()

class hud_element(pygame.sprite.Sprite):
    
    def __init__(self, type, x, y):
        super().__init__()
        if type == 'dash_bar':
            dash_bar1 = pygame.image.load(resources_path / 'hud/dash_bar1.png')
            dash_bar2 = pygame.image.load(resources_path / 'hud/dash_bar2.png')
            dash_bar3 = pygame.image.load(resources_path / 'hud/dash_bar3.png')
            dash_bar4 = pygame.image.load(resources_path / 'hud/dash_bar4.png')
            self.hud_element_frames = [dash_bar1, dash_bar2, dash_bar3, dash_bar4]

        self.hud_index = 0
        self.image = self.hud_element_frames[self.hud_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.previous_replenish = time.perf_counter()
        self.begin_replenish = False

    def animation(self):
        self.hud_index += 1
        self.image = self.hud_element_frames[self.hud_index]
    
    def replenish(self):
        if self.hud_index > 0 and not self.begin_replenish:
            self.begin_replenish = True
            self.previous_replenish = time.perf_counter()
        if self.hud_index == 0:
            self.begin_replenish = False

        if (time.perf_counter() - self.previous_replenish > 10) and self.begin_replenish:
            self.hud_index -= 1
            self.image = self.hud_element_frames[self.hud_index]
            self.previous_replenish = time.perf_counter()

    def update(self):
        self.replenish()

class room():

    def __init__(self, door_coords_list, bg_name):
        
        self.image = pygame.image.load(resources_path / f'bg/{bg_name}.png')
        self.rect = self.image.get_rect()
        self.door_coords_list = door_coords_list
        self.door_width = 20
        self.top_collision = False
        self.bottom_collision = False
        self.right_collision = False
        self.left_collision = False

    
    def display_bg(self):
        screen.blit(self.image, self.rect)
    
    def enforce_walls(self):
        
        # Wall Collisons
        self.top_collision = False
        if player.rect.top - self.rect.top < 10:
            self.top_collision = True   

        self.bottom_collision = False
        if self.rect.bottom - player.rect.bottom < 10:
            self.bottom_collision = True  

        self.right_collision = False
        if self.rect.right - player.rect.right < 6:
            self.right_collision = True   

        self.left_collision = False
        if player.rect.left - self.rect.left < 0:
            self.left_collision = True

        # Door Non-collision
        for door_pair in self.door_coords_list:

            if door_pair[0] != 0 and door_pair[0] != l:
                if abs(player.rect.centerx - door_pair[0]) <= self.door_width and abs(player.rect.centery - door_pair[1]) < 100:
                    self.top_collision, self.bottom_collision = False, False
                    self.right_collision, self.left_collision = True, True
            if door_pair[1] != 0 and door_pair[1] != w:
                if abs(player.rect.centery - door_pair[1]) <= self.door_width and abs(player.rect.centerx - door_pair[0]) < 90:
                    self.right_collision, self.left_collision = False, False    
                    self.top_collision, self.bottom_collision = True, True
        
    def update(self):
        self.display_bg()
        self.enforce_walls()

# Functions
def player_sprite_collision():
    if pygame.sprite.spritecollide(player, ball_group, False):
        screen.blit(font_surf, (50,50))

def dis(a,b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# Init
pygame.init()
l, w = 1280, 720
screen = pygame.display.set_mode((l,w), pygame.SCALED, vsync=1)
pygame.display.set_caption('kustard')
clock = pygame.time.Clock()
running = True

# Sprite Groups
player = player_sprite()
player_group = pygame.sprite.GroupSingle()
player_group.add(player)

ball1 = ball_projectile(x=0, y=0, radius=20, speed=12)
ball_group = pygame.sprite.Group()
# ball_group.add(ball1)

dash_bar = hud_element(type='dash_bar', x=140, y=70)
hud_group = pygame.sprite.Group()
hud_group.add(dash_bar)

# BG
r1 = room([(661,0), (661,w), (0,300), (l,300)], 'room1')
r2 = room([(661,0), (661,w), (0,300), (l,300)], 'room2')

# Text
font = pygame.font.Font(None, 100)
font_surf = font.render(f'{r1.top_collision}', False, 'Black')

game_on = True
while running:
    # Handle Game Exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if game_on:
        # BG
        screen.blit(r1.image, r1.rect)
        r1.update()
        for door_pair in r1.door_coords_list:
            pygame.draw.circle(screen, "#FF0000", door_pair, 10)   
        
        # Draw & Update Sprites
        player_group.update()
        player_group.draw(screen)

        # ball_group.draw(screen)
        # ball_group.update()

        hud_group.update()
        hud_group.draw(screen)

        # Collision
        player_sprite_collision()

    # Update
    pygame.display.update()
    clock.tick(60)