# Armillary Sphere

A real-time, motorized celestial body tracking system that integrates an Arduino-driven touchscreen interface, servo and stepper motor positioning, and a laser pointer, combined with NASA's JPL Horizons API for precise astronomical orientation.

This system displays real-time azimuth and elevation of planets and moons—and **physically aims a laser pointer** at their live position in the sky.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Motorized Tracking System](#motorized-tracking-system)
- [Available Celestial Objects](#available-celestial-objects)
- [Project Structure](#project-structure)
- [System Architecture](#system-architecture)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Armillary Sphere is an interactive, automated object-pointing system designed for astronomy education and experimentation. Users select celestial objects on a touchscreen, and the system:

1. **Obtains** real-time astronomical coordinates from NASA JPL Horizons
2. **Converts** azimuth/elevation into mechanical motion commands
3. **Positions** a stepper motor (yaw) and servo motor (pitch)
4. **Aims** a laser pointer at the live sky location of the selected object

The device uses robust **bidirectional serial communication** between Arduino and a Python backend, providing real-time positional data and smooth motor control.

---

## Features

### 🖐️ Touchscreen Object Selection
Choose from 24 celestial objects including planets, moons, and dwarf planets with an intuitive touch interface.

### 🌐 Location-Aware Tracking
Automatic IP-based geolocation ensures coordinate accuracy for your specific viewing location.

### 🛰️ NASA JPL Horizons API Integration
Fetches precise azimuth and elevation data for any object in real time, accounting for Earth's rotation and orbital mechanics.

### 🔄 Full Motorized Tracking
- **Stepper motor** controls yaw (azimuth 0°–360°)
- **Servo motor** controls pitch (elevation −90° to +90°)
- Automatically orients toward the selected target

### 🔦 Laser Pointer Object Indicator
The laser physically points in the direction of the selected object, making it easy to locate celestial bodies in the night sky.

### ↔️ Bidirectional Serial Communication
Arduino requests object coordinates; Python responds with live data in a simple, robust protocol.

### 📟 Live Display on TFT Screen
View coordinates, menu pages, and selection interface directly on the Arduino-connected display.

---

## Hardware Requirements

### Microcontroller & Display

| Component | Specification |
|-----------|---------------|
| **Microcontroller** | Arduino Uno or compatible ATmega328P board |
| **Display** | 320×240 TFT Touchscreen Display (MCUFRIEND_kbv-compatible) |
| **Touch Panel** | 4-wire resistive touch panel |

### Actuation System

#### Stepper Motor (Yaw / Azimuth)
- **Option 1:** 28BYJ-48 with ULN2003 driver
- **Option 2:** NEMA 17 with A4988 or DRV8825 driver

#### Servo Motor (Pitch / Elevation)
- Recommended: SG90, MG90S, or MG995
- Must support standard PWM control (50Hz, 1-2ms pulse width)

#### Laser Module
- Standard 5V laser diode module
- Power: ~30-50mA typical
- Safety: Use appropriate laser safety class (Class 2 recommended)

### Pin Configuration

#### Touchscreen Connections
```
XP (X+) : Digital Pin 8  
XM (X-) : Analog Pin A2  
YP (Y+) : Analog Pin A3  
YM (Y-) : Digital Pin 9  
```

#### Motor Connections (Example - Adjust Based on Your Setup)
```
Stepper Motor:
  IN1-IN4 : Digital Pins 2-5 (for ULN2003)
  
Servo Motor:
  Signal  : Digital Pin 6 (PWM)
  
Laser Module:
  Control : Digital Pin 7
```

### Power Requirements
- **5V Power Supply:** 2A minimum (for Arduino, display, and servo)
- **12V Power Supply:** 1A minimum (if using NEMA 17 stepper)
- Ensure common ground between all power supplies

---

## Software Requirements

### Arduino

- **Arduino IDE** 1.8.x or later
- **Required Libraries:**
  - `Adafruit_GFX` - Graphics library
  - `MCUFRIEND_kbv` - TFT display driver
  - `TouchScreen` - Resistive touch panel
  - `Servo` - Built-in Arduino servo library
  - _(Optional)_ `AccelStepper` - For advanced stepper control

**Install libraries via Arduino IDE:**
```
Sketch → Include Library → Manage Libraries
Search for each library and click "Install"
```

### Python

- **Python** 3.7 or later
- **Required Packages:**
  ```bash
  pip install requests pyserial numpy
  ```

#### Package Details
- `requests` - HTTP library for NASA API calls
- `pyserial` - Serial communication with Arduino
- `numpy` - Numerical computations

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/IEEE-QP.git
cd IEEE-QP
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install requests pyserial numpy
```

### 3. Arduino Setup

1. Open `arduino/combined_control.ino` in Arduino IDE
2. Install required libraries (see [Software Requirements](#software-requirements))
3. **Verify pin configurations** match your hardware setup
4. Select your board: `Tools → Board → Arduino Uno`
5. Select your port: `Tools → Port → COM# (or /dev/ttyUSB#)`
6. Click **Upload** ⬆️

### 4. Configure Serial Port in Python

Edit `PlanetaryObjectsFetcher.py` to match your Arduino's serial port:

**Windows:**
```python
ser = serial.Serial(
    port='COM6',      # Change to your COM port
    baudrate=9600,
    timeout=1
)
```

**Linux/Mac:**
```python
ser = serial.Serial(
    port='/dev/ttyUSB0',  # or /dev/ttyACM0
    baudrate=9600,
    timeout=1
)
```

💡 **Tip:** Find your port in Arduino IDE under `Tools → Port`

---

## Usage

### Quick Start

1. **Power on** your Arduino and ensure all connections are secure
2. **Upload** the Arduino sketch if not already done
3. **Run** the Python backend:
   ```bash
   python PlanetaryObjectsFetcher.py
   ```
4. **On the touchscreen:**
   - Tap to select celestial objects
   - Use **Prev/Next** buttons to navigate pages
   - Watch as the system automatically moves motors and activates the laser

### Serial Communication Protocol

The system uses a simple text-based protocol over serial:

#### Arduino → Python (Request)
```
STAR:Moon
```
Format: `STAR:<ObjectName>`

#### Python → Arduino (Response)
```
131.587713,38.069515
```
Format: `<azimuth_degrees>,<elevation_degrees>`

#### Error Handling
- If object not found or API fails, Python sends: `ERROR:message`
- Arduino displays error on screen and maintains last valid position

---

## Motorized Tracking System

The Armillary Sphere includes a fully automated pointing mechanism designed to physically track celestial objects in real time.

### Yaw Control (Stepper Motor)

**Responsible for:** Azimuth rotation (0°–360°)

**How it works:**
- Arduino receives target azimuth from Python
- Converts degrees to motor steps: `steps = (azimuth / 360) * steps_per_revolution`
- Rotates stepper motor to target position
- Supports smooth directional motion (always takes shortest path)

**Typical Configuration:**
- 28BYJ-48: 2048 steps per revolution (with gearing)
- NEMA 17: 200 steps per revolution (1.8° per step)

### Pitch Control (Servo Motor)

**Responsible for:** Elevation angle (−90° to +90°)

**How it works:**
- Arduino receives target elevation from Python
- Maps elevation to servo pulse width: `pulse = map(elevation, -90, 90, 1000, 2000)` microseconds
- Servo tilts laser pointer to target angle

**Calibration:**
- Adjust servo limits in code if mechanical range differs
- Ensure 0° elevation corresponds to horizontal pointing

### Laser Pointer

**Mounted to:** The pitch servo arm or rotating platform

**Operation:**
- Activated when valid coordinates are received
- Points toward chosen object's calculated sky position
- Can be toggled on/off via touchscreen

**Safety Notes:**
- ⚠️ Never point laser at aircraft, vehicles, or people
- ⚠️ Use only Class 2 lasers (<1mW) for safety
- ⚠️ Follow local regulations regarding laser pointers

### Motion Workflow

```
1. User taps object on touchscreen
         ↓
2. Arduino sends "STAR:Jupiter"
         ↓
3. Python queries JPL Horizons API
         ↓
4. Python calculates azimuth & elevation
         ↓
5. Python sends "157.23,42.15"
         ↓
6. Arduino parses coordinates
         ↓
7. Stepper motor rotates to azimuth (157.23°)
         ↓
8. Servo motor tilts to elevation (42.15°)
         ↓
9. Laser turns ON, pointing at Jupiter
```

---

## Available Celestial Objects

The system supports **24 celestial objects** across multiple categories:

### Planets
- **Inner Planets:** Mercury, Venus, Mars
- **Outer Planets:** Jupiter, Saturn, Uranus, Neptune

### Dwarf Planets
- Pluto
- Ceres

### Earth's Moon
- Moon (Luna)

### Martian Moons
- Phobos
- Deimos

### Jovian Moons (Jupiter)
- Io
- Europa
- Ganymede
- Callisto

### Saturnian Moons (Saturn)
- Titan
- Rhea
- Iapetus
- Enceladus

### Uranian Moons (Uranus)
- Titania
- Oberon

### Neptunian Moons (Neptune)
- Triton

### The Sun
- Sol (our star)

---

## Project Structure

```
IEEE-QP/
├── arduino/
│   ├── combined_control.ino       # Main Arduino sketch
│   ├── touchmapping.ino            # Touch calibration utilities
│   └── serial_communication.ino    # Serial protocol handler
│
├── python/
│   ├── PlanetaryObjectsFetcher.py  # Main Python backend
│   ├── PlanetaryObjectSelection.py # Object database
│   └── test.py                     # Testing utilities
│
├── docs/
│   └── wiring_diagram.md           # Hardware connection guide
│
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
└── LICENSE                          # MIT License
```

---

## System Architecture

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│  ┌────────────────────────────────────────────────────┐     │
│  │         Arduino TFT Touchscreen Display            │     │
│  │  • Object selection menu                           │     │
│  │  • Coordinate display                              │     │
│  │  • Status indicators                               │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ Serial Communication
                       │ (UART @ 9600 baud)
                       │
        ┌──────────────▼───────────────┐
        │                              │
        │      Arduino Controller      │
        │  • Parse serial commands     │
        │  • Control motors            │
        │  • Update display            │
        │                              │
        └──────┬───────────────┬───────┘
               │               │
     ┌─────────▼──────┐  ┌────▼──────────┐
     │ Stepper Motor  │  │ Servo Motor   │
     │ (Azimuth)      │  │ (Elevation)   │
     │ + Laser        │  │               │
     └────────────────┘  └───────────────┘
                       
                       
┌─────────────────────────────────────────────────────────────┐
│                      Python Backend                          │
│  ┌────────────────────────────────────────────────────┐     │
│  │         Serial Communication Handler               │     │
│  │  • Listen for object requests                      │     │
│  │  • Send coordinates back to Arduino                │     │
│  └────────────────┬───────────────────────────────────┘     │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────┐     │
│  │         JPL Horizons API Client                    │     │
│  │  • Format API queries                              │     │
│  │  • Parse ephemeris data                            │     │
│  │  • Calculate azimuth/elevation                     │     │
│  └────────────────┬───────────────────────────────────┘     │
└───────────────────┼──────────────────────────────────────────┘
                    │
                    │ HTTPS Request
                    │
        ┌───────────▼────────────────┐
        │                            │
        │  NASA JPL Horizons System  │
        │  • Ephemeris calculations  │
        │  • Orbital mechanics       │
        │                            │
        └────────────────────────────┘
```

### Coordinate System

The system uses the **horizontal coordinate system** (Alt-Az):

- **Azimuth (Az):** 0°–360°
  - 0° = North
  - 90° = East
  - 180° = South
  - 270° = West
  - Measured **clockwise** from North

- **Elevation (Alt):** −90° to +90°
  - 0° = Horizon
  - +90° = Zenith (directly overhead)
  - −90° = Nadir (directly below, not accessible)

### Time Synchronization

- Python backend uses system time (must be accurate)
- JPL Horizons calculates positions for current UTC time
- Recommend NTP time synchronization for best accuracy

---

## Troubleshooting

### Arduino Issues

#### Motors not moving
- ✅ Check motor driver connections and power supply
- ✅ Ensure **common ground** between Arduino and motor drivers
- ✅ Verify `steps_per_revolution` setting in code
- ✅ Test motors independently with simple sketches
- ✅ Check if motor driver is receiving step pulses (use LED or oscilloscope)

#### Laser not turning on
- ✅ Verify laser module works independently (connect to 5V/GND)
- ✅ Check transistor/MOSFET circuit if used
- ✅ Ensure digital pin mode is set to `OUTPUT`
- ✅ Measure voltage at laser control pin when activated

#### Touch not responding
- ✅ Verify XP/XM/YP/YM pin assignments
- ✅ Run `touchmapping.ino` to calibrate touch coordinates
- ✅ Check for loose connections to touch panel
- ✅ Test with different pressure levels

#### Display shows garbage or is blank
- ✅ Verify TFT library compatibility with your display
- ✅ Check power supply voltage (must be stable 5V)
- ✅ Try different display initialization sequences
- ✅ Ensure no pin conflicts with other peripherals

### Python Issues

#### "Serial port busy" error
- ✅ Close Arduino Serial Monitor before running Python script
- ✅ Check if another program is using the port
- ✅ On Linux: ensure user is in `dialout` group
  ```bash
  sudo usermod -a -G dialout $USER
  # Then log out and back in
  ```

#### API request failure
- ✅ Check internet connection
- ✅ Verify JPL Horizons endpoint is accessible
- ✅ Check for rate limiting (NASA may throttle requests)
- ✅ Ensure firewall isn't blocking outbound HTTPS

#### Incorrect coordinates
- ✅ Verify system time is accurate (use NTP)
- ✅ Check location coordinates in geolocation response
- ✅ Ensure object name matches JPL Horizons database exactly
- ✅ Account for local horizon obstructions

#### Serial communication drops
- ✅ Check USB cable quality
- ✅ Reduce baud rate if experiencing errors
- ✅ Add timeout handling in Python script
- ✅ Verify Arduino isn't resetting (capacitor on RESET pin may help)

### Mechanical Issues

#### Laser doesn't point at object
- ✅ Calibrate zero positions for both motors
- ✅ Verify azimuth direction (CW vs CCW)
- ✅ Check if servo elevation angle is correctly mapped
- ✅ Account for physical mounting offsets in code
- ✅ Ensure motors aren't skipping steps (reduce speed/acceleration)

#### Jerky or noisy motion
- ✅ Implement acceleration/deceleration curves
- ✅ Use `AccelStepper` library for smoother stepper control
- ✅ Check for mechanical binding or friction
- ✅ Reduce motor speed and increase holding torque

---

## Future Enhancements

### Short Term
- [ ] Add homing/calibration routine on startup
- [ ] Implement emergency stop button
- [ ] Add battery level indicator for portable operation
- [ ] Store favorite objects for quick access

### Medium Term
- [ ] GPS module integration for automatic location detection
- [ ] Real-time clock (RTC) for accurate timekeeping without internet
- [ ] SD card logging of pointing sessions
- [ ] Automatic tracking mode (continuously update position as objects move)

### Long Term
- [ ] Full star catalog support (Hipparcos/Tycho)
- [ ] Predict rise/set times and visibility windows
- [ ] Deep sky object database (Messier, NGC)
- [ ] Automated sky scanning/sweeping mode
- [ ] Mobile app control via Bluetooth
- [ ] Camera mount for astrophotography assistance

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Contribution Ideas
- Add support for new celestial objects
- Improve motor control algorithms
- Create wiring diagrams and schematics
- Write tutorials and documentation
- Report bugs and suggest features

---

## Data Sources & Credits

- **NASA JPL Horizons System** - Ephemeris data
  - [https://ssd.jpl.nasa.gov/horizons/](https://ssd.jpl.nasa.gov/horizons/)
- **IPInfo.io** - Geolocation API
  - [https://ipinfo.io/](https://ipinfo.io/)
- **Adafruit** - Graphics and display libraries
- **Arduino Community** - Various hardware libraries

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### MIT License Summary
```
Permission is granted to use, copy, modify, and distribute this software
for any purpose with or without fee, provided copyright notices are retained.
```

---

## Safety & Legal Disclaimer

⚠️ **Important Safety Information:**

- This device uses a **laser pointer**. Never point lasers at people, animals, vehicles, or aircraft.
- Use only **Class 2 lasers** (<1mW output) for this project.
- Follow all **local regulations** regarding laser pointer use.
- This device is for **educational and experimental purposes** only.
- The creators assume **no liability** for misuse or injuries.

---

## Acknowledgments

Special thanks to:
- NASA's Jet Propulsion Laboratory for free access to Horizons data
- The Arduino and Python communities for excellent tools and libraries
- All contributors and testers who helped improve this project

---

**Made with ❤️ for the IEEE Quarterly Projects**

*Clear skies and happy tracking!* 🌙✨
