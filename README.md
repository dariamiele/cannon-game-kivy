# The Cannon Game

2D physics-based artillery game developed in **Python** using the **Kivy framework**.

Final Exam Project for  
**Computer Programming, Algorithms and Data Structures**  
Academic Year 2023/2024

---

##  Project Overview

The Cannon Game is a 2D artillery game where the player must hit a randomly generated target using different types of projectiles.

The game is structured in **10 rounds of increasing difficulty**, where obstacles progressively alter projectile trajectories and require strategic thinking.

Each round allows a maximum of **five attempts**.  
If the target is not hit within those attempts, the game ends.  
If the player completes all 10 rounds, the final score is determined by the **total number of shots used**.

The goal is therefore to finish the game using as few shots as possible.

---

##  Game Mechanics

###  Core Elements

- Adjustable cannon (angle and velocity sliders)
- Random target generation each round
- Progressive obstacle system
- Physics-based projectile motion
- Maximum 5 attempts per round
- Win condition at Round 10
- Persistent Hall of Fame leaderboard
- Save/Load game progress

---

##  Projectile Types

Three projectile types with distinct physical behaviors:

### BULLET
- Affected by gravity
- Parabolic trajectory
- Limited impact radius

### BOMBSHELL
- Affected by gravity
- Larger explosion radius
- Can destroy rock obstacles

### LASER
- Not affected by gravity
- Linear motion
- Limited impulse duration
- Can reflect on mirrors

---

##  Obstacles

Four obstacle types increase difficulty across rounds:

### Rock
- Destructible
- Removed when hit

### Perpetio
- Indestructible
- Blocks projectiles

### Bulletproof Mirror
- Reflects lasers according to reflection laws
- May move in advanced rounds

### Elastonio
- Elastic surface
- Reflects bullets and bombs with restitution
- Absorbs lasers
- Can move vertically in later rounds

---

##  Physics Implementation

- Motion simulated in pixels and seconds
- Frame update at ~60 FPS using `Clock.schedule_interval`
- Gravity applied only to massive projectiles
- Laser uses constant velocity
- Reflection implemented via vector mathematics
- Collision detection:
  - Radius-based (bullet and bomb)
  - Bounding-box and center-point logic (laser)

---

##  Interface & Architecture

The game uses **Kivy’s ScreenManager** and follows a modular object-oriented design.

### Screens
- Welcome Screen
- Projectile Selection Screen
- Gameplay Screen
- Help Screen
- Hall of Fame Screen

### Additional Features
- JSON-based score storage
- Persistent leaderboard
- Save/Load progress system
- Adjustable sliders for angle and velocity
- Keyboard input (spacebar to shoot)

---

##  Tech Stack

- Python 3.12
- Kivy 2.3.0
- JSON (save/load & leaderboard)
- Math and Random (standard library)

---

## Author

Daria Miele

B.Sc. Artificial Intelligence

University of Milan / University of Milan-Bicocca / University of Pavia
