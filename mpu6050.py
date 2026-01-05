import utils.session
import pygame
import serial
import time
import sys
import random

# ------------------
# Bluetooth Setup
# ------------------
bt_port = 'COM5'   # Change this to your HC-05 COM port (check Device Manager)
bt_baud = 38400

try:
    ser = serial.Serial(bt_port, bt_baud, timeout=0.1)
    time.sleep(2)
    print(f"✅ Connected to {bt_port}")
except serial.SerialException:
    print("❌ Failed to connect to Bluetooth")
    sys.exit()

# ------------------
# Pygame Setup
# ------------------
pygame.init()
win_width, win_height = 800, 600
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("3D Sprite Control - MPU6050 Joystick")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Player (3D sprite simulated as circle)
player_radius = 20
player_x, player_y = win_width // 2, win_height - 50

# Falling obstacles
stone_width, stone_height = 40, 40
stone_speed = 5
stone_count = 5
stones = [{"x": random.randint(0, win_width - stone_width),
           "y": -random.randint(50, 300)} for _ in range(stone_count)]

# Game variables
DEADZONE = 20
dodged_stones = 50
game_over = False
paused = False

# Default MPU values
joyX, joyY, button = 512, 512, 1

def reset_game():
    global player_x, player_y, stones, dodged_stones, game_over, paused
    player_x, player_y = win_width // 2, win_height - 50
    stones[:] = [{"x": random.randint(0, win_width - stone_width),
                  "y": -random.randint(50, 300)} for _ in range(stone_count)]
    dodged_stones = 50
    game_over = False
    paused = False

# ------------------
# Main Game Loop
# ------------------
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_p:
                paused = not paused

    # Read Bluetooth Data
    try:
        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                parts = line.split(',')
                if len(parts) == 3:
                    joyX, joyY, button = map(int, parts)
    except serial.SerialException:
        print("⚠️ Lost connection to Bluetooth")
        running = False

    # Update Player
    if not paused and not game_over:
        move_x = ((joyX - 512) / 512) * 7 if abs(joyX - 512) > DEADZONE else 0
        move_y = ((joyY - 512) / 512) * 7 if abs(joyY - 512) > DEADZONE else 0

        player_x += move_x
        player_y += move_y

        # Keep inside window
        player_x = max(player_radius, min(win_width - player_radius, player_x))
        player_y = max(player_radius, min(win_height - player_radius, player_y))

        # Move stones
        for stone in stones:
            stone["y"] += stone_speed
            if stone["y"] > win_height:
                stone["y"] = -random.randint(50, 300)
                stone["x"] = random.randint(0, win_width - stone_width)
                dodged_stones -= 1
                if dodged_stones <= 0:
                    game_over = True

            # Collision detection
            if (player_x - player_radius < stone["x"] + stone_width and
                player_x + player_radius > stone["x"] and
                player_y - player_radius < stone["y"] + stone_height and
                player_y + player_radius > stone["y"]):
                game_over = True

    # Draw
    win.fill(WHITE)
    if game_over:
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over! Press R to restart", True, RED)
        win.blit(text, (win_width//2 - text.get_width()//2, win_height//2 - text.get_height()//2))
    else:
        pygame.draw.circle(win, GREEN, (int(player_x), int(player_y)), player_radius)
        for stone in stones:
            pygame.draw.rect(win, RED, (stone["x"], stone["y"], stone_width, stone_height))
        font = pygame.font.Font(None, 36)
        text = font.render(f"Stones left: {dodged_stones}", True, BLACK)
        win.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

# Cleanup
ser.close()
pygame.quit()
sys.exit()
