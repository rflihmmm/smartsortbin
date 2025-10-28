// Include the required libraries
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Set the LCD address to 0x27 for a 16 chars and 2 line display
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  // Initialize the LCD
  lcd.init();
  
  // Turn on the blacklight
  lcd.backlight();
  
  // Print a message to the LCD
  lcd.print("Hello, world!");
}

void loop() {
  // Set the cursor to column 0, line 1
  // (note: line 1 is the second row, since counting begins with 0)
  lcd.setCursor(0, 1);
  
  // Print the number of seconds since reset
  lcd.print(millis() / 1000);
}
