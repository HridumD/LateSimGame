# Imports and Inits
import pygame
from enum import Enum
import math

pygame.init()
pygame.display.set_caption("Late")
screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True

# Global Variables
paths = []

key_force = 50

fps = 120
g = 9.18

w = False
a = False
s = False
d = False

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
        self.pos = pos
        self.mass = mass
        self.velocity = velocity
        Vehicle.instance = self

    def update(self):
        # Render
        pygame.draw.circle(screen, "black", self.pos, 40)
        
        # Movement
        # self.pos = pygame.Vector2(self.pos.x + self.velocity.x, self.pos.y + self.velocity.y) # Update position based on velocity

        if w == True:
            accelerate(v, pygame.Vector2(0, -(key_force)))
        if s == True:
            accelerate(v, pygame.Vector2(0, key_force))
        if a == True:
            accelerate(v, pygame.Vector2(-(key_force), 0))
        if d == True:
            accelerate(v, pygame.Vector2(key_force, 0))

        apply_friction(v)

    def get_surface(self):
        for p in paths:
            if self.pos.x > p.start_x and self.pos.x < (p.width + p.start_x) and self.pos.y > p.start_y and self.pos.y < (p.height + p.start_y):
                return p

class SurfaceType(Enum):
    FLAT = 0
    WALL = 90
    RAMP_30 = 30
    RAMP_45 = 45
    RAMP_60 = 60

class Surfaces(Enum): # Material = [friction, color]
    ICE = [0, "blue"]
    RUBBER = [0.1, "pink"]

class Path:
    def __init__(self, name, type, surface, start_x, start_y, width, height):
        self.name = name
        self.type = type
        self.surface = surface
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        paths.append(self)

    def update(self, vehicle):
        self.start_x = self.start_x - vehicle.velocity.x
        self.start_y = self.start_y - vehicle.velocity.y

        pygame.draw.rect(screen, self.surface.value[1], pygame.Rect(self.start_x, self.start_y, self.width, self.height))

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

def accelerate(vehicle, force_vector):
    A_vector = pygame.Vector2(force_vector.x / vehicle.mass, force_vector.y / vehicle.mass)

    vehicle.velocity = pygame.Vector2(vehicle.velocity.x + A_vector.x, vehicle.velocity.y + A_vector.y)

def apply_friction(vehicle):
    if vehicle.get_surface() is not None:
        mu = vehicle.get_surface().surface.value[0]

        F = pygame.Vector2(vehicle.velocity.x * mu, vehicle.velocity.y * mu)

        vehicle.velocity = pygame.Vector2(vehicle.velocity.x - F.x, vehicle.velocity.y - F.y)
    else:
        pass

# Game Logic
asphalt_sheet = Path("rubber", SurfaceType.FLAT, Surfaces.RUBBER, (screen.get_width() / 2) - 25, 60, 50, 500)
sled = Vehicle("sled", pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2), 2000, pygame.Vector2(0,0))

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
    screen.fill("white")
    for p in paths:
        p.update(v)
    v.update()

    pygame.display.flip()

    clock.tick(fps)

pygame.quit()