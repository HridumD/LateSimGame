import pygame
from enum import Enum
import math

pygame.init()
pygame.display.set_caption("Late")
screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True

paths = []

fps = 120
g = 9.18

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
        self.kinetic_energy_vector = pygame.Vector2((0.5 * self.mass * ((self.velocity.x) * (self.velocity.x))), (0.5 * self.mass * ((self.velocity.y) * (self.velocity.y))))
        Vehicle.instance = self

        self.kinetic_energy_vector = pygame.Vector2(0, -100)

    def update(self):
        # Render
        pygame.draw.circle(screen, "black", self.pos, 40)
        
        # Movement
        self.pos = pygame.Vector2(self.pos.x + self.velocity.x, self.pos.y + self.velocity.y) # Update position based on velocity

        # if w == True:
        #     accelerate(v, pygame.Vector2(0, -50), get_kinetic_friction_force(v))
        # if a == True:
        #     accelerate(v, pygame.Vector2(-50, 0), get_kinetic_friction_force(v))
        # if s == True:
        #     accelerate(v, pygame.Vector2(0, 50), get_kinetic_friction_force(v))
        # if d == True:
        #     accelerate(v, pygame.Vector2(50, 0), get_kinetic_friction_force(v))

        Wfx = kinetic_friction_work(self, self.get_surface(), self.velocity.x)
        Wfy = kinetic_friction_work(self, self.get_surface(), self.velocity.y)

        # if Wfx is not None:
        #     self.kinetic_energy_vector = pygame.Vector2(self.kinetic_energy_vector.x - Wfx, self.kinetic_energy_vector.y)
        # if Wfy is not None:
        #     self.kinetic_energy_vector = pygame.Vector2(self.kinetic_energy_vector.x, self.kinetic_energy_vector.y - Wfy)

        self.kinetic_energy_vector = self.kinetic_energy_vector - pygame.Vector2(0, kinetic_friction_work(v, v.get_surface(), self.velocity.y))
        self.velocity = calc_new_velocity(self.kinetic_energy_vector, v)

        print(self.kinetic_energy_vector)

    # Motion and such
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

class SurfaceFrictions(Enum): # MATERIAL = [KINETIC, STATIC]
    ICE = [0, 0.1] 
    ASPHALT = [0.5, 0.3]

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

    def update(self):
        pygame.draw.rect(screen, "black", pygame.Rect(self.start_x, self.start_y, self.width, self.height))

# Movement & Energy
def net_force(*force_vectors):
    net_force_x = 0
    net_force_y = 0

    for force in force_vectors:
        net_force_x = net_force_x + force.x
        net_force_y = net_force_y + force.y

    return pygame.Vector2(net_force_x, net_force_y)

def calculate_speed(velocity):
    return math.sqrt(((velocity.x)*(velocity.x)) + (velocity.y)*(velocity.y))

def accelerate(vehicle, force_vector, friction_vector):
    if vehicle.get_surface() is not None:
        total_force = net_force(force_vector, friction_vector)

        a_vector = pygame.Vector2(total_force.x / vehicle.mass, total_force.y / vehicle.mass)
        vehicle.velocity = pygame.Vector2(vehicle.velocity.x + a_vector.x, vehicle.velocity.y + a_vector.y)
    else:
        a_vector = pygame.Vector2(force_vector.x / vehicle.mass, force_vector.y / vehicle.mass)
        vehicle.velocity = pygame.Vector2(vehicle.velocity.x + a_vector.x, vehicle.velocity.y + a_vector.y)

def translational_kinetic_energy(vehicle):
    s = calculate_speed(vehicle.velocity)
    return (0.5 *  vehicle.mass * (s*s))

def get_kinetic_friction_force(vehicle):
    if vehicle.get_surface() is not None:
        F = pygame.Vector2(vehicle.get_surface().surface.value[1] * vehicle.mass * g, vehicle.get_surface().surface.value[1] * vehicle.mass * g)
        return F
    else:
        return pygame.Vector2(0, 0)

def kinetic_friction_work(vehicle, path, component):
    if path is not None:
        mu = path.surface.value[1]
        m = vehicle.mass
        dist_pf = component / fps

        Wf = (mu) * (m) * (g) * (dist_pf)

        return Wf
    else:
        return 0

def calc_new_velocity(kinetic_energy, v):
    x_mod = 1
    y_mod = 1

    if kinetic_energy.x < 0:
        x_mod = -1
    elif kinetic_energy.x > 0:
        x_mod = 1

    if kinetic_energy.y < 0:
        y_mod = -1
    elif kinetic_energy.y > 0:
        y_mod = 1

    return pygame.Vector2((x_mod * math.sqrt((2*(abs(kinetic_energy.x)))/(v.mass))), (y_mod * math.sqrt((2*abs((kinetic_energy.y))/(v.mass)))))

car = Vehicle("car", pygame.Vector2(screen.get_width() / 2, screen.get_height()), 2000, pygame.Vector2(0,0))
asphalt_sheet = Path("asphalt", SurfaceType.FLAT, SurfaceFrictions.ASPHALT, (screen.get_width() / 2) - 25, 60, 50, 500)

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

    # Continuous update functions
    screen.fill("white")
    v.update()
    for p in paths:
        p.update()

    pygame.display.flip()

    clock.tick(fps)

pygame.quit()