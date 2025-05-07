#include <TFT_eSPI.h>
#include <SPI.h>

// Button pins
const int button1Pin = 22;
const int button2Pin = 17;
const int button3Pin = 12;

// Task state
bool b1 = false, b2 = false, b3 = false;
bool Task1Active = false, Task2Active = false, Task3Active = false;
bool Task4Active = false, Task5Active = false, Task6Active = false;
bool anyButtonPressed = false;
unsigned long pressTime = 0;

TFT_eSPI tft = TFT_eSPI();
uint16_t TaskColor = TFT_WHITE;

// Display Task
void showTask(const char* TaskLabel, uint16_t color) {
  tft.fillScreen(TFT_BLACK);
  tft.setRotation(3);
  tft.setTextColor(color, TFT_BLACK);
  tft.setTextDatum(MC_DATUM);
  tft.setTextSize(6);
  tft.drawString(TaskLabel, 160, 120);
  Serial.println(String(TaskLabel) + ": START");
}

// Fade out and print release
void fadeOutTask(const char* TaskLabel) {
  uint16_t fadeSteps[] = {TFT_DARKGREY, TFT_NAVY, TFT_BLACK};
  tft.setTextDatum(MC_DATUM);
  tft.setTextSize(4);

  for (int i = 0; i < 3; i++) {
    tft.fillScreen(TFT_BLACK);
    tft.setTextColor(fadeSteps[i], TFT_BLACK);
    tft.drawString(TaskLabel, 160, 120);
    delay(150);
  }

  tft.fillScreen(TFT_BLACK);
  Serial.println(String(TaskLabel) + ": STOP");
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

    Task1Active = Task2Active = Task3Active = false;
    Task4Active = Task5Active = Task6Active = false;

    if (b1 && b2 && b3) {
      Task6Active = true;
      TaskColor = TFT_ORANGE;
      showTask("Task 6", TaskColor);
    } else if (b1 && b2) {
      Task4Active = true;
      TaskColor = TFT_CYAN;
      showTask("Task 4", TaskColor);
    } else if (b2 && b3) {
      Task5Active = true;
      TaskColor = TFT_MAGENTA;
      showTask("Task 5", TaskColor);
    } else if (b1 && !b2 && !b3) {
      Task1Active = true;
      TaskColor = TFT_GREEN;
      showTask("Task 1", TaskColor);
    } else if (b2 && !b1 && !b3) {
      Task2Active = true;
      TaskColor = TFT_BLUE;
      showTask("Task 2", TaskColor);
    } else if (b3 && !b1 && !b2) {
      Task3Active = true;
      TaskColor = TFT_YELLOW;
      showTask("Task 3", TaskColor);
    }

    // Wait for release
    while (digitalRead(button1Pin) == LOW ||
           digitalRead(button2Pin) == LOW ||
           digitalRead(button3Pin) == LOW) {
      delay(10);
    }

    if (Task6Active) fadeOutTask("Task 6");
    if (Task4Active) fadeOutTask("Task 4");
    if (Task5Active) fadeOutTask("Task 5");
    if (Task1Active) fadeOutTask("Task 1");
    if (Task2Active) fadeOutTask("Task 2");
    if (Task3Active) fadeOutTask("Task 3");

    anyButtonPressed = false;
  }

  delay(10);
}
