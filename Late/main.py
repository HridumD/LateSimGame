import pygame
from enum import Enum

pygame.init()
pygame.display.set_caption("Late")
screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True

surfaces = {}

w = False
a = False
s = False
d = False

# GUI
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

# Objects
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
        self.pos = pygame.Vector2(self.pos.x + self.velocity.x, self.pos.y + self.velocity.y) # Update position based on velocity

        if w == True:
            accelerate(v, pygame.Vector2(0, -50))
        if a == True:
            accelerate(v, pygame.Vector2(-50, 0))
        if s == True:
            accelerate(v, pygame.Vector2(0, 50))
        if d == True:
            accelerate(v, pygame.Vector2(50, 0))

    def get_surface(self):
        for s in surfaces:
            print(s)

class SurfaceType(Enum):
    FLAT = 0
    WALL = 90
    RAMP_30 = 30
    RAMP_45 = 45
    RAMP_60 = 60

class SurfaceFrictions(Enum):
    ICE = 0
    ASPHALT = 0.5

class Path:
    def __init__(self, name, type, surface):
        self.name = name
        self.type = type
        self.surface = surface

# Movement
def net_force(*force_vectors):
    net_force_x = 0
    net_force_y = 0

    for force in force_vectors:
        net_force_x = net_force_x + force.x
        net_force_y = net_force_y + force.y

    return pygame.Vector2(net_force_x, net_force_y)

def accelerate(vehicle, force_vector):
    # F = ma
    a_vector = pygame.Vector2(force_vector.x / vehicle.mass, force_vector.y / vehicle.mass)
    vehicle.velocity = pygame.Vector2(vehicle.velocity.x + a_vector.x, vehicle.velocity.y + a_vector.y)

car = Vehicle("car", pygame.Vector2(screen.get_width() / 2, screen.get_height()), 2000, pygame.Vector2(0,0))

# Game Logic
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

    screen.fill("white")

    v.update()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()