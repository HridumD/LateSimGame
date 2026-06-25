# Imports and Inits
import pygame
from enum import Enum
import time
import math

pygame.init()
pygame.mixer.init()

boing = pygame.mixer.Sound("Late/assets/boing.mp3")

start = time.perf_counter()

pygame.display.set_caption("Late")
screen = pygame.display.set_mode((1280,720))
clock = pygame.time.Clock()
running = True

# Global Variables
alive = True
side_view = False
end_game = False

win_text = ""

key_force = 200

fps = 120

w = False
a = False
s = False
d = False

paths = {}
obstacles = {}
ramps = {}
exit_ramps = {}
ends = {}

paths_adjusted = False

# Colors
SNOW = pygame.Color("#b9e8ea")
SNOW_CLIFF = pygame.Color("#73c7ca")

# Maps
def top_ski_resort():
    # Top View
    fence1 = Path("fence1", SurfaceType.OBSTACLE, Surfaces.WOOD, (screen.get_width() / 2) + 50, 290, 200, 10, 0, 0, View.TOP, 1)
    fence2 = Path("fence2", SurfaceType.OBSTACLE, Surfaces.WOOD, (screen.get_width() / 2) - 250, 290, 200, 10, 0, 0, View.TOP, 1)
    fence3 = Path("fence3", SurfaceType.OBSTACLE, Surfaces.WOOD, (screen.get_width() / 2) - 250, 800, 500, 10, 0, 0, View.TOP, 1)
    fence4 = Path("fence4", SurfaceType.OBSTACLE, Surfaces.WOOD, (screen.get_width() / 2) - 260, 300, 10, 500, 0, 0, View.TOP, 1)
    fence5 = Path("fence5", SurfaceType.OBSTACLE, Surfaces.WOOD, (screen.get_width() / 2) + 250, 300, 10, 500, 0, 0, View.TOP, 1)

    snow_start = Path("snow_start", SurfaceType.FLAT, Surfaces.SNOW, (screen.get_width() / 2) - 250, 300, 500, 500, 0, 0, View.TOP, 1)
    wood_path1 = Path("wood_path_1", SurfaceType.FLAT, Surfaces.WOOD, (screen.get_width() / 2) - 50, -200, 100, 600, 0, 0, View.TOP, 1)

    stage1 = Path("ramp1", SurfaceType.RAMP, Surfaces.RAMP, (screen.get_width() / 2) - 40, -180, 80, 80, 0, 0, View.TOP, 1)

    wood_path2 = Path("wood_path_2", SurfaceType.FLAT, Surfaces.WOOD, (screen.get_width() / 2) - 50, -500, 100, 200, 0, 0, View.TOP, 1)

    end = Path("end", SurfaceType.END, Surfaces.END, (screen.get_width() / 2) - 25, -475, 50, 50, 0, 0, View.TOP, 1)

    # Side View
    side_wood_path = Path("side_wood_path", SurfaceType.OBSTACLE, Surfaces.WOOD, (screen.get_width() / 2) - 40, (screen.get_height() / 2) + 40, 300, 40, 0, 0, View.SIDE, 1)
    side_wood_path2 = Path("side_wood_path2", SurfaceType.OBSTACLE, Surfaces.WOOD, (screen.get_width() / 2) + 450, (screen.get_height() / 2) + 40, 300, 40, 0, 0, View.SIDE, 1)

    side_exit_ramp = Path("side_exit_ramp", SurfaceType.EXIT_RAMP, Surfaces.EXIT_RAMP, (screen.get_width() / 2) + 670, (screen.get_height() / 2), 40, 40, 0, 0, View.SIDE, 1)

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
        if alive == True and side_view == False:
            blocks = check_for_blocking(self)

            check_win()

            if w is True and blocks[3] == False:
                accelerate(self, pygame.Vector2(0, -(key_force)))
            if s is True and blocks[2] == False:
                accelerate(self, pygame.Vector2(0, key_force))
            if a is True and blocks[1] == False:
                accelerate(self, pygame.Vector2(-(key_force), 0))
            if d is True and blocks[0] == False:
                accelerate(self, pygame.Vector2(key_force, 0))

            apply_friction(self)

            pygame.draw.rect(screen, "black", self.rectangle)

        if alive == True and side_view == True:
            blocks = check_for_blocking(self)

            if a is True and blocks[1] == False and blocks[2] == True:
                accelerate(self, pygame.Vector2(-(key_force), 0))
            if d is True and blocks[0] == False and blocks[2] == True:
                accelerate(self, pygame.Vector2(key_force, 0))

            if w is True and blocks[3] == False and blocks[2] == True:
                accelerate(self, pygame.Vector2(0, -4*(key_force)))

            if blocks[2] == False:
                accelerate(self, pygame.Vector2(0, 0.7*key_force))

            apply_friction(self)

            pygame.draw.rect(screen, "black", self.rectangle)

class SurfaceType(Enum):
    FLAT = 0
    RAMP = 45
    OBSTACLE = -1
    EXIT_RAMP = -45
    END = 100

class Surfaces(Enum): # Material = [friction, color]
    SNOW = [0.001, SNOW]
    WOOD = [0.01, "brown"]
    RAMP = [-1, "orange"]
    EXIT_RAMP = [-1, "red"]
    END = [0, "green"]

class View(Enum):
    TOP = 0
    SIDE = 1

class Path:
    def __init__(self, name, type, surface, start_x, start_y, width, height, thickness, angle, view, active):
        self.name = name
        self.type = type
        self.surface = surface
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        self.thickness = thickness
        self.angle = angle
        self.view = view
        self.active = active
        self.rectangle = pygame.Rect(self.start_x, self.start_y, self.width, self.height)

        if side_view == False and self.view == View.TOP:
            paths[self] = self.rectangle

        if side_view == True and self.view == View.SIDE:
            paths[self] = self.rectangle

    def update(self, vehicle):
        check_for_ramp()
        check_exit_ramp()

        if side_view == False:
            if self.view == View.TOP and self.active == 1:
                # Update path position
                self.rectangle = pygame.Rect(self.start_x, self.start_y, self.width, self.height)
                paths[self] = self.rectangle

                self.start_x = self.start_x - vehicle.velocity.x
                self.start_y = self.start_y - vehicle.velocity.y

                # Add to other important dictionaries
                if self.type.name == "OBSTACLE":
                    obstacles[self] = self.rectangle

                if self.type.name == "END":
                    ends[self] = self.rectangle

                # Render path (LAST)
                pygame.draw.rect(screen, self.surface.value[1], self.rectangle, self.thickness)
        elif side_view == True:
            if self.view == View.SIDE and self.active == 1:
                # Update path position
                self.rectangle = pygame.Rect(self.start_x, self.start_y, self.width, self.height)
                paths[self] = self.rectangle

                if self.start_y < 0:
                    kill(vehicle)

                self.start_x = self.start_x - vehicle.velocity.x
                self.start_y = self.start_y - vehicle.velocity.y

                # Add to other important dictionaries
                if self.type.name == "OBSTACLE":
                    obstacles[self] = self.rectangle

                if self.type.name == "RAMP":
                    ramps[self] = self.rectangle

                if self.type.name == "EXIT_RAMP":
                    exit_ramps[self] = self.rectangle

                # Render path (LAST)
                pygame.draw.rect(screen, self.surface.value[1], self.rectangle, self.thickness)

# Movement
def check_win():
    collided = v.rectangle.collidedictall(ends, 1)
    
    global end_game
    global text_surface

    if len(collided) > 0 and end_game == False:
        global win_text

        paths.clear()
        end_game = True

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
                if v.velocity.x > 0:
                    v.velocity.x = 0
                    boing.play()
                px = True
            else:
                px = False

            if (obs.left + obs.width) < (screen.get_width() / 2):
                if v.velocity.x < 0:
                    v.velocity.x = 0
                    boing.play()
                mx = True
            else:
                mx = False

            if obs.top > ((screen.get_height() / 2)):
                if v.velocity.y > 0:
                    v.velocity.y = 0
                    boing.play()
                py = True
            else:
                py = False

            if (obs.top + obs.height) < (screen.get_height() / 2):
                if v.velocity.y < 0:
                    v.velocity.y = 0
                    boing.play()
                my = True
            else:
                my = False

    return px, mx, py, my, side

def accelerate(vehicle, force_vector):
    A_vector = pygame.Vector2(force_vector.x / vehicle.mass, force_vector.y / vehicle.mass)

    vehicle.velocity = pygame.Vector2(vehicle.velocity.x + A_vector.x, vehicle.velocity.y + A_vector.y)

def get_surface_friction():
    collided = v.rectangle.collidedictall(paths, 1)
    if len(collided) > 0:
        return(collided[0][0].surface.value[0])
    else:
        if alive == True and side_view == False and end_game == False:
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

def check_for_ramp():
    collided = v.rectangle.collidedictall(paths, 1)
    global side_view

    if len(collided) > 0:
        for c in collided:
            sf = c[0].surface.value[0]
            if sf < 0 and side_view == False:
                side_view = True
                paths.clear()
                top_ski_resort()
                v.velocity.x = -v.velocity.y
                v.velocity.y = 0

def check_exit_ramp():
    collided = v.rectangle.collidedictall(exit_ramps, 1)
    global side_view
    global paths_adjusted

    if collided is not None:
        if len(collided) > 0 and side_view == True:
            side_view = False
            v.velocity = pygame.Vector2(0, 0)

            paths.clear()
            obstacles.clear()

            top_ski_resort()

            if paths_adjusted == False:
                adjust_paths()

            side_view = False

def adjust_paths():
    global paths_adjusted
    paths_adjusted = True

    for p in paths:
        if p.view == View.TOP:
            p.start_y = p.start_y + 700

def kill(vehicle):
    global alive
    global paths_adjusted
    global side_view

    alive = False
    vehicle.velocity = pygame.Vector2(0, 0)
    
    paths_adjusted = False

    paths.clear()
    obstacles.clear()

    alive = True
    top_ski_resort()

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

    try:
        for p in paths:
            p.update(v)
    except RuntimeError as e:
        if "dictionary changed size during iteration" in str(e):
            pass
        else:
            raise

    v.update()

    if end_game == True:
        # Win Text
        end = time.perf_counter()
        total_time = end - start

        font = pygame.font.SysFont(None, 50)
        text_surface = font.render(f'You were {str(math.floor(total_time))}s late', True, "black")
        text_rect = text_surface.get_rect()
        text_rect.center = (400, 300)
        screen.blit(text_surface, text_rect)

    pygame.display.flip()

    clock.tick(fps)

pygame.quit()
