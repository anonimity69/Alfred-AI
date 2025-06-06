import pygame
import random
import math
import sys

# Configs
WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)
RADIUS = 300
NUM_DOTS = 2000

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Dot Sphere")
clock = pygame.time.Clock()

def spherical_to_cartesian(theta, phi, r=1):
    """Convert spherical coordinates to Cartesian"""
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    return x, y, z

def project(x, y, z, scale=600):
    """Perspective projection"""
    factor = scale / (z + scale)
    x_proj = x * factor + CENTER[0]
    y_proj = y * factor + CENTER[1]
    return int(x_proj), int(y_proj)

def generate_points(n):
    points = []
    for _ in range(n):
        theta = random.uniform(0, 2 * math.pi)
        phi = math.acos(1 - 2 * random.uniform(0, 1))  # uniform spherical distribution
        x, y, z = spherical_to_cartesian(theta, phi, RADIUS)
        points.append((x, y, z))
    return points

points = generate_points(NUM_DOTS)

# Main loop
running = True
angle = 0
while running:
    screen.fill((0, 0, 0))  # Background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for x, y, z in points:
        # Simple Y-axis rotation
        x_rot = x * math.cos(angle) - z * math.sin(angle)
        z_rot = x * math.sin(angle) + z * math.cos(angle)

        px, py = project(x_rot, y, z_rot)
        pygame.draw.circle(screen, (255, 255, 255), (px, py), 1)

    pygame.display.flip()
    angle += 0.01  # Rotate slowly
    clock.tick(60)

pygame.quit()
sys.exit()
