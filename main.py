import pygame

pygame.init()
pygame.display.set_caption("Late")
screen = pygame.display.set_mode((1280,720), pygame.RESIZABLE)
clock = pygame.time.Clock()
running = True

vehicles = []
temp_gui = []

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
    def __init__(self, name, pos, mass, velocity):
        self.name = name
        self.pos = pos
        self.mass = mass
        self.velocity = velocity

    def create_vehicle(self):
        pygame.draw.circle(screen, "red", self.pos, 40)

class Path:
    def __init__(self, vehicle, length, pos):
        self.vehicle = vehicle
        self.length = length
        self.pos = pos

# Game Logic
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if(event.key == pygame.K_SPACE):
                print("Space pressed!")

    screen.fill("white")

    # Permanent GUI
    pause_button = RectButton("pause", "red", screen.get_width()-90, 20, 70, 70).drawButton()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()