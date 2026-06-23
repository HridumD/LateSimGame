# Imports and Inits
import pygame
from enum import Enum

pygame.init()
pygame.display.set_caption("Late")
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
running = True

# Global Variables
alive = True

side_view = False

key_force = 50

fps = 120

w = False
a = False
s = False
d = False

paths = {}
obstacles = {}

# Colors
SNOW = pygame.Color("#b9e8ea")
SNOW_CLIFF = pygame.Color("#73c7ca")

# Maps
def top_ski_resort():
    # Starting Area
    fence1 = Path("fence1", SurfaceType.OBSTACLE, Surfaces.WOOD, (screen.get_width() / 2) + 50, 290, 200, 10, 0, 0)
    fence2 = Path("fence2", SurfaceType.OBSTACLE, Surfaces.WOOD, (screen.get_width() / 2) - 250, 290, 200, 10, 0, 0)
    fence3 = Path("fence3", SurfaceType.OBSTACLE, Surfaces.WOOD, (screen.get_width() / 2) - 250, 800, 500, 10, 0, 0)
    fence4 = Path("fence4", SurfaceType.OBSTACLE, Surfaces.WOOD, (screen.get_width() / 2) - 260, 300, 10, 500, 0, 0)
    fence5 = Path("fence5", SurfaceType.OBSTACLE, Surfaces.WOOD, (screen.get_width() / 2) + 250, 300, 10, 500, 0, 0)

    snow_start = Path("snow_start", SurfaceType.FLAT, Surfaces.SNOW, (screen.get_width() / 2) - 250, 300, 500, 500, 0, 0)
    wood_path1 = Path("wood_path_1", SurfaceType.FLAT, Surfaces.WOOD, (screen.get_width() / 2) - 50, -290, 100, 600, 0, 0)

    stage1 = Path("ramp1", SurfaceType.RAMP, Surfaces.RAMP, (screen.get_width() / 2) - 40, -180, 80, 80, 0, 0)

# Classes
class Vehicle:
    instance = None

    def __init__(self, name, size, mass, velocity):
        self.name = name
        self.mass = mass
        self.velocity = velocity
        self.size = size
        self.rectangle = pygame.Rect((screen.get_width() / 2) - (self.size / 2), (screen.get_height() / 2) - (self.size / 2), self.size, self.size)
        Vehicle.instance = self

    def update(self):
        if alive == True:
            blocks = check_for_blocking(self)

            if w is True and blocks[3] == False:
                accelerate(self, pygame.Vector2(0, -(key_force)))
            if s is True and blocks[2] == False:
                accelerate(self, pygame.Vector2(0, key_force))
            if a is True and blocks[1] == False:
                accelerate(self, pygame.Vector2(-(key_force), 0))
            if d is True and blocks[0] == False:
                accelerate(self, pygame.Vector2(key_force, 0))

            apply_friction(self)
            check_for_ramp()

            pygame.draw.rect(screen, "black", self.rectangle)

class SurfaceType(Enum):
    FLAT = 0
    RAMP = 45
    OBSTACLE = -1

class Surfaces(Enum): # Material = [friction, color]
    SNOW = [0.001, SNOW]
    WOOD = [0.01, "brown"]
    RAMP = [-1, "green"]

class Path:
    def __init__(self, name, type, surface, start_x, start_y, width, height, thickness, angle):
        self.name = name
        self.type = type
        self.surface = surface
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        self.thickness = thickness
        self.angle = angle
        self.rectangle = pygame.Rect(self.start_x, self.start_y, self.width, self.height)
        paths[self] = self.rectangle

    def update(self, vehicle):
        # Update path position
        self.rectangle = pygame.Rect(self.start_x, self.start_y, self.width, self.height)
        paths[self] = self.rectangle

        self.start_x = self.start_x - vehicle.velocity.x
        self.start_y = self.start_y - vehicle.velocity.y

        # Add to other important dictionaries
        if self.type.name == "OBSTACLE":
            obstacles[self] = self.rectangle

        # Render path (LAST)
        pygame.draw.rect(screen, self.surface.value[1], self.rectangle, self.thickness)

# Movement
def check_for_blocking(v):
    px = False
    mx = False
    py = False
    my = False
    side = False

    collided = v.rectangle.collidedictall(obstacles, 1)
    if len(collided) >= 0:
        for c in collided:
            obs = c[1]
            if (obs.left) > ((screen.get_width() / 2)):
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

    return px, mx, py, my, side

def accelerate(vehicle, force_vector):
    A_vector = pygame.Vector2(force_vector.x / vehicle.mass, force_vector.y / vehicle.mass)

    vehicle.velocity = pygame.Vector2(vehicle.velocity.x + A_vector.x, vehicle.velocity.y + A_vector.y)

def check_for_ramp():
    collided = v.rectangle.collidedictall(paths, 1)
    if len(collided) > 0:
        for c in collided:
            sf = c[0].surface.value[0]
            if sf < 0:
                return True
            else:
                return False
    else:
        return False

def get_surface_friction():
    collided = v.rectangle.collidedictall(paths, 1)
    if len(collided) > 0:
        return(collided[0][0].surface.value[0])
    else:
        if alive == True:
            kill(v)

def apply_friction(vehicle):
    if get_surface_friction() is not None:
        mu = get_surface_friction()
    else:
        mu = 0.0
    
    F = pygame.Vector2(vehicle.velocity.x * mu, vehicle.velocity.y * mu)
    vehicle.velocity = pygame.Vector2(vehicle.velocity.x - F.x, vehicle.velocity.y - F.y)

# Game Logic
sled = Vehicle("sled", 40, 2000, pygame.Vector2(0,0))

top_ski_resort()

def respawn():
    global alive
    alive = True

    top_ski_resort()

def kill(vehicle):
    global alive
    alive = False
    vehicle.velocity = pygame.Vector2(0, 0)

    paths.clear()
    obstacles.clear()

    respawn()


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

    for p in paths:
        p.update(v)

    v.update()

    pygame.display.flip()

    clock.tick(fps)

pygame.quit()
