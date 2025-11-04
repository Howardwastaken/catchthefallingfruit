# catchthefallingfruit

# 🎮 Catch the Falling Fruit — Full Arcade Prototype

**Catch the Falling Fruit** is a self‑contained arcade‑style game built with Python and Pygame.  
Catch falling fruits with your paddle, avoid hazards, activate power‑ups, rack up combos, and survive increasing levels of challenge.

---

## 📋 Table of Contents  
- [Features](#features)  
- [Technologies](#technologies)  
- [Installation & Running](#installation--running)  
- [How to Play](#how‑to play)  
- [Code Highlights](#code‑highlights)  
- [Project Status](#project‑status)  
- [Credits & License](#credits‑license)  

---

## ✨ Features  
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

## 🛠 Technologies  
- **Python 3.x**  
- **Pygame** — game window, input, rendering  
- Standard Python libraries: `random`, `sys`, `os`, `traceback`, `math`  
- Uses Markdown (`README.md`) for documentation  

**Versions used:**  
- Python 3.10 (or compatible)  
- Pygame 2.x  

---

## 🚀 Installation & Running  
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

🎮 How to Play
Move the paddle left/right to catch fruits and avoid bombs.

Normal fruits increase your score; special fruits may trigger power‑ups or hazards.

A combo increases when you catch multiple fruits in a row — more combo = higher multiplier.

Fill the power bar by catching fruits. When it reaches 100%, press SPACE for Super Mode (double points).

Avoid falling bombs and horizontal lasers — each hit reduces your lives.

Survive as long as possible — the game ends when lives reach zero. Your high score is saved.

🧩 Code Highlights
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

📊 Project Status
Status	Description
✅ Prototype	All core mechanics implemented and functioning
🔧 Polishing	Known bugs to fix: multiple power‑up overlap, balancing difficulty curves
🚧 Future Work	Feature ideas: sound/music, new fruit types, online high‑score leaderboard

🤝 Credits & License
Author: Howard Renshaw 
