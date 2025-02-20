# HoodTag

## Overview
HoodTag is an interactive laser tag game designed to bring excitement to desk-bound evenings. The system consists of a laser gun powered by a Raspberry Pi Pico W and a target board with light-sensitive elements. These components communicate via Wi-Fi to track hits and manage the gameplay.
<p align="center">
  <img src="https://github.com/user-attachments/assets/119fd0ba-ec45-4e45-9155-8fcce7e77111" width="300">
</p>


## How It Works
HoodTag operates using a client-server model:
- **The Target Board (Server)**: This is a wooden hexagonal board embedded with active light sensors (photoresistors) and calibration sensors to adjust for ambient lighting conditions. It also includes LED rings to highlight targets and a buzzer for sound effects. The Raspberry Pi Pico W controls the board, processes hits, and displays scores on an OLED screen.
<p align="center">
  <img src="https://github.com/user-attachments/assets/6198f3df-d59c-4dc6-89a6-5809401869e4" width="535">
  <img src="https://github.com/user-attachments/assets/763ab129-2d31-446d-8a87-996e4defae83" width="300">
</p>

- **The Laser Gun (Client)**: A modified toy gun houses another Raspberry Pi Pico W, a laser diode, a trigger switch, and a buzzer. It connects to the target board via Wi-Fi and sends laser shots when triggered. An OLED screen on the gun provides real-time game feedback.
<p align="center">
  <img src="https://github.com/user-attachments/assets/adc43661-c83a-4ce4-9d8f-cf76d40ea0e9" width="300">
</p>


## Gameplay
1. The target board initializes and lights up a random target.
2. The player aims and shoots using the laser gun.
3. If the laser beam hits an active target within the given timeframe, the player scores a point.
4. The game continues for 10 to 30 rounds, with three difficulty modes:
   - **Easy**: Longer reaction time.
   - **Medium**: Balanced reaction time.
   - **Hard**: Shorter reaction time.
5. The system records game data and can replay previous rounds.

## Hardware Components
- **Raspberry Pi Pico W** (x2)
- **Laser Diode** (5mW)
- **Light Sensors** (Photoresistors x40)
- **LED Rings** (x5)
- **OLED Displays** (x2)
- **Buzzers** (x2)
- **End Switches, Resistors, and Power Modules**
- **Battery Packs (3xAA)**

## Setup & Connection
1. **Power the Devices**: Insert batteries into both the target board and laser gun.
2. **Wi-Fi Connection**: The target board acts as a server, and the gun connects as a client.
3. **Start the Game**: The OLED display on the target board will guide the setup.
4. **Playing**: Follow on-screen prompts and aim for the illuminated targets.

Simplified expamples of connecting both devices (comments in PL) are as below:

**Laser gun:**
<p align="center">
  <img src="https://github.com/user-attachments/assets/3a15730d-0e22-4ec2-8429-c55279be1a07" width="900">
</p>

**Board:**
<p align="center">
  <img src="https://github.com/user-attachments/assets/40e3fd74-060d-41b4-9480-7a00d0eeef24" width="900">
</p>

HoodTag is an engaging project that blends hardware, software, and interactive gaming into a fun, skill-based experience.

