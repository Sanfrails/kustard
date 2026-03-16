import pygame
import time
from math import *
import pathlib
resources_path = pathlib.Path().cwd() / 'resources'

# Classes 
class player_sprite(pygame.sprite.Sprite):
    
    def __init__(self):
        super().__init__()
        # Images
        scale = 0.6
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
        self.last_dashed = 0
        self.dash_max = 4
        self.dash_interval = 0.3
        # Health
        # self.health_pts = 4
    
    def move(self):
        move_speed = 8
        keys = pygame.key.get_pressed()
        # Key Bools
        any_wasd = keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d]
        opposites_wasd = (keys[pygame.K_a] and keys[pygame.K_d]) or (keys[pygame.K_w] and keys[pygame.K_s])
        diagonals_wasd = (keys[pygame.K_w] and keys[pygame.K_d]) or (keys[pygame.K_w] and keys[pygame.K_a]) or (keys[pygame.K_s] and keys[pygame.K_d]) or (keys[pygame.K_s] and keys[pygame.K_a])

        # Speed Adjustment for Diagonal Movement
        if diagonals_wasd:
            move_speed = move_speed/sqrt(2)

        # Dash
        if (any_wasd and keys[pygame.K_l]) and (time.perf_counter() - self.last_dashed > 1) and dash_bar.hud_index < 3:
            self.accelerate = True
            self.last_dashed = time.perf_counter()
            dash_bar.consume()
        if self.accelerate:
            t = (time.perf_counter() - self.last_dashed)
            a = 4*(1-self.dash_max)/(self.dash_interval**2)
            b = 4*(self.dash_max-1)/(self.dash_interval)
            acc_factor = a*(t**2) + b*(t) + 1
            if t < self.dash_interval:
                move_speed = move_speed*acc_factor
            else:    
                self.accelerate = False
                move_speed = move_speed
            
        # UP-LEFT-RIGHT-DOWN MOVEMENT
        if keys[pygame.K_w] and (not active_room.top_collision):
            self.rect.y -= move_speed
        if keys[pygame.K_s] and (not active_room.bottom_collision):
            self.rect.y += move_speed
        if keys[pygame.K_a] and (not active_room.left_collision):
            self.rect.x = self.rect.x - move_speed
            # Orientation
            if self.lookn_right:
                for i in range(len(self.player_frames)):
                    self.player_frames[i] = pygame.transform.flip(self.player_frames[i], 1, 0)
                self.lookn_right = False
                self.lookn_left = True
        if keys[pygame.K_d] and (not active_room.right_collision):
            self.rect.x = self.rect.x + move_speed
            # Orientation
            if self.lookn_left:
                for i in range(len(self.player_frames)):
                    self.player_frames[i] = pygame.transform.flip(self.player_frames[i], 1, 0)
                self.lookn_left = False
                self.lookn_right = True
        
        # surf = font.render(f'{self.rect.center}', 0 , 'black')
        # screen.blit(surf,surf.get_rect())

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

class hud_element(pygame.sprite.Sprite):
    
    def __init__(self, type, x, y, replenish_speed):
        super().__init__()

        self.hud_element_frames = []
        self.hud_index = 0
        for image_path in sorted(pathlib.Path(resources_path / f'hud/{type}').iterdir()):
            image = pygame.image.load(image_path)
            self.hud_element_frames.append(image)

        self.replenish_speed = replenish_speed
        self.image = self.hud_element_frames[self.hud_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.previous_replenish = time.perf_counter()
        self.begin_replenish = False

    def consume(self):
        self.hud_index += 1
        self.image = self.hud_element_frames[self.hud_index]
    
    def replenish(self):
        if self.hud_index > 0 and not self.begin_replenish:
            self.begin_replenish = True
            self.previous_replenish = time.perf_counter()
        if self.hud_index == 0:
            self.begin_replenish = False

        if (time.perf_counter() - self.previous_replenish > 1/self.replenish_speed) and self.begin_replenish:
            self.hud_index -= 1
            self.image = self.hud_element_frames[self.hud_index]
            self.previous_replenish = time.perf_counter()

    def update(self):
        self.replenish()

class room():

    def __init__(self, bg_name, wall_width=8, door_coords_list=[], door_width=20, oob_degree=20, sprite_groups=[]):

        # Setup 
        self.image = pygame.image.load(resources_path / f'bg/{bg_name}.png')
        self.rect = self.image.get_rect()
        self.wall_width = wall_width
        self.door_coords_list = door_coords_list
        self.door_width = door_width
        self.oob_degree = oob_degree
        self.sprite_groups = sprite_groups
        # Collision Bools
        self.top_collision = False
        self.bottom_collision = False
        self.right_collision = False
        self.left_collision = False
        # Doors Setup
        self.door_pairs_dic = {}
        for coords in self.door_coords_list:
            self.door_pairs_dic.update({coords:None})
        self.closed_doors_list = []

    def display_bg(self):
        screen.blit(self.image, self.rect)
    
    def connect_doors(self, door1, room2, door2):
        self.door_pairs_dic.update({door1:(room2, door2)})

    def close_doors(self, door_list):
        for door in door_list:
            self.closed_doors_list.append(door)
    
    def open_doors(self, door_list):
        for door in door_list:
            self.closed_doors_list.remove(door)

    def enforce_walls(self):
        
        # Wall Collisons
        self.top_collision = False
        if player.rect.top - self.rect.top < self.wall_width:
            self.top_collision = True   

        self.bottom_collision = False
        if self.rect.bottom - player.rect.bottom < self.wall_width:
            self.bottom_collision = True  

        self.right_collision = False
        if self.rect.right - player.rect.right < -self.wall_width:
            self.right_collision = True

        self.left_collision = False
        if player.rect.left - self.rect.left < -self.wall_width:
            self.left_collision = True

        # Door Non-collision
        for door_pair in self.door_coords_list:
            if door_pair in self.closed_doors_list:
                continue
            if door_pair[0] != 0 and door_pair[0] != l:
                if abs(player.rect.centerx - door_pair[0]) <= self.door_width and abs(player.rect.centery - door_pair[1]) < 100:
                    self.top_collision, self.bottom_collision = False, False
                    self.right_collision, self.left_collision = True, True
            if door_pair[1] != 0 and door_pair[1] != w:
                if abs(player.rect.centery - door_pair[1]) <= self.door_width and abs(player.rect.centerx - door_pair[0]) < 90:
                    self.right_collision, self.left_collision = False, False    
                    self.top_collision, self.bottom_collision = True, True
        
    def door_access(self): 
        # Door Transfer
        oob_bool = (player.rect.centerx - l > self.oob_degree) or (-player.rect.centerx > self.oob_degree) or (-player.rect.centery > self.oob_degree) or (player.rect.centery - w > self.oob_degree) 
        if oob_bool:
            for door_pair in self.door_coords_list:
                if dis(player.rect.center, door_pair) < 50:
                    global active_room
                    active_room = self.door_pairs_dic[door_pair][0]
                    player.rect.center = self.door_pairs_dic[door_pair][1]
                    self.inform_sprites()

    def activate_sprite_groups(self):
        if active_room == self:
            for group in self.sprite_groups:
                group.update()
                group.draw(screen)

    def inform_sprites(self):
        # Inform sprites to seek player
        for group in self.sprite_groups:
                for sprite in group:
                    sprite.aware_of_player = False
                    sprite.start_seeking = True
        
    def update(self):
        self.display_bg()
        self.enforce_walls()
        self.door_access()
        self.activate_sprite_groups()

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

class hostile_npc(pygame.sprite.Sprite):

    def __init__(self, npc_name, move_speed, search_time=0.3):
        super().__init__()
        # Setup
        self.npc_frames = []
        self.npc_frame_index = 0
        for image_path in pathlib.Path(resources_path / f'npc/{npc_name}').iterdir():
            image = pygame.image.load(image_path)
            image = pygame.transform.scale2x(image)
            self.npc_frames.append(image)
        self.move_speed = move_speed
        self.search_time = search_time
        # Image and Rect 
        self.image = self.npc_frames[self.npc_frame_index]
        self.image = pygame.transform.scale(self.image, (240,240))
        self.rect = self.image.get_rect()
        self.rect.center = (500,500)
        # Orientation
        self.lookn_right = False
        self.lookn_left = True
        # Awareness
        self.aware_of_player = False
        self.start_seeking = True
        self.time_sought = 0

    def awareness_of_player(self):
        if self.start_seeking:
            self.seek_start_time = time.perf_counter()
            self.start_seeking = False
        if not self.aware_of_player:
            self.time_sought = time.perf_counter() - self.seek_start_time
        if self.time_sought > self.search_time:
            self.aware_of_player = True
            self.time_sought = 0

    def move(self):
        self.move_speed = 1
        # Find Player's Direction
        x_to_player = (player.rect.centerx - self.rect.centerx)
        self.xsign = (x_to_player > 0) - (x_to_player < 0)
        y_to_player = (player.rect.centery - self.rect.centery)
        self.ysign = (y_to_player > 0) - (y_to_player < 0)
        # Diagonal Walking
        if self.xsign and self.ysign:
            self.move_speed = self.move_speed*sqrt(2)
        # Move towards player
        if self.aware_of_player:
            self.rect.centerx += self.xsign*self.move_speed
            self.rect.centery += self.ysign*self.move_speed
        
    def animate(self):
        if self.aware_of_player:
            # Walking Animation
            npc_fps = 0.11
            if self.xsign or self.ysign:
                self.npc_frame_index = (self.npc_frame_index + npc_fps) % (len(self.npc_frames))
                self.image = self.npc_frames[int(self.npc_frame_index)]
            # Orientation
            if self.xsign == 1 and self.lookn_left:
                for i in range(len(self.npc_frames)):
                        self.npc_frames[i] = pygame.transform.flip(self.npc_frames[i], 1, 0)
                        self.lookn_left = False
                        self.lookn_right = True
            if self.xsign == -1 and self.lookn_right:
                for i in range(len(self.npc_frames)):
                        self.npc_frames[i] = pygame.transform.flip(self.npc_frames[i], 1, 0)
                        self.lookn_left = True
                        self.lookn_right = False

    def update(self):
        self.awareness_of_player()
        self.move()
        self.animate()

# Functions
def player_sprite_collision():
    if pygame.sprite.spritecollide(player, ball_group, False):
        font_surf = font.render('Collision!', 0, "#FF0000")
        screen.blit(font_surf, (800,600))

def dis(a,b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def connect_doors_2way(r1,r2,p1,p2):
    r1.connect_doors(p1, r2, p2)
    r2.connect_doors(p2, r1, p1)

# User_Events
# CHANGED_ROOMS = pygame.USEREVENT + 1

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

dash_bar = hud_element(type='dash_bar', x=140, y=70, replenish_speed=5)
health_bar = hud_element(type='health_bar', x=140, y=110, replenish_speed=0.1)
hud_group = pygame.sprite.Group()
hud_group.add([dash_bar, health_bar])

ball = ball_projectile(x=0, y=0, radius=20, speed=12)
ball_group = pygame.sprite.Group()
ball_group.add(ball)

ego = hostile_npc('ego', move_speed=1)
ego_group = pygame.sprite.Group()
# ego_group.add(ego)

# BG
r1 = room('room1', door_coords_list=[(661,0),(l,300)], sprite_groups=[ego_group])
r2 = room('room2', door_coords_list=[(0,300), (661,w)], sprite_groups=[ball_group])
connect_doors_2way(r1,r2,(l,300),(0,300))
connect_doors_2way(r1,r2,(661,0),(661,w))
active_room = r1

# Text
font = pygame.font.Font(None, 100)

game_on = True
while running:
    # Handle Game Exit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if game_on:
        # BG
        screen.blit(active_room.image, active_room.rect)
        active_room.update()
        for door_pair in active_room.door_coords_list:
            pygame.draw.circle(screen, "#FF0000", door_pair, 10)   
        
        # Draw & Update Sprites
        player_group.update()
        player_group.draw(screen)

        hud_group.update()
        hud_group.draw(screen)

        # Collision
        player_sprite_collision()

    # Update
    pygame.display.update()
    clock.tick(60)