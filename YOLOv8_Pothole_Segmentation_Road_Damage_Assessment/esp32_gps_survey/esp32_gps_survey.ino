// ESP32 + NEO-6M GPS -> JSON-over-USB-serial for road_survey.py, plus Bluetooth car control
// Wiring: NEO-6M TX -> GPIO16 (RX2), NEO-6M RX -> GPIO17 (TX2), VCC -> 3.3V/5V, GND -> GND
// Motor driver: IN1 -> GPIO32, IN2 -> GPIO33, IN3 -> GPIO25, IN4 -> GPIO26
// Status LED on GPIO13: solid ON = fix locked, blinking = searching for fix
// Library: TinyGPSPlus (Arduino Library Manager -> "TinyGPSPlus" by Mikal Hart)
// Bluetooth: pair with "My Bluetooth Car", send F/B/L/R/S

#include <TinyGPSPlus.h>
#include <BluetoothSerial.h>

static const int RXPin = 16, TXPin = 17;
static const uint32_t GPSBaud = 9600;
static const int STATUS_LED = 13;
static const uint32_t HOST_BAUD = 115200;  // must match SERIAL_BAUD in road_survey.py

#define IN1 32
#define IN2 33
#define IN3 25
#define IN4 26

TinyGPSPlus gps;
HardwareSerial gpsSerial(2);
BluetoothSerial SerialBT;

unsigned long lastBlink = 0;
bool ledState = false;

void setMotors(int a, int b, int c, int d) {
  digitalWrite(IN1, a);
  digitalWrite(IN2, b);
  digitalWrite(IN3, c);
  digitalWrite(IN4, d);
}

void setup() {
  Serial.begin(HOST_BAUD);
  gpsSerial.begin(GPSBaud, SERIAL_8N1, RXPin, TXPin);
  pinMode(STATUS_LED, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  SerialBT.begin("My Bluetooth Car");
}

void loop() {
  if (SerialBT.available()) {
    switch (SerialBT.read()) {
      case 'F': setMotors(HIGH, LOW, HIGH, LOW); break;  // forward
      case 'B': setMotors(LOW, HIGH, LOW, HIGH); break;  // backward
      case 'L': setMotors(LOW, HIGH, HIGH, LOW); break;  // left
      case 'R': setMotors(HIGH, LOW, LOW, HIGH); break;  // right
      case 'S': setMotors(LOW, LOW, LOW, LOW); break;    // stop
    }
  }

  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
  }

  if (gps.location.isValid()) {
    digitalWrite(STATUS_LED, HIGH);
    if (gps.location.isUpdated()) {
      Serial.print("{\"lat\":");
      Serial.print(gps.location.lat(), 6);
      Serial.print(",\"lon\":");
      Serial.print(gps.location.lng(), 6);
      Serial.println("}");
    }
  } else if (millis() - lastBlink >= 500) {
    // no fix yet: blink while searching
    lastBlink = millis();
    ledState = !ledState;
    digitalWrite(STATUS_LED, ledState);
  }
}
