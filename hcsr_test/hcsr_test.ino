// Define the pins for the HC-SR04 sensor
const int TrigPin = 9;
const int EchoPin = 10;

void setup() {
  // Initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  // Set the TrigPin as an output
  pinMode(TrigPin, OUTPUT);
  // Set the EchoPin as an input
  pinMode(EchoPin, INPUT);
}

void loop() {
  // Clear the TrigPin by setting it LOW for 2 microseconds
  digitalWrite(TrigPin, LOW);
  delayMicroseconds(2);

  // Set the TrigPin HIGH for 10 microseconds to send a pulse
  digitalWrite(TrigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(TrigPin, LOW);

  // Measure the duration of the pulse on the EchoPin
  long duration = pulseIn(EchoPin, HIGH);

  // Calculate the distance in centimeters
  // The speed of sound is 343 meters per second, or 0.0343 cm/microsecond.
  // The pulse travels to the object and back, so divide by 2.
  float distanceCm = duration * 0.0343 / 2;

  // Print the distance to the serial monitor
  Serial.print("Distance: ");
  Serial.print(distanceCm);
  Serial.println(" cm");

  // Wait for a short period before the next measurement
  delay(100);
}
