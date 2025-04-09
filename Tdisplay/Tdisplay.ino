const int button1Pin = 22;
const int button2Pin = 17;
const int button3Pin = 12;

// Track button states
bool b1 = false, b2 = false, b3 = false;

// Track task states
bool task1Active = false;
bool task2Active = false;
bool task3Active = false;
bool task4Active = false;
bool task5Active = false;
bool task6Active = false;

void setup() {
  Serial.begin(9600);
  pinMode(button1Pin, INPUT_PULLUP);
  pinMode(button2Pin, INPUT_PULLUP);
  pinMode(button3Pin, INPUT_PULLUP);
}

void loop() {
  // Read button states (LOW = START)
  b1 = digitalRead(button1Pin) == LOW;
  b2 = digitalRead(button2Pin) == LOW;
  b3 = digitalRead(button3Pin) == LOW;

  // --- Task 6: All buttons ---
  if (b1 && b2 && b3) {
    if (!task6Active) {
      Serial.println("Task 6: START");
      task6Active = true;
    }
  } else if (task6Active) {
    Serial.println("Task 6: STOP");
    task6Active = false;
  }

  // --- Task 4: Button 1 + 2 ---
  if (b1 && b2 && !b3) {
    if (!task4Active) {
      Serial.println("Task 4: START");
      task4Active = true;
    }
  } else if (task4Active) {
    Serial.println("Task 4: STOP");
    task4Active = false;
  }

  // --- Task 5: Button 2 + 3 ---
  if (b2 && b3 && !b1) {
    if (!task5Active) {
      Serial.println("Task 5: START");
      task5Active = true;
    }
  } else if (task5Active) {
    Serial.println("Task 5: STOP");
    task5Active = false;
  }

  // --- Task 1: Only Button 1 ---
  if (b1 && !b2 && !b3) {
    if (!task1Active) {
      Serial.println("Task 1: START");
      task1Active = true;
    }
  } else if (task1Active) {
    Serial.println("Task 1: STOP");
    task1Active = false;
  }

  // --- Task 2: Only Button 2 ---
  if (b2 && !b1 && !b3) {
    if (!task2Active) {
      Serial.println("Task 2: START");
      task2Active = true;
    }
  } else if (task2Active) {
    Serial.println("Task 2: STOP");
    task2Active = false;
  }

  // --- Task 3: Only Button 3 ---
  if (b3 && !b1 && !b2) {
    if (!task3Active) {
      Serial.println("Task 3: START");
      task3Active = true;
    }
  } else if (task3Active) {
    Serial.println("Task 3: STOP");
    task3Active = false;
  }

  delay(50);  // Small debounce + CPU relief
}
