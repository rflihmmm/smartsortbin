// Define stepper motor connections and steps per revolution:
const int dirPin = 4; // DIR pin connected to Arduino pin 8
const int stepPin = 3; // STEP pin connected to Arduino pin 9
const int stepsPerRevolution = 200; // 200 steps per revolution for a standard 1.8 degree stepper

// Delay between step pulses in microseconds (adjust for speed)
// A larger value means slower rotation. 1000 microseconds = 1 millisecond.
const int stepDelayMicroseconds = 100;

void setup() {
  Serial.begin(9600);
  Serial.println("Stepper test started with A4988 driver.");

  pinMode(dirPin, OUTPUT);
  pinMode(stepPin, OUTPUT);
}

// Function to rotate the stepper motor
// steps: number of steps to move
// direction: true for one direction (e.g., clockwise), false for the other (e.g., counter-clockwise)
void stepMotor(int steps, bool direction) {
  digitalWrite(dirPin, direction); // Set direction pin
  for (int i = 0; i < steps; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(stepDelayMicroseconds);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(stepDelayMicroseconds);
  }
}

void loop() {
  // Rotate 200 steps clockwise
  Serial.println("Rotating 200 steps clockwise...");
  stepMotor(stepsPerRevolution, HIGH); // HIGH for clockwise (adjust based on your wiring)
  delay(1000); // Wait for a second

  // Rotate 200 steps counter-clockwise
  Serial.println("Rotating 200 steps counter-clockwise...");
  stepMotor(stepsPerRevolution, LOW); // LOW for counter-clockwise (adjust based on your wiring)
  delay(1000); // Wait for a second
}
