#include <Adafruit_GFX.h>
#include <TouchScreen.h>
#include <MCUFRIEND_kbv.h>
#include <Servo.h>

#define MINPRESSURE 40
#define MAXPRESSURE 1000

// Touchscreen pins
const int16_t XP = 8,  XM = A2, YP = A3, YM = 9;
TouchScreen ts = TouchScreen(XP, YP, XM, YM, 300);
MCUFRIEND_kbv tft;

// Stepper motor pins
#define DIR_PIN 23
#define PUL_PIN 22
#define EN_PIN  24

// Stepper parameters
const int STEPS_PER_REV = 800;
const int STEP_DELAY_US = 800;
const float STEPS_PER_DEGREE = 20.0 / 9.0;

// Servo motors
Servo servo1, servo2;
int currentServoAngle = 90;  // Track current elevation angle

// Object selection
const int NUM_OBJECTS = 24;
const char* OBJECTS[NUM_OBJECTS] = {
  "Sun",       // 0
  "Mercury",   // 1
  "Venus",     // 2
  "Mars",      // 3
  "Jupiter",   // 4
  "Saturn",    // 5
  "Uranus",    // 6
  "Neptune",   // 7
  "Pluto",     // 8
  "Ceres",     // 9
  "Moon",      //10
  "Phobos",    //11
  "Deimos",    //12
  "Io",        //13
  "Europa",    //14
  "Ganymede",  //15
  "Callisto",  //16
  "Titan",     //17
  "Rhea",      //18
  "Iapetus",   //19
  "Enceladus", //20
  "Titania",   //21
  "Oberon",    //22
  "Triton"     //23
};

const int OBJECTS_PER_PAGE = 2;
const int TOTAL_PAGES = (NUM_OBJECTS + OBJECTS_PER_PAGE - 1) / OBJECTS_PER_PAGE;

int currentPage = 0;

// Variables to store received azimuth and elevation
float currentAzimuth = 0.0;
float currentElevation = 0.0;
float targetAzimuth = 0.0;
float targetElevation = 0.0;
bool dataReceived = false;

// Mapping functions
int mapX(int rawY) {
  return constrain(map(rawY, 130, 900, 0, 320), 0, 319);
}
int mapY(int rawX) {
  return constrain(map(rawX, 150, 880, 0, 240), 0, 239);
}

// Stepper control function
void stepMotor(int dir, int steps) {
  digitalWrite(DIR_PIN, dir);
  for (int i = 0; i < steps; i++) {
    digitalWrite(PUL_PIN, HIGH);
    delayMicroseconds(STEP_DELAY_US);
    digitalWrite(PUL_PIN, LOW);
    delayMicroseconds(STEP_DELAY_US);
  }
}

// Move to target azimuth
void moveToAzimuth(float targetAz) {
  float azDiff = targetAz - currentAzimuth;
  int steps = abs((int)(azDiff * STEPS_PER_DEGREE));

  if (steps > 0) {
    int direction = (azDiff > 0) ? HIGH : LOW;
    stepMotor(direction, steps);
    currentAzimuth = targetAz;

    Serial.print("Moved to azimuth: ");
    Serial.print(currentAzimuth);
    Serial.print(" (");
    Serial.print(steps);
    Serial.println(" steps)");
  }
}

// Move to target elevation
void moveToElevation(float targetEl) {
  // Handle negative angles: convert to positive by adding 180
  if (targetEl < 0) {
    targetEl = 180 + targetEl;
  }
  int targetAngle = constrain((int)targetEl, 0, 180);

  if (targetAngle != currentServoAngle) {
    currentServoAngle = targetAngle;
    servo1.write(currentServoAngle);
    servo2.write(180 - currentServoAngle);
    currentElevation = targetEl;
  }
}

// Draw the UI
void drawPage() {
  tft.fillScreen(0x0000);
  tft.setTextSize(2);
  tft.setTextColor(0xFFFF);

  int idxLeft  = currentPage * OBJECTS_PER_PAGE;
  int idxRight = idxLeft + 1;

  // Top left - Object 1
  tft.fillRect(0, 0, 160, 120, 0x07E0); // green
  tft.setCursor(10, 50);
  if (idxLeft < NUM_OBJECTS) {
    tft.print(OBJECTS[idxLeft]);
  } else {
    tft.print("---");
  }

  // Top right - Object 2
  tft.fillRect(160, 0, 160, 120, 0x001F); // blue
  tft.setCursor(170, 50);
  if (idxRight < NUM_OBJECTS) {
    tft.print(OBJECTS[idxRight]);
  } else {
    tft.print("---");
  }

  // Bottom left - Prev
  tft.fillRect(0, 120, 160, 120, 0x7BEF); // grey
  tft.setCursor(40, 170);
  tft.print("Prev");

  // Bottom right - Next
  tft.fillRect(160, 120, 160, 120, 0x7BEF);
  tft.setCursor(190, 170);
  tft.print("Next");

  // Page numbers
  tft.setTextSize(2);
  tft.setCursor(100, 220);
  tft.print("Page ");
  tft.print(currentPage + 1);
  tft.print("/");
  tft.print(TOTAL_PAGES);

  // Display azimuth and elevation if data received
  if (dataReceived) {
    tft.setTextSize(1);
    tft.setCursor(5, 5);
    tft.print("Az:");
    tft.print(currentAzimuth, 1);
    tft.print(" El:");
    tft.print(currentElevation, 1);
  }
}

void setup() {
  Serial.begin(9600);

  // Initialize TFT display
  uint16_t ID = tft.readID();
  tft.begin(ID);
  tft.setRotation(3);
  drawPage();

  // Initialize servos
  servo1.attach(30);
  servo2.attach(31);
  servo1.write(currentServoAngle);
  servo2.write(180 - currentServoAngle);

  // Initialize stepper motor
  pinMode(DIR_PIN, OUTPUT);
  pinMode(PUL_PIN, OUTPUT);
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW);
}

void loop() {
  // Check for incoming serial data (azimuth, elevation)
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();

    int commaIndex = data.indexOf(',');
    if (commaIndex > 0) {
      targetAzimuth = data.substring(0, commaIndex).toFloat();
      targetElevation = data.substring(commaIndex + 1).toFloat();
      dataReceived = true;

      // Move motors to new positions
      moveToAzimuth(targetAzimuth);
      moveToElevation(targetElevation);

      // Redraw page to show updated coordinates
      drawPage();
    }
  }

  // Handle touch input
  TSPoint p = ts.getPoint();
  pinMode(XM, OUTPUT);
  pinMode(YP, OUTPUT);

  if (p.z > MINPRESSURE && p.z < MAXPRESSURE) {
    int px = mapX(p.y);
    int py = mapY(p.x);

    bool isTop    = (py >= 120);
    bool isLeft   = (px >= 160);
    bool isRight  = !isLeft;
    bool isBottom = !isTop;

    int idxLeft  = currentPage * OBJECTS_PER_PAGE;
    int idxRight = idxLeft + 1;

    if (isTop) {
      // Object selection
      if (isLeft && idxLeft < NUM_OBJECTS) {
        const char* name = OBJECTS[idxLeft];

        // Reset to zero position
        moveToAzimuth(0.0);
        moveToElevation(0.0);

        Serial.print("STAR:");
        Serial.println(name);
      }
      else if (isRight && idxRight < NUM_OBJECTS) {
        const char* name = OBJECTS[idxRight];

        // Reset to zero position
        moveToAzimuth(0.0);
        moveToElevation(0.0);

        Serial.print("STAR:");
        Serial.println(name);
      }
    }
    else {
      // Navigation
      if (isLeft) {
        if (currentPage > 0) {
          currentPage--;
          drawPage();
        }
      }
      else {
        if (currentPage < TOTAL_PAGES - 1) {
          currentPage++;
          drawPage();
        }
      }
    }

    delay(200);
  }
}
