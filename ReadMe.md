# Armillary Sphere

A real-time celestial body tracking system combining Arduino touchscreen interface and Servo Motors with NASA JPL Horizons API for accurate astronomical positioning.

## Overview

This project provides an interactive touchscreen interface for selecting and tracking celestial objects (planets, moons, asteroids) with real-time azimuth and elevation coordinates. The system uses bidirectional serial communication between an Arduino-based touchscreen display and a Python backend that interfaces with NASA's JPL Horizons API.

## Features

- **Interactive Touchscreen UI**: Browse and select from 24 celestial objects including planets, moons, and dwarf planets
- **Real-time Coordinate Tracking**: Get current azimuth and elevation for any selected object
- **Location-aware**: Automatically detects user location via IP geolocation for accurate local coordinates
- **NASA JPL Integration**: Fetches astronomical data from the official JPL Horizons system
- **Live Display**: Arduino screen displays both object selection interface and current coordinates
- **Bidirectional Communication**: Seamless Arduino ↔ Python serial communication

## Hardware Requirements

- **Arduino Board**: Compatible with Arduino Uno or similar (ATmega328P-based)
- **TFT Touchscreen Display**: 320x240 pixel display compatible with MCUFRIEND_kbv library
- **Touch Panel**: 4-wire resistive touchscreen

### Pin Configuration

```
XP (X+): Digital Pin 8
XM (X-): Analog Pin A2
YP (Y+): Analog Pin A3
YM (Y-): Digital Pin 9
```

## Software Requirements

### Arduino
- Arduino IDE 1.8.x or later
- Required Libraries:
  - `Adafruit_GFX`
  - `TouchScreen`
  - `MCUFRIEND_kbv`

### Python
- Python 3.7+
- Required packages:
  ```bash
  pip install requests pyserial numpy
  ```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/IEEE-QP.git
cd IEEE-QP
```

### 2. Install Python Dependencies

```bash
pip install requests pyserial numpy
```

### 3. Arduino Setup

1. Open `arduino/combined_control.ino` in Arduino IDE
2. Install required libraries via Library Manager:
   - Adafruit GFX Library
   - TouchScreen (by Adafruit)
   - MCUFRIEND_kbv
3. Upload to your Arduino board

### 4. Configure Serial Port

Edit `PlanetaryObjectsFetcher.py` line 13-17 to match your Arduino's COM port:

```python
serial = serial.Serial(
    port='COM6',  # Change to your port (e.g., 'COM3', '/dev/ttyUSB0', '/dev/ttyACM0')
    baudrate=9600,
    timeout=1
)
```

**Finding your port:**
- **Windows**: Check Device Manager → Ports (COM & LPT)
- **macOS/Linux**: Run `ls /dev/tty.*` or `ls /dev/ttyUSB*`

## Usage

### Quick Start

1. **Upload Arduino sketch**: Upload `arduino/combined_control.ino` to your Arduino
2. **Run Python script**:
   ```bash
   python PlanetaryObjectsFetcher.py
   ```
3. **Interact with touchscreen**:
   - Touch top-left or top-right to select celestial object
   - Touch bottom-left/right to navigate Prev/Next pages
   - Coordinates display automatically in top-left corner

### Common Mistakes

**Opening Serial Monitor on Arduino IDE**:
The Serial Monitor locks the COM port and prevents Python from connecting. **You must close the Serial Monitor** before running the Python script!

### Communication Protocol

**Arduino → Python:**
```
STAR:Moon
```

**Python → Arduino:**
```
131.587713,38.069515
```

Format: `azimuth,elevation` in degrees

## Available Celestial Objects

### Planets
Sun, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune

### Dwarf Planets
Pluto, Ceres

### Earth's Moon
Moon

### Moons of Mars
Phobos, Deimos

### Galilean Moons (Jupiter)
Io, Europa, Ganymede, Callisto

### Moons of Saturn
Titan, Rhea, Iapetus, Enceladus

### Moons of Uranus
Titania, Oberon

### Moons of Neptune
Triton

## Project Structure

```
IEEE-QP/
├── arduino/
│   ├── combined_control.ino          # Main Arduino sketch
│   ├── touchmapping.ino               # Legacy: Touchscreen UI only
│   └── serial_communication.ino       # Legacy: Serial handling only
├── PlanetaryObjectsFetcher.py         # Main Python backend
├── PlaneraryObjectSelection.py        # JPL Horizons object ID mappings
├── test.py                            # Standalone coordinate fetcher
└── ReadMe.md                          # This file
```

## How It Works

### System Architecture

```
┌─────────────────┐         Serial          ┌──────────────────┐
│                 │  ─────────────────────>  │                  │
│  Arduino TFT    │      "STAR:Moon"         │  Python Script   │
│  Touchscreen    │                          │                  │
│                 │  <─────────────────────  │                  │
└─────────────────┘   "131.58,38.07"         └──────────────────┘
                                                      │
                                                      │ HTTPS
                                                      ▼
                                              ┌──────────────────┐
                                              │  NASA JPL        │
                                              │  Horizons API    │
                                              └──────────────────┘
```

### Workflow

1. **User Selection**: Touch an object on the Arduino display
2. **Request**: Arduino sends object name to Python via serial
3. **Location Detection**: Python determines user's geographic location
4. **API Query**: Python queries JPL Horizons for current coordinates
5. **Data Parsing**: Extract azimuth and elevation from API response
6. **Response**: Send coordinates back to Arduino
7. **Display**: Arduino shows coordinates on screen

### Coordinate System

- **Azimuth**: Horizontal angle (0-360°) measured clockwise from North
  - 0° = North
  - 90° = East
  - 180° = South
  - 270° = West

- **Elevation**: Vertical angle (0-90°) above the horizon
  - 0° = Horizon
  - 90° = Directly overhead (zenith)
  - Negative values = Below horizon (not visible)

## API Reference

### PlanetaryObjectsFetcher Class

#### Methods

**`get_user_location()`**
```python
lat, lon, elev = PlanetaryObjectsFetcher.get_user_location()
```
Returns user's geographic coordinates via IP geolocation.

**Returns**: `(latitude, longitude, elevation)` tuple

---

**`fetch_coordinates(target_body)`**
```python
coords = PlanetaryObjectsFetcher.fetch_coordinates("301")  # Moon
```
Fetch azimuth and elevation coordinates for a celestial body.

**Parameters**:
- `target_body` (str): JPL Horizons object ID

**Returns**: List of coordinate strings from API

---

**`parse_coordinates(coord_string)`**
```python
azimuth, elevation = PlanetaryObjectsFetcher.parse_coordinates(coord_string)
```
Parse raw coordinate string into azimuth/elevation values.

**Parameters**:
- `coord_string` (str): Raw coordinate string from API

**Returns**: `(azimuth, elevation)` tuple in degrees

---

**`fetch_distance(target_body)`**
```python
distance = PlanetaryObjectsFetcher.fetch_distance("301")
```
Fetch distance data from observer to celestial object.

**Parameters**:
- `target_body` (str): JPL Horizons object ID

**Returns**: Distance data from API

### PlanetaryObjectSelection Class

Dictionary mapping common names to JPL Horizons IDs:

```python
from PlaneraryObjectSelection import PlanetaryObjectSelection

moon_id = PlanetaryObjectSelection.OBJECTS["Moon"]  # Returns "301"
mars_id = PlanetaryObjectSelection.OBJECTS["Mars"]  # Returns "499"
```

## Troubleshooting

### Arduino Issues

**Display not working:**
- Verify TFT shield is properly seated on Arduino
- Check library versions (update to latest)
- Try different TFT IDs in `tft.begin(ID)`
- Test with example sketches from MCUFRIEND library

**Touch not responsive:**
- Verify pin connections match code
- Adjust `MINPRESSURE` (line 5) and `MAXPRESSURE` (line 6) values
- Calibrate touch mapping in `mapX()` and `mapY()` functions (lines 14-19)
- Test touch with TouchScreen library examples

### Python Issues

**Serial port not found:**
- Check Arduino is connected via USB and drivers are installed
- Verify correct COM port in code (Windows: Device Manager, macOS/Linux: `ls /dev/tty*`)
- **Close Arduino Serial Monitor** (conflicts with Python serial connection)
- Try different USB ports or cables

**API request failures:**
- Check internet connection
- Verify JPL Horizons API is accessible: https://ssd.jpl.nasa.gov/api/horizons.api
- Check for rate limiting (wait a few seconds between requests)
- Verify object ID exists in `PlanetaryObjectSelection.OBJECTS`

**Location detection fails:**
- System falls back to (0, 0, 0) coordinates
- Check internet connection for IP geolocation
- Manually set location in `get_user_location()` if needed

**Import errors:**
- Ensure all dependencies are installed: `pip install requests pyserial numpy`
- Check Python version is 3.7+

## Data Sources

- **Astronomical Data**: NASA JPL Horizons System API
  - Documentation: https://ssd.jpl.nasa.gov/horizons/
  - API Access: https://ssd-api.jpl.nasa.gov/doc/horizons.html

- **Location Data**: IPInfo.io Geolocation API
  - Service: https://ipinfo.io

## Future Enhancements

- [ ] Store and display object distance (range)
- [ ] Add constellation identification
- [ ] Implement custom object tracking (asteroids, comets)
- [ ] Add GPS module for precise location
- [ ] Save favorite objects
- [ ] Time-based prediction (future positions)
- [ ] Export tracking data to CSV/JSON
- [ ] Add rise/set times for objects
- [ ] Implement compass mode for finding objects

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NASA JPL for providing the Horizons API
- Adafruit for excellent Arduino libraries
- IPInfo.io for geolocation services
- MCUFRIEND for TFT display library

## Contact

For questions or support, please open an issue on GitHub.

---

**Note**: This project is for educational purposes and astronomical observation. Coordinate accuracy depends on location detection precision and API data freshness. For professional astronomical work, use dedicated equipment with GPS and precise time synchronization.
