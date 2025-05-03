#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Initialize the LCD with I2C address 0x27 (adjust if needed)
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  Serial.begin(9600);  // Start serial communication
  lcd.begin(16, 2);    // Initialize the LCD
  lcd.backlight();      // Turn on LCD backlight
  lcd.print("Waiting for data"); // Initial message
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n'); // Read incoming data
    lcd.clear();

    // Print received data to the serial monitor
    Serial.print("Received: ");
    Serial.println(data);

    // Split data by commas
    int firstComma = data.indexOf(',');
    if (firstComma != -1) {
      String id = data.substring(0, firstComma);
      String remaining = data.substring(firstComma + 1);
      lcd.setCursor(0, 0);
      lcd.print("ID:");
      lcd.print(id);
      lcd.setCursor(0, 1);
      lcd.print(remaining.substring(0, 16)); // Display remaining info

      Serial.println("LCD Line 1: ID: " + id);
      Serial.println("LCD Line 2: " + remaining);
    } else {
      lcd.setCursor(0, 0);
      lcd.print(data.substring(0, 16)); // Display all data on one line if no comma
      Serial.println("LCD Display: " + data);
    }
  }
}
