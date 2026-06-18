# Imports and Inits
import pygame
from enum import Enum
import math

pygame.init()
pygame.display.set_caption("Late")
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
running = True

# Global Variables
paths = []
obstacle_list = []

alive = True

key_force = 50

fps = 120
g = 9.18

w = False
a = False
s = False
d = False

# Colors
SNOW = pygame.Color("#b9e8ea")
SNOW_CLIFF = pygame.Color("#73c7ca")

# Maps
def ski_resort():
    # Starting Area
    fence1 = Path("fence1", SurfaceType.FENCE, Surfaces.WOOD, (screen.get_width() / 2) + 50, 290, 200, 10, 0)
    fence2 = Path("fence2", SurfaceType.FENCE, Surfaces.WOOD, (screen.get_width() / 2) - 250, 290, 200, 10, 0)
    fence3 = Path("fence3", SurfaceType.FENCE, Surfaces.WOOD, (screen.get_width() / 2) - 250, 800, 500, 10, 0)
    fence4 = Path("fence4", SurfaceType.FENCE, Surfaces.WOOD, (screen.get_width() / 2) - 260, 300, 10, 500, 0)
    fence5 = Path("fence5", SurfaceType.FENCE, Surfaces.WOOD, (screen.get_width() / 2) + 250, 300, 10, 500, 0)

    snow_start = Path("snow_start", SurfaceType.FLAT, Surfaces.SNOW, (screen.get_width() / 2) - 250, 300, 500, 500, 0)
    wood_path1 = Path("wood_path_1", SurfaceType.FLAT, Surfaces.WOOD, (screen.get_width() / 2) - 50, -190, 100, 500, 0)

# Classes
class RectButton:
    def __init__(self, name, color, start_x, start_y, width, height):
        self.name = name
        self.color = color
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(start_x, start_y, width, height)
    
    def drawButton(self):
        pygame.draw.rect(screen, self.color, self.rect)

class Vehicle:
    instance = None

    def __init__(self, name, pos, mass, velocity):
        self.name = name
        self.mass = mass
        self.velocity = velocity
        self.rectangle = pygame.Rect((screen.get_width() / 2) - 20, (screen.get_height() / 2) - 20, 40, 40)
        Vehicle.instance = self

    def update(self):
        path_update(self)
        blocks = check_for_blocking(self)

        if alive is True:
            if w == True:
                accelerate(v, pygame.Vector2(0, -(key_force)))
            if s == True:
                accelerate(v, pygame.Vector2(0, key_force))
            if a == True:
                if blocks[1] == False:
                    accelerate(v, pygame.Vector2(-(key_force), 0))
            if d == True:
                if blocks[0] == False:
                    accelerate(v, pygame.Vector2(key_force, 0))

        apply_friction(v)

        # Render (LAST)
        pygame.draw.rect(screen, "black", pygame.Rect((screen.get_width() / 2) - 20, (screen.get_height() / 2) - 20, 40, 40))

    def get_surface(self):
        for p in paths:
            if (screen.get_width() / 2) - 20 > p.start_x and (screen.get_width() / 2) + 20 < (p.start_x + p.width) and (screen.get_height() / 2) - 20 > p.start_y and (screen.get_height() / 2) + 20 < (p.start_y + p.height):
                return p

class SurfaceType(Enum):
    FLAT = 0
    WALL = 90
    RAMP_30 = 30
    RAMP_45 = 45
    RAMP_60 = 60
    FENCE = -1

class Surfaces(Enum): # Material = [friction, color]
    SNOW = [0.001, SNOW]
    WOOD = [0.01, "brown"]

class Path:
    def __init__(self, name, type, surface, start_x, start_y, width, height, thickness):
        self.name = name
        self.type = type
        self.surface = surface
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        self.thickness = thickness
        self.rectangle = pygame.Rect(self.start_x, self.start_y, self.width, self.height)
        paths.append(self)

# Movement
def net_force(*force_vectors):
    net_force_x = 0
    net_force_y = 0

    for force in force_vectors:
        net_force_x = net_force_x + force.x
        net_force_y = net_force_y + force.y

    return pygame.Vector2(net_force_x, net_force_y)

def calculate_speed(velocity):
    return math.sqrt(((velocity.x)*(velocity.x)) + (velocity.y)*(velocity.y))

def check_for_blocking(v):
    px = False
    mx = False
    py = False
    my = False

    col = v.rectangle.collidelist(obstacle_list)
    if col >= 0:
        obs = obstacle_list[col]
        if obs.left > ((screen.get_width() / 2)):
            v.velocity.x = 0
            px = True
        else:
            px = False

        if (obs.left + obs.width) < (screen.get_width() / 2):
            v.velocity.x = 0
            mx = True
        else:
            mx = False

        if obs.top > ((screen.get_height() / 2)):
            v.velocity.y = 0
            py = True
        else:
            py = False

        if (obs.top + obs.height) < (screen.get_height() / 2):
            v.velocity.y = 0
            my = True
        else:
            my = False

    return px, mx, py, my

def accelerate(vehicle, force_vector):
    A_vector = pygame.Vector2(force_vector.x / vehicle.mass, force_vector.y / vehicle.mass)

    vehicle.velocity = pygame.Vector2(vehicle.velocity.x + A_vector.x, vehicle.velocity.y + A_vector.y)

def apply_friction(vehicle):
    if vehicle.get_surface() is not None:
        mu = vehicle.get_surface().surface.value[0]
    else:
        mu = 0.0
    
    F = pygame.Vector2(vehicle.velocity.x * mu, vehicle.velocity.y * mu)
    vehicle.velocity = pygame.Vector2(vehicle.velocity.x - F.x, vehicle.velocity.y - F.y)

# Game Logic
def path_update(vehicle):
    obstacle_list.clear()
    for p in paths:
        p.start_x = p.start_x - vehicle.velocity.x
        p.start_y = p.start_y - vehicle.velocity.y

        if p.type.name == "FENCE":
            obstacle_list.append(pygame.Rect(p.start_x, p.start_y, p.width, p.height))

        pygame.draw.rect(screen, p.surface.value[1], pygame.Rect(p.start_x, p.start_y, p.width, p.height), p.thickness)

def kill(v):
    for p in paths:
        del p
    del v

sled = Vehicle("sled", pygame.Vector2(screen.get_width() / 2, (screen.get_height() / 2)), 2000, pygame.Vector2(0,0))
ski_resort()

while running:
    v = Vehicle.instance
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        w = True
    elif keys[pygame.K_w] == False:
        w = False
    
    if keys[pygame.K_a]:
        a = True
    elif keys[pygame.K_a] == False:
        a = False

    if keys[pygame.K_s]:
        s = True
    elif keys[pygame.K_s] == False:
        s = False

    if keys[pygame.K_d]:
        d = True
    elif keys[pygame.K_d] == False:
        d = False

    # Continuous update functions
    screen.fill(SNOW_CLIFF)
    v.update()

    pygame.display.flip()

    clock.tick(fps)

pygame.quit()