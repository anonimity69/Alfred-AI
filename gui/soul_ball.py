import pygame
import numpy as np
import sounddevice as sd
import math
import sys
import random

# Configs
WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)
BASE_RADIUS = 150
NUM_DOTS = 1500

# Setup pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fully Audio Reactive Sphere")
clock = pygame.time.Clock()

# Global waveform data
waveform = np.zeros(NUM_DOTS)

# Audio callback
def audio_callback(indata, frames, time, status):
    global waveform
    samples = indata[:, 0]
    waveform = np.interp(np.linspace(0, len(samples), NUM_DOTS), np.arange(len(samples)), samples)

# Start microphone stream
stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=44100, blocksize=1024)
stream.start()

def spherical_to_cartesian(theta, phi, r=1):
    x = r * math.sin(phi) * math.cos(theta)
    y = r * math.sin(phi) * math.sin(theta)
    z = r * math.cos(phi)
    return x, y, z

def project(x, y, z, scale=600):
    factor = scale / (z + scale + 1e-5)
    x_proj = x * factor + CENTER[0]
    y_proj = y * factor + CENTER[1]
    return int(x_proj), int(y_proj)

def generate_points(n):
    points = []
    for _ in range(n):
        theta = random.uniform(0, 2 * math.pi)
        phi = math.acos(1 - 2 * random.uniform(0, 1))
        points.append((theta, phi))
    return points

points = generate_points(NUM_DOTS)

running = True
angle = 0

while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for i, (theta, phi) in enumerate(points):
        # Use audio waveform to perturb the radius per dot
        audio_mod = waveform[i] * 50  # more sensitivity
        r = BASE_RADIUS + audio_mod

        x, y, z = spherical_to_cartesian(theta, phi, r)

        # Rotate around Y-axis
        x_rot = x * math.cos(angle) - z * math.sin(angle)
        z_rot = x * math.sin(angle) + z * math.cos(angle)

        px, py = project(x_rot, y, z_rot)
        pygame.draw.circle(screen, (253, 218, 13), (px, py), 1)

    pygame.display.flip()
    angle += 0.01
    clock.tick(60)

stream.stop()
pygame.quit()
sys.exit()
