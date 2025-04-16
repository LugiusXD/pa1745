#include <TFT_eSPI.h>
#include <SPI.h>

// Button pins
const int button1Pin = 22;
const int button2Pin = 17;
const int button3Pin = 12;

// Task state
bool b1 = false, b2 = false, b3 = false;
bool task1Active = false, task2Active = false, task3Active = false;
bool task4Active = false, task5Active = false, task6Active = false;
bool anyButtonPressed = false;
unsigned long pressTime = 0;

TFT_eSPI tft = TFT_eSPI();
uint16_t taskColor = TFT_WHITE;

// Display task
void showTask(const char* taskLabel, uint16_t color) {
  tft.fillScreen(TFT_BLACK);
  tft.setTextColor(color, TFT_BLACK);
  tft.setTextDatum(MC_DATUM);
  tft.setTextSize(4);
  tft.drawString(taskLabel, 160, 120);
  Serial.println(String(taskLabel) + ": START");
}

// Fade out and print release
void fadeOutTask(const char* taskLabel) {
  uint16_t fadeSteps[] = {TFT_DARKGREY, TFT_NAVY, TFT_BLACK};
  tft.setTextDatum(MC_DATUM);
  tft.setTextSize(4);

  for (int i = 0; i < 3; i++) {
    tft.fillScreen(TFT_BLACK);
    tft.setTextColor(fadeSteps[i], TFT_BLACK);
    tft.drawString(taskLabel, 160, 120);
    delay(150);
  }

  tft.fillScreen(TFT_BLACK);
  Serial.println(String(taskLabel) + ": STOP");
}

void setup() {
  Serial.begin(9600);
  pinMode(button1Pin, INPUT_PULLUP);
  pinMode(button2Pin, INPUT_PULLUP);
  pinMode(button3Pin, INPUT_PULLUP);

  tft.init();
  tft.setRotation(1);
  tft.fillScreen(TFT_BLACK);
  tft.setTextDatum(MC_DATUM);
}

void loop() {
  bool currentB1 = digitalRead(button1Pin) == LOW;
  bool currentB2 = digitalRead(button2Pin) == LOW;
  bool currentB3 = digitalRead(button3Pin) == LOW;

  if ((currentB1 || currentB2 || currentB3) && !anyButtonPressed) {
    pressTime = millis();
    anyButtonPressed = true;
  }

  if (anyButtonPressed && millis() - pressTime >= 2000) {
    b1 = digitalRead(button1Pin) == LOW;
    b2 = digitalRead(button2Pin) == LOW;
    b3 = digitalRead(button3Pin) == LOW;

    task1Active = task2Active = task3Active = false;
    task4Active = task5Active = task6Active = false;

    if (b1 && b2 && b3) {
      task6Active = true;
      taskColor = TFT_ORANGE;
      showTask("TASK 6", taskColor);
    } else if (b1 && b2) {
      task4Active = true;
      taskColor = TFT_CYAN;
      showTask("TASK 4", taskColor);
    } else if (b2 && b3) {
      task5Active = true;
      taskColor = TFT_MAGENTA;
      showTask("TASK 5", taskColor);
    } else if (b1 && !b2 && !b3) {
      task1Active = true;
      taskColor = TFT_GREEN;
      showTask("TASK 1", taskColor);
    } else if (b2 && !b1 && !b3) {
      task2Active = true;
      taskColor = TFT_BLUE;
      showTask("TASK 2", taskColor);
    } else if (b3 && !b1 && !b2) {
      task3Active = true;
      taskColor = TFT_YELLOW;
      showTask("TASK 3", taskColor);
    }

    // Wait for release
    while (digitalRead(button1Pin) == LOW ||
           digitalRead(button2Pin) == LOW ||
           digitalRead(button3Pin) == LOW) {
      delay(10);
    }

    if (task6Active) fadeOutTask("TASK 6");
    if (task4Active) fadeOutTask("TASK 4");
    if (task5Active) fadeOutTask("TASK 5");
    if (task1Active) fadeOutTask("TASK 1");
    if (task2Active) fadeOutTask("TASK 2");
    if (task3Active) fadeOutTask("TASK 3");

    anyButtonPressed = false;
  }

  delay(10);
}
