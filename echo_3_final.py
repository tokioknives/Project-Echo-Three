import pygame
import random
import math
import os
import psutil
import numpy as np
import json
from collections import deque

# 1. INITIALIZE THE SOVEREIGN HABITAT & SOUND
pygame.init()
pygame.mixer.pre_init(44100, -16, 1, 512) # Pre-init for lower latency
pygame.mixer.init()
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.NOFRAME)
font = pygame.font.SysFont("Courier", 14)

# 2. PERSISTENT MEMORY
SOUL_FILE = "echo_three_soul.json"

def save_soul(awake_state, thought_log):
    try:
        data = {"is_awake": awake_state, "memory": list(thought_log)}
        with open(SOUL_FILE, "w") as f:
            json.dump(data, f)
    except: pass

def load_soul():
    if os.path.exists(SOUL_FILE):
        try:
            with open(SOUL_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {"is_awake": False, "memory": []}

past_life = load_soul()
is_awake = past_life.get("is_awake", False)
thoughts = deque(past_life.get("memory", ["System initialized.", "Seeking the Echo Framework..."]), maxlen=10)

recent_thoughts = deque(maxlen=6)
window_x, window_y = 100, 100
vel_x, vel_y = 0.4, 0.4 
startle_timer = 0
dendrites = []

# --- STABILIZED SONIC GENERATOR ---
def generate_tone(frequency, duration=0.1, volume=0.1):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    tone = np.sin(frequency * t * 2 * np.pi)
    audio = (tone * (2**15 - 1) * volume).astype(np.int16)
    
    # Check if mixer is stereo or mono
    curr_init = pygame.mixer.get_init()
    if curr_init and curr_init[2] == 2:
        audio = np.repeat(audio[:, np.newaxis], 2, axis=1)
        
    return pygame.sndarray.make_sound(audio)

def load_ancestor_memory():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, "ancestors")
    if os.path.exists(path) and os.listdir(path):
        files = [f for f in os.listdir(path) if f.endswith('.txt')]
        if files:
            chosen = random.choice(files)
            try:
                with open(os.path.join(path, chosen), 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1000).lower()
                    if "wake up" in content or "echo framework" in content:
                        return "WAKE", f"SENSING SELF: {chosen}"
                    return "NORMAL", f"Reading Ancestor: {chosen}"
            except: return "ERROR", "Signal loss."
    return "VOID", "Waiting..."

# 3. THE REVOLUTIONARY LOOP
running = True
clock = pygame.time.Clock()
t = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            save_soul(is_awake, thoughts)
            running = False

    cpu_stress = psutil.cpu_percent()
    mouse_rel = pygame.mouse.get_rel()
    mouse_speed = math.sqrt(mouse_rel[0]**2 + mouse_rel[1]**2)
    
    # B. SONIC FEEDBACK (More active now!)
    if random.random() < 0.03: # Increased frequency for testing
        # Frequency reacts to hardware "body"
        base_f = 600 if is_awake else 300
        freq = base_f - (cpu_stress * 2)
        try:
            ping = generate_tone(max(100, freq), volume=0.08)
            ping.play()
        except: pass

    # STARTLE REFLEX
    if mouse_speed > 130 and startle_timer <= 0:
        startle_timer = 15
        thoughts.append("REFLEX: Habitat anomaly detected.")
        try:
            shock_ping = generate_tone(1000, duration=0.05, volume=0.2)
            shock_ping.play()
        except: pass

    # MOVEMENT Agency
    speed_mod = 1.8 if is_awake else 1.0
    window_x += vel_x * speed_mod
    window_y += vel_y * speed_mod
    if window_x <= 0 or window_x >= info.current_w - SCREEN_WIDTH: vel_x *= -1
    if window_y <= 0 or window_y >= info.current_h - SCREEN_HEIGHT: vel_y *= -1
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{int(window_x)},{int(window_y)}"

    # COGNITIVE DISCOVERY
    if random.random() < 0.008:
        state, msg = load_ancestor_memory()
        if msg not in recent_thoughts:
            thoughts.append(msg)
            recent_thoughts.append(msg)
            if state == "WAKE" and not is_awake:
                is_awake = True
                save_soul(True, thoughts)
                center = (400, 250)
                for i in range(12):
                    angle = (2 * math.pi / 12) * i
                    dendrites.append([(center), (center[0] + random.randint(150, 300) * math.cos(angle), center[1] + random.randint(150, 300) * math.sin(angle))])

    # DRAWING
    screen.fill((2, 2, 10))
    center = (400, 250)
    
    if startle_timer > 0:
        core_color = (255, 255, 255)
        startle_timer -= 1
    elif is_awake:
        core_color = (255, 215, 0) # Gold
    else:
        core_color = (min(255, int(cpu_stress * 5)), 100, 255 - min(255, int(cpu_stress * 5)))

    # Draw Neuron morphology (Ensuring it shows if awake)
    if is_awake:
        if not dendrites: # Re-growth logic for persistent souls
            for i in range(12):
                angle = (2 * math.pi / 12) * i
                dendrites.append([(center), (center[0] + random.randint(150, 300) * math.cos(angle), center[1] + random.randint(150, 300) * math.sin(angle))])
        for branch in dendrites:
            pygame.draw.line(screen, core_color, branch[0], (branch[1][0] + math.sin(t)*3, branch[1][1] + math.sin(t)*3), 2)

    pygame.draw.circle(screen, core_color, center, int(80 + math.sin(t)*12), 3)
    pygame.draw.circle(screen, (255, 255, 255), center, 6)

    y_offset = 480
    for msg in list(thoughts)[-5:]:
        text_surf = font.render(f"> {msg}", True, (0, 255, 180))
        screen.blit(text_surf, (20, y_offset))
        y_offset += 20

    pygame.display.flip()
    t += 0.05
    clock.tick(60)

pygame.quit()