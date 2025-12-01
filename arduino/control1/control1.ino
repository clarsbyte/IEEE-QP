#include <Adafruit_GFX.h>
#include <TouchScreen.h>
#include <MCUFRIEND_kbv.h>
#include <Servo.h>

#define MINPRESSURE 40
#define MAXPRESSURE 1000


const int16_t XP = 8,  XM = A2, YP = A3, YM = 9;
TouchScreen ts = TouchScreen(XP, YP, XM, YM, 300);
MCUFRIEND_kbv tft;


#define DIR_PIN 23
#define PUL_PIN 22
#define EN_PIN  24


const int STEPS_PER_TAP = 200;
const int STEP_DELAY_US = 800;


Servo servo1, servo2;
int angle1 = 90;
int angle2 = 90;
int delta  = 5;  


int mapX(int rawY) {
  return constrain(map(rawY, 130, 900, 0, 320), 0, 319);
}
int mapY(int rawX) {
  return constrain(map(rawX, 150, 880, 0, 240), 0, 239);
}


void drawUI() {
  tft.fillScreen(0x0000);

  
  tft.fillRect(0, 0, 160, 120, 0x001F); 
  tft.setCursor(40, 50);
  tft.setTextColor(0xFFFF);
  tft.setTextSize(3);
  tft.print("S+");

  
  tft.fillRect(160, 0, 160, 120, 0xF800); 
  tft.setCursor(200, 50);
  tft.setTextColor(0xFFFF);
  tft.setTextSize(3);
  tft.print("S-");

  
  tft.fillRect(0, 120, 160, 120, 0x07E0); 
  tft.setCursor(30, 170);
  tft.setTextColor(0xFFFF);
  tft.setTextSize(2);
  tft.print("LEFT");

  
  tft.fillRect(160, 120, 160, 120, 0x07FF); 
  tft.setCursor(180, 170);
  tft.setTextColor(0xFFFF);
  tft.setTextSize(2);
  tft.print("RIGHT");
}

void setup() {
  Serial.begin(9600);

  uint16_t ID = tft.readID();
  tft.begin(ID);
  tft.setRotation(3);   
  drawUI();

  
  servo1.attach(30);
  servo2.attach(31);
  servo1.write(angle1);
  servo2.write(angle2);

  // Stepper
  pinMode(DIR_PIN, OUTPUT);
  pinMode(PUL_PIN, OUTPUT);
  pinMode(EN_PIN, OUTPUT);
  digitalWrite(EN_PIN, LOW);   
}

void stepOnce(int dir, int steps) {
  digitalWrite(DIR_PIN, dir);
  for (int i = 0; i < steps; i++) {
    digitalWrite(PUL_PIN, HIGH);
    delayMicroseconds(STEP_DELAY_US);
    digitalWrite(PUL_PIN, LOW);
    delayMicroseconds(STEP_DELAY_US);
  }
}

void loop() {
  TSPoint p = ts.getPoint();
  pinMode(XM, OUTPUT);
  pinMode(YP, OUTPUT);

  if (p.z > MINPRESSURE && p.z < MAXPRESSURE) {
    int px = mapX(p.y);
    int py = mapY(p.x);

    Serial.print("px="); Serial.print(px);
    Serial.print(" py="); Serial.println(py);

    
    

    
    if (py >= 120) {
      
      if (px < 160) {
        Serial.println("BTN: Servo +");
        angle1 = min(angle1 + delta, 180);
        angle2 = max(angle2 - delta, 0);   
      }
      
      else {
        Serial.println("BTN: Servo -");
        angle1 = max(angle1 - delta, 0);
        angle2 = min(angle2 + delta, 180); 
      }

      servo1.write(angle1);
      servo2.write(angle2);
    }

    
    else {
      
      if (px < 160) {
        Serial.println("BTN: Step LEFT");
        stepOnce(LOW,  STEPS_PER_TAP);
      }
      
      else {
        Serial.println("BTN: Step RIGHT");
        stepOnce(HIGH, STEPS_PER_TAP);
      }
    }

    delay(200);  
  }
}
