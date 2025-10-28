// ---------- PIN MAP ----------
#define STEP_PIN  3     // D14
#define DIR_PIN   4      // D27
//#define EN_PIN    13      // D13 (aktif-LOW)

// ---------- KONSTAN ----------
const int stepsPerRev = 200;   // step motor 1,8°
const int rpm         = 60;    // kecepatan putaran
// delay per setengah pulsa (micro-second)
const int stepDelay   = 60L * 1000L * 1000L / stepsPerRev / rpm / 2;

/*================================================*/
void setup() {
  pinMode(STEP_PIN, OUTPUT);
  pinMode(DIR_PIN,  OUTPUT);
  //pinMode(EN_PIN,   OUTPUT);

  //digitalWrite(EN_PIN, LOW);   // 🔧 driver ON sejak awal
  Serial.begin(115200);
  Serial.println("A4988 ready – EN=D13, FULL-STEP");
}

/*================================================*/
void loop() {
  Serial.println("CW 1 revolusi");
  rotateSteps(stepsPerRev, true);
  delay(1000);

  Serial.println("CCW 1 revolusi");
  rotateSteps(stepsPerRev, false);
  delay(1000);
}

/*================================================*/
void rotateSteps(int steps, boolean clockwise) {
  digitalWrite(DIR_PIN, clockwise ? HIGH : LOW);

  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(stepDelay);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(stepDelay);
  }
}