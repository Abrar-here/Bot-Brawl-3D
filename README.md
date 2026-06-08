# 🎮 Bot Brawl 3D

Bot Brawl 3D is a Python-based 3D multiplayer combat game built using PyOpenGL. It features dynamic combat mechanics, AI-driven enemies, weapon systems, and a fully interactive arena environment.

---

## 🚀 Project Overview

Bot Brawl 3D is a fast-paced arena battle game where players fight enemies (and each other in multiplayer mode) using different weapons. The game focuses on real-time action, physics-based interactions, and simple but effective 3D rendering using OpenGL primitives.

---

## 🛠️ Technologies Used

- Python
- PyOpenGL
  - OpenGL
  - GLUT
  - GLU
- GLUT (for rendering and input handling)

---

## 🎯 Game Modes

- **Menu Mode**: Startup screen with game options
- **Single Player**: Fight waves of AI enemies
- **Multiplayer**: Two players battle locally
- **Game Over Screen**: Displays result and score

---

## 🧍 Player Mechanics

- Supports **two players**
- Movement:
  - Player 1: WASD
  - Player 2: Arrow keys
- Jumping:
  - W / Up Arrow
- Attacks:
  - Space / Mouse / Ctrl
- Weapon system:
  - Sword (melee attack)
  - Gun (projectile shooting)
  - Grenade (explosive AoE)

---

## 🤖 Enemy AI

- Random movement with basic targeting behavior
- Attempts to follow and attack players
- Platform-aware movement and jumping logic
- Simple animation (eyes blinking, wing movement)

---

## 🔫 Weapons & Projectiles

- Weapons spawn randomly on platforms
- Players can hold only one weapon at a time
- Weapon types:
  - **Sword** → Close-range melee damage
  - **Gun** → Fast straight-line bullets
  - **Grenade** → Physics-based projectile with explosion

---

## 💥 Explosions

- Triggered by grenades
- Area-of-effect damage system
- Visual expansion using transparency effects
- Affects both players and enemies within radius

---

## 🏗️ Arena & Platforms

- Fixed 3D arena layout
- Multiple platforms with different heights
- Collision detection for all entities
- Ground + elevated fighting zones

---

## 🎥 Camera System

- Smooth third-person dynamic camera
- Follows average position of active players
- Maintains gameplay visibility and balance

---

## 🎨 Visuals & UI

- Built using primitive 3D shapes (cubes, spheres, quads)
- Simple sky-blue background
- In-game HUD includes:
  - Health bars
  - Weapon status
  - Score & survival time
  - Control instructions
- Game Over screen:
  - Winner display
  - Restart/Exit options

---

## 🎮 Controls

| Action              | Player 1        | Player 2 (Multiplayer) |
|---------------------|----------------|------------------------|
| Move Left/Right     | A / D          | Left / Right Arrows    |
| Jump                | W              | Up Arrow               |
| Attack              | Space / Mouse  | Down Arrow             |
| Restart Game        | R              | R                      |
| Return to Menu      | Esc            | Esc                    |

---

## ⚙️ Game Logic Highlights

- All core logic handled inside a central `Game` class
- Timed spawning of enemies and weapons
- Sword attack uses angle-based hit detection
- Grenade explosion uses radial damage calculation
- OpenGL blending used for transparency effects
- Smooth physics-based movement system

---

## ⭐ Notable Features

- Local multiplayer support
- AI-based enemy behavior
- Multiple weapon system with pickup mechanics
- Real-time combat with physics interactions
- Smooth camera tracking system
- Visual feedback (damage flash, explosions)

---

## 📦 How to Run

Run the executable:
BotBrawl.exe
