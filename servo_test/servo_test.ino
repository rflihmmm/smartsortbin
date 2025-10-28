#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position

void setup() {
  myservo.attach(9);
    // attaches the servo on pin 13 to the servo object for ESP32
myservo.write(75);
}

void loop() {
  // for (pos = 0; pos <= 90; pos += 1) { // goes from 0 degrees to 90 degrees
  //   // in steps of 1 degree
  //   myservo.write(pos);              // tell servo to go to position in variable 'pos'
  //   delay(15);                       // waits 15ms for the servo to reach the position
  // }
  // delay(1000); // wait for 1 second at 90 degrees
  // for (pos = 90; pos >= 0; pos -= 1) { // goes from 90 degrees to 0 degrees
  //   myservo.write(pos);              // tell servo to go to position in variable 'pos'
  //   delay(15);                       // waits 15ms for the servo to reach the position
  // }
  // delay(1000); // wait for 1 second at 0 degrees
}
