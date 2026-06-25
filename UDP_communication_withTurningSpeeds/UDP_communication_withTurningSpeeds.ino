/*
 * Arduino Nano ESP32 — Verified Modular Motor Drive Core
 */

#include <WiFi.h>
#include <WiFiUdp.h>

// H-Bridge Pin Mapping (Optimized for TB6612FNG profiles)
const int AIN1 = 2;  const int AIN2 = 4;  const int PWMA = 3; 
const int BIN1 = 7;  const int BIN2 = 8;  const int PWMB = 6; 
const int STBY = 5;
const int driveSpeed = 150; // corresponds to 5.6V with 6v tt motors
const int turnSpeed = 90 ; // around 3.4 V. minimum is 3v 
const int backSpeed = 100; // make reversing slower 



const char* WIFI_SSID = "WIFI NAME HERE";  
const char* WIFI_PASS = "WIFI PASSWORD HERE";  

WiFiUDP udp;
unsigned int localPort = 9999; 
char packetBuffer[255];

// --- Sub-Movement Operations ---
void moveForward() {
  digitalWrite(STBY, HIGH); // Wake up the chip gates
  digitalWrite(AIN1, HIGH); digitalWrite(AIN2, LOW);
  digitalWrite(BIN1, HIGH); digitalWrite(BIN2, LOW);
  analogWrite(PWMA, driveSpeed); analogWrite(PWMB, driveSpeed);
}

void moveBackward() {
  digitalWrite(STBY, HIGH); 
  digitalWrite(AIN1, LOW);  digitalWrite(AIN2, HIGH);
  digitalWrite(BIN1, LOW);  digitalWrite(BIN2, HIGH);
  analogWrite(PWMA, backSpeed); analogWrite(PWMB, backSpeed);
}

void spinLeft() {
  digitalWrite(STBY, HIGH); 
  digitalWrite(BIN1, HIGH);  digitalWrite(BIN2, LOW);
  digitalWrite(AIN1, LOW); digitalWrite(AIN2, HIGH);
  analogWrite(PWMA, turnSpeed); analogWrite(PWMB, turnSpeed);
}

void spinRight() {
  digitalWrite(STBY, HIGH); 
  digitalWrite(BIN1, LOW); digitalWrite(BIN2, HIGH);
  digitalWrite(AIN1, HIGH);  digitalWrite(AIN2, LOW);
  analogWrite(PWMA, turnSpeed); analogWrite(PWMB, turnSpeed);
}

void stopMotors() {
  analogWrite(PWMA, 0); 
  analogWrite(PWMB, 0);
  digitalWrite(STBY, LOW); // Cut all physical power to the motor coils
}

// --- Driver Router Suite ---
void executeDriveVector(char directive) {
  switch(directive) {
    case 'F': // FORWARD
      moveForward();
      break;
    case 'B': // REVERSE
      moveBackward();
      break;
    case 'L': // STEER LEFT
      spinLeft();
      break;
    case 'R': // STEER RIGHT
      spinRight();
      break;
    case 'S': // HARD STOP
      stopMotors();
      break;
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000); 

  // Mount Pin Structures
  pinMode(AIN1, OUTPUT); pinMode(AIN2, OUTPUT); pinMode(PWMA, OUTPUT);
  pinMode(BIN1, OUTPUT); pinMode(BIN2, OUTPUT); pinMode(PWMB, OUTPUT);
  pinMode(STBY, OUTPUT); 
  
  stopMotors(); // Safe start: Keep car locked until packet verified

  Serial.println("\n==================================================");
  Serial.println("   ARDUINO NANO ESP32: LIVE MOTOR SYSTEM LINK    ");
  Serial.println("==================================================");

  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to network: ");
  Serial.println(WIFI_SSID);
  
  int timeoutCounter = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    timeoutCounter++;
    
    if(timeoutCounter > 30) {
      Serial.println("\n[ERROR]: Wi-Fi Connection Timeout.");
      while(true) delay(1000);
    }
  }
  
  udp.begin(localPort);
  
  Serial.println("\n\n>>> SYSTEM CHASSIS ONLINE <<<");
  Serial.print("Target IP Address: ");
  Serial.println(WiFi.localIP().toString());
}

void loop() {
  int packetSize = udp.parsePacket();
  if (packetSize) {
    int len = udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0; 
      Serial.print("Vector Log: [ ");
      Serial.print(packetBuffer);
      Serial.println(" ]");
      
      // FIXED: Added [0] index accessor to pull just the individual char symbol out
      executeDriveVector(packetBuffer[0]); 
    }
  }
}
