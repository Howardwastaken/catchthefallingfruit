

import pygame
import random
import sys
import os
import traceback
from math import sin, pi

# -------------------------
# Configuration constants
# -------------------------
WIDTH, HEIGHT = 480, 720
FPS = 60
HIGH_SCORE_FILE = "highscore.txt"

# Timers (milliseconds)
LASER_INTERVAL = 8000      # spawn laser every 8s
LASER_DURATION = 1200      # laser active for 1.2s
MYSTERY_INTERVAL = 12000   # spawn mystery orb every 12s
SUPER_DURATION = 4000      # super mode lasts 4s
FREEZE_DURATION = 2000     # freeze time bonus duration
SCORE_POP_LIFETIME = 700   # ms

# -------------------------
# Helper functions
# -------------------------
def load_high_score(filename):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return int(f.read().strip() or 0)
        except:
            return 0
    return 0

def save_high_score(filename, score):
    try:
        with open(filename, "w") as f:
            f.write(str(score))
    except:
        pass

def neon_text(surface, text, font, center, base_color, glow_color, glow_strength=3):
    """Render glowing neon-like text by drawing layered 'glow' then base text."""
    for i in range(glow_strength, 0, -1):
        alpha = max(8, 80 - i * 18)
        glow_surf = font.render(text, True, glow_color)
        glow_surf.set_alpha(alpha)
        glow_rect = glow_surf.get_rect(center=center)
        surface.blit(glow_surf, glow_rect)
    base_surf = font.render(text, True, base_color)
    base_rect = base_surf.get_rect(center=center)
    surface.blit(base_surf, base_rect)

def clamp(v, a, b):
    return max(a, min(b, v))

# -------------------------
# Spawn helpers
# -------------------------
def spawn_fruit(width, fruit_types):
    f = random.choice(fruit_types)
    return {
        "x": random.randint(30, width - 30),
        "y": -random.randint(20, 160),
        "size": f["size"],
        "speed": f["speed"],
        "color": f["color"],
        "points": f["points"],
        "power": f.get("power", None),
        "wobble": random.random() * 2 * pi
    }

def spawn_mystery(width):
    return {
        "x": random.randint(40, width - 40),
        "y": -random.randint(30, 200),
        "size": 18,
        "speed": 3.5,
        "type": "mystery",  # handled specially
        "wobble": random.random() * 2 * pi
    }

def spawn_laser():
    # Horizontal laser beam spans width at random Y; short lifetime
    return {"y": random.randint(140, HEIGHT - 200), "start": pygame.time.get_ticks(), "active": True}

# -------------------------
# Main game
# -------------------------
def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Catch the Falling Fruit — Full Arcade")
    clock = pygame.time.Clock()

    # Neon palette
    BLACK = (6, 6, 10)
    NEON_PINK = (255, 64, 200)
    NEON_BLUE = (48, 200, 255)
    NEON_GREEN = (120, 255, 120)
    NEON_YELLOW = (255, 225, 60)
    NEON_ORANGE = (255, 140, 0)
    RED = (255, 60, 60)
    GRAY = (120, 120, 120)
    WHITE = (255, 255, 255)
    PURPLE = (160, 64, 240)

    # Fonts
    big_font = pygame.font.SysFont("Arial", 56, bold=True)
    med_font = pygame.font.SysFont("Arial", 28, bold=True)
    small_font = pygame.font.SysFont("Arial", 18, bold=True)

    # Player state (rect paddle)
    player = {"x": WIDTH // 2 - 30, "y": HEIGHT - 90, "w": 60, "h": 44,
              "vel": 0.0, "accel": 0.7, "max_speed": 9.0, "friction": 0.86,
              "base_w": 60, "base_h": 44}

    # Fruit types (shape-based)
    fruit_types = [
        {"color": NEON_PINK, "points": 1, "speed": 4.2, "size": 18},    # small apple
        {"color": NEON_YELLOW, "points": 2, "speed": 5.0, "size": 24},  # banana-like
        {"color": NEON_ORANGE, "points": 3, "speed": 6.0, "size": 28},  # orange-ish
        {"color": NEON_BLUE, "points": 5, "speed": 4.8, "size": 22, "power": "slow"},  # slow-power
        {"color": GRAY, "points": -1, "speed": 5.0, "size": 20, "power": "bomb"}       # bomb hazard
    ]

    # Save base speeds for reset
    for f in fruit_types:
        f["base_speed"] = f["speed"]

    # Initial fruit
    fruit = spawn_fruit(WIDTH, fruit_types)

    # Mystery orb
    mystery = None
    last_mystery = pygame.time.get_ticks()

    # Laser
    laser = None
    last_laser = pygame.time.get_ticks()

    # Background neon lines (parallax)
    bg_lines = []
    for i in range(24):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        length = random.randint(60, 180)
        speed = random.uniform(0.15, 0.6)
        color = NEON_BLUE if random.random() < 0.5 else NEON_PINK
        bg_lines.append([x, y, length, speed, color])

    # Game state variables
    score = 0
    lives = 3
    level = 1
    slow_mode = False
    slow_start = 0
    high_score = load_high_score(HIGH_SCORE_FILE)

    # Combo system
    combo = 0
    combo_timer = 0  # reset if miss or after some time
    COMBO_RESET_MS = 1800

    # Power bar (fills when catching fruits). When full, press SPACE for super mode.
    power_bar = 0.0
    POWER_PER_CATCH = 12.0   # percent points
    SUPER_ACTIVE = False
    super_start = 0

    # Mystery effect states
    reverse_controls = False
    reverse_until = 0
    freeze_time = False
    freeze_until = 0

    # Score pop animation
    pop_list = []  # each: {"x","y","text","start_time"}

    # HUD flash
    hud_flash = None  # {"color","timer"}

    # Title animation
    title_phase = 0.0

    # Game screens
    state = "menu"  # 'menu', 'playing', 'gameover'

    # Helpers
    def reset_game():
        nonlocal fruit, mystery, laser, score, lives, level, slow_mode, slow_start
        nonlocal combo, combo_timer, power_bar, SUPER_ACTIVE, super_start
        nonlocal reverse_controls, reverse_until, freeze_time, freeze_until, pop_list, hud_flash
        score = 0
        lives = 3
        level = 1
        slow_mode = False
        slow_start = 0
        fruit = spawn_fruit(WIDTH, fruit_types)
        mystery = None
        laser = None
        combo = 0
        combo_timer = 0
        power_bar = 0.0
        SUPER_ACTIVE = False
        super_start = 0
        reverse_controls = False
        reverse_until = 0
        freeze_time = False
        freeze_until = 0
        pop_list = []
        hud_flash = None
        # reset speeds
        for f in fruit_types:
            f["speed"] = f["base_speed"]

    # Utility to apply a mystery effect
    def apply_mystery_effect(effect):
        nonlocal score, hud_flash, reverse_controls, reverse_until, freeze_time, freeze_until, player
        if effect == "double_points":
            # temporarily double next point value via marking a pop
            hud_flash = {"color": NEON_YELLOW, "timer": 0}
            pop_list.append({"x": WIDTH/2, "y": HEIGHT/2, "text": "DOUBLE!", "start": pygame.time.get_ticks()})
            # We implement double points by adding a short window where SUPER-like double applied
            # Simpler: increase score immediately (bonus)
            score += 5
        elif effect == "reverse":
            reverse_controls = True
            reverse_until = pygame.time.get_ticks() + 5000
            hud_flash = {"color": PURPLE, "timer": 0}
            pop_list.append({"x": WIDTH/2, "y": HEIGHT/2, "text": "REVERSE!", "start": pygame.time.get_ticks()})
        elif effect == "shrink":
            # shrink player for challenge
            player["w"] = int(player["base_w"] * 0.6)
            player["h"] = int(player["base_h"] * 0.6)
            # restore after 6s
            pop_list.append({"x": WIDTH/2, "y": HEIGHT/2, "text": "SHRINK!", "start": pygame.time.get_ticks()})
            pygame.time.set_timer(pygame.USEREVENT + 5, 6000, loops=1)
        elif effect == "grow":
            player["w"] = int(player["base_w"] * 1.25)
            player["h"] = int(player["base_h"] * 1.25)
            pop_list.append({"x": WIDTH/2, "y": HEIGHT/2, "text": "GROW!", "start": pygame.time.get_ticks()})
            pygame.time.set_timer(pygame.USEREVENT + 6, 6000, loops=1)
        elif effect == "freeze":
            freeze_time = True
            freeze_until = pygame.time.get_ticks() + FREEZE_DURATION
            pop_list.append({"x": WIDTH/2, "y": HEIGHT/2, "text": "FREEZE!", "start": pygame.time.get_ticks()})
            hud_flash = {"color": NEON_BLUE, "timer": 0}
        elif effect == "bonus_points":
            bonus = random.randint(3, 8)
            score += bonus
            pop_list.append({"x": WIDTH/2, "y": HEIGHT/2, "text": f"+{bonus}", "start": pygame.time.get_ticks()})
            hud_flash = {"color": NEON_YELLOW, "timer": 0}

    # ----------------------
    # Main loop
    # ----------------------
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        now = pygame.time.get_ticks()
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score(HIGH_SCORE_FILE, high_score)
                pygame.quit()
                sys.exit()
            # Timed events for restoring player size
            if event.type == pygame.USEREVENT + 5:
                # restore from shrink
                player["w"] = player["base_w"]
                player["h"] = player["base_h"]
            if event.type == pygame.USEREVENT + 6:
                # restore from grow
                player["w"] = player["base_w"]
                player["h"] = player["base_h"]
            if event.type == pygame.KEYDOWN:
                if state == "menu":
                    reset_game()
                    state = "playing"
                elif state == "gameover":
                    reset_game()
                    state = "playing"
                elif state == "playing":
                    if event.key == pygame.K_SPACE:
                        # activate super if bar full
                        if power_bar >= 100 and not SUPER_ACTIVE:
                            SUPER_ACTIVE = True
                            super_start = pygame.time.get_ticks()
                            power_bar = 0.0
                            hud_flash = {"color": NEON_YELLOW, "timer": 0}
            # No other special events

        keys = pygame.key.get_pressed()

        # ----------------------
        # STATE: MENU
        # ----------------------
        if state == "menu":
            title_phase += dt * 2.4
            # Draw gradient background
            for y in range(HEIGHT):
                t = y / HEIGHT
                r = int(8 * (1 - t) + 28 * t)
                g = int(6 * (1 - t) + 20 * t)
                b = int(20 * (1 - t) + 40 * t)
                pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

            # Animated neon bars
            for i, line in enumerate(bg_lines):
                line[1] += line[3]
                if line[1] > HEIGHT + line[2]:
                    line[0] = random.randint(-80, WIDTH)
                    line[1] = -random.randint(20, 160)
                    line[2] = random.randint(60, 180)
                    line[3] = random.uniform(0.15, 0.6)
                    line[4] = NEON_BLUE if random.random() < 0.5 else NEON_PINK
                lx, ly, length, _, color = line
                pygame.draw.line(screen, color, (lx, ly), (lx, ly + length), 2)

            neon_text(screen, "CATCH THE FRUIT", big_font, (WIDTH // 2, HEIGHT // 2 - 90), WHITE, NEON_PINK, glow_strength=4)
            neon_text(screen, "Press any key to start", med_font, (WIDTH // 2, HEIGHT // 2 + 10), NEON_BLUE, NEON_BLUE, glow_strength=2)
            neon_text(screen, f"High Score: {high_score}", small_font, (WIDTH // 2, HEIGHT // 2 + 60), NEON_YELLOW, NEON_YELLOW, glow_strength=1)
            pygame.display.flip()
            continue

        # ----------------------
        # STATE: PLAYING
        # ----------------------
        if state == "playing":
            # Background subtle gradient
            for y in range(HEIGHT):
                t = y / HEIGHT
                r = int(6*(1 - t) + 18*t)
                g = int(8*(1 - t) + 18*t)
                b = int(20*(1 - t) + 36*t)
                pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

            # Update bg lines
            for i, line in enumerate(bg_lines):
                line[1] += line[3]
                if line[1] > HEIGHT + line[2]:
                    line[0] = random.randint(-80, WIDTH)
                    line[1] = -random.randint(20, 160)
                    line[2] = random.randint(60, 180)
                    line[3] = random.uniform(0.2, 0.7)
                    line[4] = NEON_BLUE if random.random() < 0.5 else NEON_PINK
                lx, ly, length, _, color = line
                pygame.draw.line(screen, color, (lx, ly), (lx, ly + length), 2)

            # Update lasers (spawn periodically)
            if not laser and now - last_laser > LASER_INTERVAL:
                laser = spawn_laser()
                last_laser = now
            if laser:
                if now - laser["start"] > LASER_DURATION:
                    laser = None

            # Update mystery orb spawns
            if not mystery and now - last_mystery > MYSTERY_INTERVAL:
                mystery = spawn_mystery(WIDTH)
                last_mystery = now

            # Movement input (account for reverse_controls)
            left_pressed = keys[pygame.K_LEFT]
            right_pressed = keys[pygame.K_RIGHT]
            if reverse_controls:
                left_pressed, right_pressed = right_pressed, left_pressed

            if left_pressed:
                player["vel"] -= player["accel"]
            elif right_pressed:
                player["vel"] += player["accel"]
            else:
                player["vel"] *= player["friction"]

            # clamp velocity
            player["vel"] = clamp(player["vel"], -player["max_speed"], player["max_speed"])
            player["x"] += player["vel"]
            # bounds
            if player["x"] < 6:
                player["x"] = 6
                player["vel"] = 0
            if player["x"] > WIDTH - player["w"] - 6:
                player["x"] = WIDTH - player["w"] - 6
                player["vel"] = 0

            # Freeze time effect stops fruit/laser/mystery movement
            time_frozen = freeze_time and now < freeze_until

            # Fruit physics
            if not time_frozen:
                speed_mod = 0.55 if slow_mode else 1.0
                fruit["wobble"] += 0.06
                fruit["x"] += sin(fruit["wobble"]) * 0.6
                fruit["y"] += fruit["speed"] * speed_mod

            # Mystery physics
            if mystery and not time_frozen:
                mystery["wobble"] += 0.06
                mystery["x"] += sin(mystery["wobble"]) * 0.6
                mystery["y"] += mystery["speed"]

            # Laser collision check (if active)
            if laser and not time_frozen:
                # Laser represented as a thick horizontal beam; touching it costs a life
                laser_rect = pygame.Rect(0, laser["y"] - 8, WIDTH, 16)
                player_rect = pygame.Rect(int(player["x"]), int(player["y"]), player["w"], player["h"])
                if player_rect.colliderect(laser_rect):
                    # hit laser: lose a life and flash HUD
                    lives -= 1
                    hud_flash = {"color": RED, "timer": 0}
                    # remove laser to avoid multiple hits
                    laser = None

            # Collision detection with fruit
            player_rect = pygame.Rect(int(player["x"]), int(player["y"]), player["w"], player["h"])
            fruit_rect = pygame.Rect(int(fruit["x"] - fruit["size"]), int(fruit["y"] - fruit["size"]),
                                     fruit["size"] * 2, fruit["size"] * 2)
            collided = False
            if player_rect.colliderect(fruit_rect):
                collided = True
                # handle power types
                if fruit.get("power") == "slow":
                    slow_mode = True
                    slow_start = now
                    hud_flash = {"color": NEON_BLUE, "timer": 0}
                elif fruit.get("power") == "bomb":
                    # bomb subtracts a life
                    lives -= 1
                    hud_flash = {"color": RED, "timer": 0}
                    # negative points penalty optional
                else:
                    # normal fruit: calculate points with combo and super
                    base_points = fruit.get("points", 1)
                    # increment combo
                    combo += 1
                    combo_timer = now
                    # calculate multiplier from combo
                    multiplier = 1 + (combo // 5) * 0.5  # +0.5 every 5 chain
                    if SUPER_ACTIVE:
                        multiplier *= 2.0
                    pts = int(base_points * multiplier)
                    score += pts
                    pop_list.append({"x": fruit["x"], "y": fruit["y"] - 6, "text": f"+{pts}", "start": now})
                    hud_flash = {"color": NEON_GREEN, "timer": 0}
                    # power bar fill
                    power_bar = clamp(power_bar + POWER_PER_CATCH, 0.0, 100.0)

                # Respawn fruit
                fruit = spawn_fruit(WIDTH, fruit_types)

                # Level scaling every 10 points
                new_level = score // 10 + 1
                if new_level > level:
                    level = new_level
                    for ft in fruit_types:
                        ft["speed"] += 0.45

            # If fruit missed (falls beyond bottom)
            if fruit["y"] > HEIGHT + fruit["size"]:
                lives -= 1
                hud_flash = {"color": RED, "timer": 0}
                fruit = spawn_fruit(WIDTH, fruit_types)
                # reset combo on miss
                combo = 0
                combo_timer = 0

            # Mystery collision
            if mystery:
                mystery_rect = pygame.Rect(int(mystery["x"] - mystery["size"]), int(mystery["y"] - mystery["size"]),
                                           mystery["size"] * 2, mystery["size"] * 2)
                if player_rect.colliderect(mystery_rect):
                    # pick random effect
                    effects = ["double_points", "reverse", "shrink", "grow", "freeze", "bonus_points"]
                    effect = random.choice(effects)
                    apply_mystery_effect(effect)
                    mystery = None

                # if missed -> disappear
                if mystery and mystery["y"] > HEIGHT + mystery["size"]:
                    mystery = None

            # Super mode expiration
            if SUPER_ACTIVE and now - super_start > SUPER_DURATION:
                SUPER_ACTIVE = False

            # slow mode expiration
            if slow_mode and now - slow_start > 3500:
                slow_mode = False

            # reverse controls expiration
            if reverse_controls and now > reverse_until:
                reverse_controls = False

            # freeze expiration
            if freeze_time and now > freeze_until:
                freeze_time = False

            # Combo timeout
            if combo > 0 and now - combo_timer > COMBO_RESET_MS:
                combo = 0

            # HUD flash timer
            if hud_flash:
                hud_flash["timer"] += 1
                if hud_flash["timer"] > 18:
                    hud_flash = None

            # Score pop animations update: fade & rise
            for pop in pop_list[:]:
                elapsed = now - pop["start"]
                if elapsed > SCORE_POP_LIFETIME:
                    pop_list.remove(pop)
                else:
                    pop["y"] -= 30 * dt  # float upward

            # Laser lifetime removal handled earlier

            # Spawn new mystery item periodically handled earlier

            # Draw player with neon glow
            for i in range(4, 0, -1):
                glow_rect = pygame.Rect(int(player["x"] - i*2), int(player["y"] - i*1.2),
                                        player["w"] + i*4, player["h"] + i*2)
                g = pygame.Surface((glow_rect.w, glow_rect.h), pygame.SRCALPHA)
                alpha = int(28 / i)
                g.fill((NEON_PINK[0], NEON_PINK[1], NEON_PINK[2], max(0, alpha)))
                screen.blit(g, (glow_rect.x, glow_rect.y))
            pygame.draw.rect(screen, NEON_PINK, (int(player["x"]), int(player["y"]), player["w"], player["h"]), border_radius=6)
            pygame.draw.rect(screen, WHITE, (int(player["x"])+8, int(player["y"])+12, player["w"]-16, player["h"]-24), 2, border_radius=4)

            # Draw fruit with shapes
            if fruit.get("power") == "bomb":
                pygame.draw.circle(screen, GRAY, (int(fruit["x"]), int(fruit["y"])), fruit["size"])
                pygame.draw.line(screen, RED, (fruit["x"]-fruit["size"], fruit["y"]-fruit["size"]),
                                 (fruit["x"]+fruit["size"], fruit["y"]+fruit["size"]), 4)
                pygame.draw.line(screen, RED, (fruit["x"]+fruit["size"], fruit["y"]-fruit["size"]),
                                 (fruit["x"]-fruit["size"], fruit["y"]+fruit["size"]), 4)
            elif fruit.get("power") == "slow":
                pulse = 1.0 + 0.12 * sin(pygame.time.get_ticks() / 140.0)
                r = int(fruit["size"] * pulse)
                glow_s = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
                pygame.draw.circle(glow_s, (NEON_BLUE[0], NEON_BLUE[1], NEON_BLUE[2], 60),
                                   (r*2, r*2), int(r*1.8))
                screen.blit(glow_s, (int(fruit["x"] - r*2), int(fruit["y"] - r*2)))
                pygame.draw.circle(screen, NEON_BLUE, (int(fruit["x"]), int(fruit["y"])), r)
                pygame.draw.circle(screen, WHITE, (int(fruit["x"]), int(fruit["y"])), max(3, r-6), 2)
            else:
                pygame.draw.circle(screen, fruit["color"], (int(fruit["x"]), int(fruit["y"])), fruit["size"])
                pygame.draw.ellipse(screen, WHITE, (fruit["x"] - fruit["size"] // 2, fruit["y"] - fruit["size"] // 1.6,
                                                   fruit["size"]//2, fruit["size"]//3))

            # Draw mystery orb if exists (neon star-like)
            if mystery:
                msize = mystery["size"]
                # pulsing glow
                pulse = 1.0 + 0.18 * sin(pygame.time.get_ticks() / 180.0)
                r = int(msize * pulse)
                glow = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
                pygame.draw.circle(glow, (NEON_YELLOW[0], NEON_YELLOW[1], NEON_YELLOW[2], 80),
                                   (r*2, r*2), int(r*1.8))
                screen.blit(glow, (int(mystery["x"] - r*2), int(mystery["y"] - r*2)))
                pygame.draw.circle(screen, NEON_YELLOW, (int(mystery["x"]), int(mystery["y"])), r)
                pygame.draw.circle(screen, WHITE, (int(mystery["x"]), int(mystery["y"])), max(3, r-6), 2)

            # Draw laser beam (if active)
            if laser:
                # neon horizontal beam with glow
                y = laser["y"]
                beam_surf = pygame.Surface((WIDTH, 18), pygame.SRCALPHA)
                beam_surf.fill((255, 40, 40, 160))
                screen.blit(beam_surf, (0, y - 9))
                # thin bright center
                pygame.draw.line(screen, RED, (0, y), (WIDTH, y), 3)

            # HUD drawing (score, lives, level, power bar, combo)
            hud_x = 12
            hud_y = 12
            # HUD glow base
            if hud_flash:
                glow_color = hud_flash["color"]
            else:
                glow_color = NEON_YELLOW
            for i in range(6, 0, -1):
                alpha = 14 - i*2
                rect = pygame.Rect(-i*2 + hud_x, -i + hud_y, 240 + i*4, 78 + i*2)
                gsurf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                gsurf.fill((glow_color[0], glow_color[1], glow_color[2], max(0, alpha)))
                screen.blit(gsurf, (rect.x, rect.y))
            # HUD container
            hud_rect = pygame.Rect(hud_x, hud_y, 240, 78)
            pygame.draw.rect(screen, (12, 12, 18, 220), hud_rect, border_radius=8)
            # Score and lives
            neon_text(screen, f"Score: {score}", med_font, (hud_x + 90, hud_y + 22), WHITE, NEON_PINK, glow_strength=2)
            neon_text(screen, f"Lives: {lives}", small_font, (hud_x + 90, hud_y + 52), WHITE, NEON_GREEN, glow_strength=1)
            neon_text(screen, f"Level: {level}", small_font, (WIDTH - 80, 26), WHITE, NEON_YELLOW, glow_strength=2)
            neon_text(screen, f"High: {high_score}", small_font, (WIDTH - 80, 52), WHITE, NEON_YELLOW, glow_strength=1)

            # power bar drawn on HUD
            bar_x, bar_y = WIDTH - 180, 84
            pygame.draw.rect(screen, (8, 8, 12, 220), (bar_x, bar_y - 10, 148, 12), border_radius=6)
            # fill percent
            pygame.draw.rect(screen, NEON_BLUE, (bar_x + 4, bar_y - 8, int((power_bar/100.0) * 140), 8), border_radius=4)
            neon_text(screen, "POWER", small_font, (bar_x + 70, bar_y + 4), WHITE, NEON_BLUE, glow_strength=1)
            # combo display
            if combo >= 2:
                neon_text(screen, f"Combo x{1 + (combo//5)*0.5:.1f}", small_font, (WIDTH//2, 44), WHITE, NEON_PINK, glow_strength=2)

            # Super indicator
            if SUPER_ACTIVE:
                neon_text(screen, "SUPER!", med_font, (WIDTH//2, 84), NEON_YELLOW, NEON_YELLOW, glow_strength=3)

            # Draw pop_list floating texts
            for pop in pop_list:
                elapsed = now - pop["start"]
                alpha = clamp(255 - int(255 * (elapsed / SCORE_POP_LIFETIME)), 0, 255)
                surf = med_font.render(pop["text"], True, NEON_GREEN)
                surf.set_alpha(alpha)
                screen.blit(surf, (int(pop["x"] - surf.get_width() // 2), int(pop["y"] - surf.get_height() // 2)))

            # Update high score dynamically
            if score > high_score:
                high_score = score

            # End condition
            if lives <= 0:
                # save HS and go to gameover
                save_high_score(HIGH_SCORE_FILE, high_score)
                state = "gameover"

        # ----------------------
        # STATE: GAMEOVER
        # ----------------------
        if state == "gameover":
            # stylized game over display
            time_ms = pygame.time.get_ticks()
            for y in range(HEIGHT):
                t = y / HEIGHT
                r = int(4*(1 - t) + 16 * t)
                g = int(6*(1 - t) + 12 * t)
                b = int(10*(1 - t) + 28 * t)
                pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
            # neon bars
            for i in range(12):
                offset = (time_ms / 4 + i * 45) % (WIDTH + 200) - 100
                color = NEON_PINK if i % 2 == 0 else NEON_BLUE
                pygame.draw.rect(screen, color, (offset, HEIGHT//2 + i*6 - 160, 80, 3))

            neon_text(screen, "GAME OVER", big_font, (WIDTH // 2, HEIGHT // 2 - 60), WHITE, NEON_PINK, glow_strength=5)
            neon_text(screen, f"Score: {score}", med_font, (WIDTH // 2, HEIGHT // 2 + 10), NEON_YELLOW, NEON_YELLOW, glow_strength=3)
            neon_text(screen, f"High Score: {high_score}", small_font, (WIDTH // 2, HEIGHT // 2 + 64), WHITE, NEON_YELLOW, glow_strength=2)
            neon_text(screen, "Press any key to play again", small_font, (WIDTH // 2, HEIGHT // 2 + 120), NEON_BLUE, NEON_BLUE, glow_strength=2)

        # Flip the display
        pygame.display.flip()

    # end main loop

# Entry point
if __name__ == "__main__":
    try:
        run_game()
    except Exception:
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)


