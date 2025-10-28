// Include Library
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>

// ==================== DEFINISI KONSTANTA & VARIABEL ====================

// --- Definisi Pesan Serial ---
const char* MSG_TRIGGER_RASPI = "3";
const char* MSG_ORGANIK = "0";
const char* MSG_NONORGANIK = "1";
const char* MSG_CAMPURAN = "2";
const char* MSG_ERROR = "00";

// --- Konfigurasi Sensor HC-SR04 ---
const int HCSR_TRIG_PIN = 9;
const int HCSR_ECHO_PIN = 10;
const float INITIAL_DISTANCE = 34.78;
const float DISTANCE_THRESHOLD = INITIAL_DISTANCE - 5.0; // Threshold untuk deteksi sampah

// --- Konfigurasi Motor Stepper (berdasarkan stepper_motor.ino) ---
const int STEP_PIN = 3;
const int DIR_PIN = 4;
const int STEPS_ORGANIK = 0;      // 0 step
const int STEPS_NONORGANIK = 72;  // 66 step
const int STEPS_CAMPURAN = 132;   // 132 step
const int STEPS_PER_REV = 200;    // step motor 1,8°
const int RPM = 40;               // kecepatan putaran
const int STEP_DELAY = 60L * 1000L * 1000L / STEPS_PER_REV / RPM / 2; // delay per setengah pulsa (micro-second)

// --- Konfigurasi Motor Servo ---
const int SERVO_PIN = 6;
const int SERVO_CLOSE_POS = 73;
const int SERVO_OPEN_POS = 0;

// --- Konfigurasi LCD I2C ---
LiquidCrystal_I2C lcd(0x27, 16, 2);

// --- Konfigurasi Servo ---
Servo gateServo;

// ==================== FUNGSI SETUP ====================

void setup() {
  // Inisialisasi Serial Komunikasi
  Serial.begin(9600);
  Serial.println("Sistem Pemilah Sampah Siap.");

  // Inisialisasi LCD
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("Sistem Siap");
  lcd.setCursor(0, 1);
  lcd.print("Menunggu Sampah");

  // Inisialisasi Pin Sensor HC-SR04
  pinMode(HCSR_TRIG_PIN, OUTPUT);
  pinMode(HCSR_ECHO_PIN, INPUT);

  // Inisialisasi Pin Motor Stepper
  pinMode(DIR_PIN, OUTPUT);
  pinMode(STEP_PIN, OUTPUT);

  // Inisialisasi Motor Servo
  gateServo.attach(SERVO_PIN);
  gateServo.write(SERVO_CLOSE_POS); // Pastikan gerbang tertutup di awal
}

// ==================== FUNGSI LOOP UTAMA ====================

void loop() {
  float currentDistance = measureDistance();
  // 1. Cek jika ada sampah yang masuk (jarak berkurang signifikan)
  if (currentDistance < DISTANCE_THRESHOLD) {
    lcd.clear();
    lcd.print("Sampah Terdeteksi");
    
    // 2. Kirim trigger ke Raspberry Pi
    Serial.println(MSG_TRIGGER_RASPI);
    
    // 3. Tunggu balasan dari Raspberry Pi
    lcd.setCursor(0, 1);
    lcd.print("Menganalisis...");
    
    while (Serial.available() == 0) {
      // Tunggu hingga ada data serial yang masuk
    }
    
    String response = Serial.readStringUntil('\n');
    response.trim();
    
    int stepsToMove = 0;
    
    // 4. Proses pesan dari Raspberry Pi
    if (response == MSG_ORGANIK) {
      lcd.clear();
      lcd.print("Jenis: Organik");
      stepsToMove = STEPS_ORGANIK;
    } else if (response == MSG_NONORGANIK) {
      lcd.clear();
      lcd.print("Jenis: Anorganik");
      stepsToMove = STEPS_NONORGANIK;
    } else if (response == MSG_CAMPURAN) {
      lcd.clear();
      lcd.print("Jenis: Campuran");
      stepsToMove = STEPS_CAMPURAN;
    } else if (response == MSG_ERROR) {
      lcd.clear();
      lcd.print("Jenis: Invalid");
      delay(500);
      lcd.clear();
      lcd.print("Jenis: Campuran");
      stepsToMove = STEPS_CAMPURAN;
    }else {
      lcd.clear();
      lcd.print("Pesan Tdk Dikenal");
      delay(2000); // Tampilkan pesan error sejenak
      resetToWaiting();
      return; // Kembali ke awal loop
    }
    
    delay(1000); // Jeda agar pesan di LCD terbaca

    // 5. Putar motor stepper sesuai jenis sampah
    if (stepsToMove > 0) {
      lcd.setCursor(0, 1);
      lcd.print("Memutar wadah...");
      rotateStepper(stepsToMove, HIGH);
    }
    
    // 6. Buka dan tutup gerbang servo
    lcd.setCursor(0, 1);
    lcd.print("Membuka gerbang ");
    gateServo.write(SERVO_OPEN_POS);
    delay(1000);
    
    lcd.setCursor(0, 1);
    lcd.print("Menutup gerbang ");
    gateServo.write(SERVO_CLOSE_POS);
    delay(1000);
    
    // 7. Kembalikan motor stepper ke posisi awal
    if (stepsToMove > 0) {
      lcd.setCursor(0, 1);
      lcd.print("Kembali ke awal ");
      rotateStepper(stepsToMove, LOW);
    }
    
    // 8. Kembali ke siklus awal
    resetToWaiting();
  }
  
  // Beri jeda singkat antar pengukuran untuk stabilitas sensor
  delay(100); 
}

// ==================== FUNGSI BANTUAN ====================

/**
 * Mengukur jarak menggunakan sensor HC-SR04.
 * @return Jarak dalam sentimeter (cm).
 */
float measureDistance() {
  digitalWrite(HCSR_TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(HCSR_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(HCSR_TRIG_PIN, LOW);
  
  long duration = pulseIn(HCSR_ECHO_PIN, HIGH);
  float distance = duration * 0.0343 / 2;
  return distance;
}

/**
 * Menggerakkan motor stepper.
 * @param steps Jumlah langkah.
 * @param direction Arah putaran (HIGH atau LOW).
 */
void rotateStepper(int steps, bool direction) {
  digitalWrite(DIR_PIN, direction);
  for (int i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(STEP_DELAY);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(STEP_DELAY);
  }
}

/**
 * Mengatur ulang tampilan LCD ke status menunggu.
 */
void resetToWaiting() {
  lcd.clear();
  lcd.print("Sistem Siap");
  lcd.setCursor(0, 1);
  lcd.print("Menunggu Sampah");
  delay(1000); // Beri jeda agar tidak langsung mendeteksi sampah yang sama
}
