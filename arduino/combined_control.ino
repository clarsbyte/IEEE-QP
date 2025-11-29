#include <Adafruit_GFX.h>
#include <TouchScreen.h>
#include <MCUFRIEND_kbv.h>

#define MINPRESSURE 40
#define MAXPRESSURE 1000


const int16_t XP = 8,  XM = A2, YP = A3, YM = 9;
TouchScreen ts = TouchScreen(XP, YP, XM, YM, 300);
MCUFRIEND_kbv tft;


int mapX(int rawY) {
  return constrain(map(rawY, 130, 900, 0, 320), 0, 319);
}
int mapY(int rawX) {
  return constrain(map(rawX, 150, 880, 0, 240), 0, 239);
}


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

// two object each page, Prev / Next
const int OBJECTS_PER_PAGE = 2;
const int TOTAL_PAGES = (NUM_OBJECTS + OBJECTS_PER_PAGE - 1) / OBJECTS_PER_PAGE;

int currentPage = 0;

// Variables to store received azimuth and elevation
float currentAzimuth = 0.0;
float currentElevation = 0.0;
bool dataReceived = false;


void drawPage() {
  tft.fillScreen(0x0000);
  tft.setTextSize(2);
  tft.setTextColor(0xFFFF);


  int idxLeft  = currentPage * OBJECTS_PER_PAGE;
  int idxRight = idxLeft + 1;

  // topleft
  tft.fillRect(0, 0, 160, 120, 0x07E0); // green
  tft.setCursor(10, 50);
  if (idxLeft < NUM_OBJECTS) {
    tft.print(OBJECTS[idxLeft]);
  } else {
    tft.print("---");
  }

  // topright
  tft.fillRect(160, 0, 160, 120, 0x001F); // blue
  tft.setCursor(170, 50);
  if (idxRight < NUM_OBJECTS) {
    tft.print(OBJECTS[idxRight]);
  } else {
    tft.print("---");
  }

  // Prev
  tft.fillRect(0, 120, 160, 120, 0x7BEF); // grey
  tft.setCursor(40, 170);
  if (currentPage > 0) {
    tft.print("Prev");
  } else {
    tft.print("Prev");
  }

  // Next
  tft.fillRect(160, 120, 160, 120, 0x7BEF);
  tft.setCursor(190, 170);
  if (currentPage < TOTAL_PAGES - 1) {
    tft.print("Next");
  } else {
    tft.print("Next");
  }

  // page numbers
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

  uint16_t ID = tft.readID();
  tft.begin(ID);
  tft.setRotation(3);

  drawPage();
}


void loop() {
  // Check for incoming serial data (azimuth, elevation)
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();

    int commaIndex = data.indexOf(',');
    if (commaIndex > 0) {
      currentAzimuth = data.substring(0, commaIndex).toFloat();
      currentElevation = data.substring(commaIndex + 1).toFloat();
      dataReceived = true;

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

      if (isLeft && idxLeft < NUM_OBJECTS) {
        const char* name = OBJECTS[idxLeft];
        Serial.print("STAR:");
        Serial.println(name);
      }

      else if (isRight && idxRight < NUM_OBJECTS) {
        const char* name = OBJECTS[idxRight];
        Serial.print("STAR:");
        Serial.println(name);
      }
    }

    else {

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
