# Cannon Game  
Interactive artillery game built in Python using the **Kivy** framework, showcasing event-driven programming, modular architecture, and real-time physics simulation.


## Description
The **Cannon Game** is a single-player artillery game where the player must hit all moving targets across three progressively challenging levels.  
The player controls a rotating cannon that can fire **three different projectiles** — each with distinct physical properties (bullet, bombshell, laser).  
Obstacles such as **rocks, mirrors, wormholes, and perpetios** add complexity by deflecting, teleporting, or blocking projectiles.  

Gameplay combines **strategic decision-making** (choosing projectile type, adjusting angle and velocity) with **real-time physics simulation**.  
If the player loses, their score is saved in the **Hall of Fame**, displayed via a scrollable popup.  


## Key Features
- **Three gameplay levels** with increasing difficulty  
- **Three projectile types** with distinct physics  
- **Dynamic obstacles** (reflection, teleportation, destruction)  
- **Real-time physics simulation** (gravity, inertia, collisions)  
- **Scoring system + Hall of Fame leaderboard**  
- **Auxiliary features**:
  - Help screen  
  - Show trajectory (with time limit and score penalty)  
  - Level reset (with score penalty)  
  - Projectile selection menu  
- **Object-Oriented modular architecture**  
- **Event-driven updates** (via Kivy’s `Clock.schedule_interval`)  


## Project Structure
| Module | Description |
|---------|--------------|
| **main.py** | Central controller managing UI, gameplay loop, state transitions, collisions, and level progression. |
| **cannon.py** | Handles cannon rotation, rendering, and projectile launching position. |
| **projectiles.py** | Defines behavior of bullets, bombshells, and lasers — including gravity, speed, and special effects. |
| **obstacles.py** | Manages all obstacles (rocks, mirrors, wormholes, perpetios) and their interactions with projectiles. |
| **target.py** | Represents targets that move and can be destroyed to score points. |
| **assets/** | Contains all graphical resources (backgrounds, buttons, cannon, obstacles, etc.). |
| **hall_of_fame.txt** | Stores player nicknames and scores, updated after each game. |


## Libraries and Frameworks
- **Python 3.12** — main programming language  
- **Kivy** — for UI creation, rendering, and event-driven logic  
- **Math module** — for physics and trigonometric calculations  


## Controls
| Key / Button | Action |
|---------------|--------|
| ⬅️ / ➡️ | Adjust cannon angle |
| ⬆️ / ⬇️ | Adjust projectile velocity |
| Spacebar | Shoot |
| **Help** | Show gameplay instructions |
| **Select Projectile** | Choose bullet, bombshell, or laser |
| **Reset** | Restart level (−15 points) |
| **Show Trajectory** | Display predicted path for 15 s (−10 points) |


## Gameplay Flow
1. Enter nickname → Main Menu → Play  
2. Select projectile type → Start level  
3. Adjust cannon angle and velocity → Shoot  
4. Avoid or use obstacles strategically  
5. Clear all targets to advance to the next level  
6. After Level 3 → Win screen and Hall of Fame update  


## Conclusion
This project demonstrates the use of **object-oriented programming**, **event-driven systems**, and **real-time simulation** within a game environment.  
It highlights principles of **software modularity, debugging, and physics modeling**, providing a strong foundation for more advanced interactive systems.


## Report
For full design, implementation, and detailed module explanation, see the [complete report](./report.pdf).
