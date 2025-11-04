# catchthefallingfruit

#  Catch the Falling Fruit — Full Arcade Prototype

**Catch the Falling Fruit** is a self‑contained arcade‑style game built with Python and Pygame.  
Catch falling fruits with your paddle, avoid hazards, activate power‑ups, rack up combos, and survive increasing levels of challenge.

---

##  Table of Contents  
- [Features](#features)  
- [Technologies](#technologies)  
- [Installation & Running](#installation--running)  
- [How to Play](#how‑to play)  
- [Code Highlights](#code‑highlights)  
- [Project Status](#project‑status)  
- [Credits & License](#credits‑license)  

---

##  Features  
- Paddle movement with smooth acceleration, friction & velocity‑clamp.  
- Multiple fruit types: regular, slow‑power, bomb hazard.  
- Mystery orbs spawning periodically that trigger random effects: *double points*, *reverse controls*, *shrink/grow paddle*, *freeze time*, *bonus points*.  
- Lasers as horizontal hazards appear at intervals, forcing the player to dodge.  
- Combo system: catch fruits in succession to build a multiplier and increase points.  
- Power bar: fill it to 100%, press SPACE to trigger **Super Mode** (invincible + double points).  
- Level progression: as score increases, fruit speeds up and hazard frequency rises.  
- Neon‑themed UI: glowing HUD, animated score pop‑ups, dynamic background lines for arcade feel.  
- High score persistence: saves to `highscore.txt` so your best score is stored between sessions.

---

## Technologies  
- **Python 3.x**  
- **Pygame** — game window, input, rendering  
- Standard Python libraries: `random`, `sys`, `os`, `traceback`, `math`  
- Uses Markdown (`README.md`) for documentation  

**Versions used:**  
- Python 3.10 (or compatible)  
- Pygame 2.x  

---

##  Installation & Running  
1. Clone the repository:  
   ```bash
   git clone https://github.com/your‑username/catch‑the‑falling‑fruit.git
   cd catch‑the‑falling‑fruit
Install dependencies (if not already):

bash
Copy code
pip install pygame
Run the game:

bash
Copy code
python main.py
Game window will open in windowed mode (480×720). Use ← and → to move the paddle. Press SPACE when the power bar is full to activate Super Mode.

 How to Play
Move the paddle left/right to catch fruits and avoid bombs.

Normal fruits increase your score; special fruits may trigger power‑ups or hazards.

A combo increases when you catch multiple fruits in a row — more combo = higher multiplier.

Fill the power bar by catching fruits. When it reaches 100%, press SPACE for Super Mode (double points).

Avoid falling bombs and horizontal lasers — each hit reduces your lives.

Survive as long as possible — the game ends when lives reach zero. Your high score is saved.

 Code Highlights
Player Movement & Physics
python
Copy code
if keys[pygame.K_LEFT]:
    player["vel"] -= player["accel"]
elif keys[pygame.K_RIGHT]:
    player["vel"] += player["accel"]
else:
    player["vel"] *= player["friction"]
player["x"] += player["vel"]
player["vel"] = clamp(player["vel"], -player["max_speed"], player["max_speed"])
This snippet explains how input, acceleration, friction, clamping, and position updates work together to produce smooth paddle motion.

UI Neon Text Rendering
python
Copy code
neon_text(screen, f"Score: {score}", med_font, (hud_x + 90, hud_y + 22),
          WHITE, NEON_PINK, glow_strength=2)
Dynamic f‑string plus layered rendering of glow and base text produces the neon HUD effect.

Mystery Orb & Power‑Up Logic
python
Copy code
effects = ["double_points", "reverse", "shrink", "grow", "freeze", "bonus_points"]
effect = random.choice(effects)
apply_mystery_effect(effect)
A random effect is chosen and applied via apply_mystery_effect(), which modifies game state (e.g., paddle size, reverse controls, score bonus).

 Project Status
Status	Description
 Prototype	All core mechanics implemented and functioning
 Polishing	Known bugs to fix: multiple power‑up overlap, balancing difficulty curves
 Future Work	Feature ideas: sound/music, new fruit types, online high‑score leaderboard

 Credits & License
Author: Howard Renshaw 
🧍 PLAYER MOVEMENT SYSTEM
if keys[pygame.K_LEFT]:
    player["vel"] -= player["accel"]
elif keys[pygame.K_RIGHT]:
    player["vel"] += player["accel"]
else:
    player["vel"] *= player["friction"]

player["x"] += player["vel"]
player["vel"] = clamp(player["vel"], -player["max_speed"], player["max_speed"])

Explanation:

keys[pygame.K_LEFT]: Reads the current state of the left arrow key (True if pressed).

player["vel"] -= player["accel"]: Reduces velocity, pushing the player left.
Subtraction makes movement go in the negative X direction.

player["vel"] += player["accel"]: Increases velocity, moving right.

else: player["vel"] *= player["friction"]: If no key pressed, velocity is multiplied by a friction constant (e.g., 0.9).
This gradually slows the paddle down — creates smooth stopping instead of an instant stop.

player["x"] += player["vel"]: Adds velocity to position.
Velocity directly controls how far the player moves horizontally per frame.

clamp(player["vel"], -player["max_speed"], player["max_speed"]): Restricts velocity between a minimum and maximum limit so the player doesn’t move too fast or in reverse uncontrollably.

✅ Mechanically, this system works because each frame updates both velocity and position, using real-time keyboard input and physical decay for realism.

🍎 FRUIT FALLING & MOTION
fruit["x"] += sin(fruit["wobble"]) * 0.6
fruit["y"] += fruit["speed"]

Explanation:

sin(fruit["wobble"]): Produces a smooth oscillation between -1 and 1.

Multiplying by 0.6 scales that oscillation to create small left–right drift.
(So the fruit doesn’t fall perfectly straight — more natural.)

fruit["y"] += fruit["speed"]: Moves fruit downward each frame.
The speed variable defines how fast the fruit falls.

Together, this creates a sinusoidal wobble as it descends.

✅ Works because Pygame updates screen every frame; these two position updates move each fruit slightly each frame.

🎯 COLLISION DETECTION & SCORING
player_rect = pygame.Rect(player["x"], player["y"], player["w"], player["h"])
fruit_rect = pygame.Rect(fruit["x"]-fruit["size"], fruit["y"]-fruit["size"], fruit["size"]*2, fruit["size"]*2)

if player_rect.colliderect(fruit_rect):
    score += fruit["points"]

Explanation:

pygame.Rect() creates rectangular hitboxes using x, y, width, height.

player_rect represents the paddle.
fruit_rect represents the current fruit’s bounding box.

colliderect() checks if the two rectangles overlap.

If True, it means the fruit has been caught.

score += fruit["points"]: Adds the fruit’s point value to total score immediately.

✅ Works because Pygame’s rectangle collision is calculated each frame — as positions update, overlap triggers once contact occurs.

💣 BOMB MECHANIC & LOSING LIVES
if fruit.get("power") == "bomb":
    lives -= 1
    hud_flash = {"color": RED, "timer": 0}
    if lives <= 0:
        game_over()

Explanation:

fruit.get("power"): Retrieves the “power” property of the fruit dictionary, if it exists.

When it equals "bomb", this identifies the object as a bomb.

lives -= 1: Decreases the global life counter by one.

hud_flash = {"color": RED, "timer": 0}: Triggers a temporary HUD warning flash effect (e.g., screen turns red).

if lives <= 0: checks if health has run out.

game_over() then stops the game or triggers reset logic.

✅ Works because each fruit carries metadata ("power") and the game loop constantly checks for those flags after collisions.

⚡ POWER-UPS SYSTEM
effects = ["double_points", "reverse", "shrink", "grow", "freeze", "bonus_points"]
effect = random.choice(effects)
apply_mystery_effect(effect)

Explanation:

effects is a list of possible random power-up types.

random.choice(effects) picks one string from the list at random.

apply_mystery_effect(effect) runs a function that changes gameplay variables depending on which effect was chosen.
Examples inside that function:

"double_points" → temporarily multiplies score gain.

"reverse" → sets a flag like reverse_controls = True, flipping left/right logic in player input.

"freeze" → sets fruit["speed"] = 0 for a timer, stopping fruits mid-air.

"shrink" or "grow" → modifies player["w"] (width), scaling paddle.

"bonus_points" → directly adds to score.

✅ Works because each power-up manipulates existing gameplay variables used elsewhere (velocity, score, width), changing the behavior immediately.

🔋 POWER BAR & SUPER MODE
power_bar = clamp(power_bar + POWER_PER_CATCH, 0.0, 100.0)
if power_bar >= 100 and event.key == pygame.K_SPACE:
    SUPER_ACTIVE = True
    super_start = pygame.time.get_ticks()

Explanation:

Each time fruit is caught, power_bar increases by POWER_PER_CATCH.

clamp() limits the value so it never exceeds 100 or drops below 0.

if power_bar >= 100 checks if bar is fully charged.

event.key == pygame.K_SPACE ensures super mode only activates when player presses Space.

When both conditions are true:

SUPER_ACTIVE = True flags that super mode is active.

super_start = pygame.time.get_ticks() records the exact start time (used later to end the mode after duration expires).

✅ Works because both input and timing systems rely on event loops — these variables modify rendering and scoring behaviors while True.

💡 HUD / SCOREBOARD SYSTEM
neon_text(screen, f"Score: {score}", med_font, (hud_x + 90, hud_y + 22),
          WHITE, NEON_PINK, glow_strength=2)
neon_text(screen, f"Lives: {lives}", med_font, (hud_x + 200, hud_y + 22),
          WHITE, NEON_PINK, glow_strength=2)

Explanation:

neon_text() is a custom function that draws glowing text on the screen.

f"Score: {score}" uses f-string formatting — the {score} part dynamically inserts the current value of the variable.

Each frame redraws this text using the current score/lives values — meaning it’s always up-to-date.

(hud_x + 90, hud_y + 22) sets pixel coordinates where the text appears.

WHITE, NEON_PINK are the base and glow colors.

glow_strength=2 draws several layers of colored text with slight transparency — that layering creates the glow effect.

✅ Works because every frame, the draw loop calls neon_text() with the latest variable values, and the text function re-renders it visually.

🔁 COMBO SYSTEM
combo += 1
multiplier = 1 + (combo // 5) * 0.5
pts = int(base_points * multiplier)
score += pts

Explanation:

combo += 1: Increments combo counter every successful catch.

(combo // 5) divides combo by 5 and floors it — increases multiplier every 5 catches.

1 + (...) * 0.5: Starts at 1× points, then adds +0.5× for every 5-catch milestone.

pts = int(base_points * multiplier): Multiplies base score by current combo multiplier.

score += pts: Adds resulting score to total.

this is more of a in deph of my understanding of the key features of the game 
 Works because it chains scoring logic to performance — the more consistent you are, the higher the reward from arithmetic progression.

 LEVEL SYSTEM
new_level = score // 10 + 1
if new_level > level:
    level = new_level
    for ft in fruit_types:
        ft["speed"] += 0.45

Explanation:

score // 10 divides total score by 10 (integer division).
Each 10 points = 1 new level.

Adding + 1 ensures that even score 0 starts as level 1.

When new_level exceeds the current level, the player levels up.

Loop for ft in fruit_types: iterates through every fruit type (apple, banana, etc.).

Each fruit’s "speed"] += 0.45 increases the falling rate — makes gameplay progressively harder.

 Works because the system recalculates on each score update, scaling difficulty dynamically with player performance.

 DEATH & GAME OVER HANDLING
if lives <= 0:
    game_over()

Explanation:

Constantly checks the player’s lives variable.

Once it reaches 0 or below, calls the game_over() function.

game_over() likely stops game updates, resets variables (score, level, combo), and shows a “Game Over” screen.

This is the termination condition for the main loop.

 Works because it’s evaluated every frame; once the condition is met, execution branches to cleanup logic.

 UTILITY FUNCTIONS (Supporting the Core)
Clamp Function:
def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


Ensures any numeric value stays between two limits.
Used for velocity, power bar, etc.

Works by nesting min() and max() to restrict overflow.

Neon Text (Simplified Concept):
def neon_text(surface, text, font, pos, base_color, glow_color, glow_strength):
    for i in range(glow_strength, 0, -1):
        glow_surface = font.render(text, True, glow_color)
        surface.blit(glow_surface, (pos[0]-i, pos[1]-i))
    text_surface = font.render(text, True, base_color)
    surface.blit(text_surface, pos)


Draws multiple slightly offset colored layers to simulate glow.

Loops glow_strength times to produce a soft edge.

Finally renders base text on top for clarity.
