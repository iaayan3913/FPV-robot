// --- HARDWARE PIN CONFIGURATION ---
const int MOTOR_PWM_PIN = 9;  // L293D Pin 1 (Speed/Enable)
const int MOTOR_IN1_PIN = 4;  // L293D Pin 2 (Direction A)
const int MOTOR_IN2_PIN = 5;  // L293D Pin 7 (Direction B)
const int ENCODER_A_PIN = 2;  // Encoder Phase A (Must be Pin 2 on the Uno)

// 'volatile' ensures the Arduino updates this variable instantly inside the interrupt
volatile unsigned long pulse_count = 0;

// --- HARDWARE INTERRUPT ROUTINE ---
// This function executes instantly in the background every time the magnet spins past the sensor
void encoder_isr() {
  pulse_count++; 
}

void setup() {
  Serial.begin(9600);
  Serial.println("==================================================");
  Serial.println("     INITIALIZING SINGLE TT MOTOR + ENCODER TEST   ");
  Serial.println("==================================================");

  // Configure L293D control pins as outputs
  pinMode(MOTOR_PWM_PIN, OUTPUT);
  pinMode(MOTOR_IN1_PIN, OUTPUT);
  pinMode(MOTOR_IN2_PIN, OUTPUT);

  // Configure encoder pin with internal pull-up to keep the signal stable
  pinMode(ENCODER_A_PIN, INPUT_PULLUP);

  // Attach our interrupt handler to physical Pin 2
  // RISING means it triggers every time the signal goes from Low (0V) to High (5V)
  attachInterrupt(digitalPinToInterrupt(ENCODER_A_PIN), encoder_isr, RISING);

  delay(1000);
}

void loop() {
  // Test Phase 1: Forward Sweep
  Serial.println("\n[PHASE 1] Driving FORWARD at 70% speed for 3 seconds...");
  pulse_count = 0; // Reset counter before the test
  driveMotor(180, "forward"); // PWM values range from 0 (stopped) to 255 (max speed)
  delay(3000);
  driveMotor(0, "stop");
  
  Serial.print("--> Phase 1 Complete. Total Pulses Logged: ");
  Serial.println(pulse_count);
  delay(1500);

  // Test Phase 2: Reverse Sweep
  Serial.println("\n[PHASE 2] Driving BACKWARD at 70% speed for 3 seconds...");
  pulse_count = 0; // Reset counter
  driveMotor(180, "backward");
  delay(3000);
  driveMotor(0, "stop");
  
  Serial.print("--> Phase 2 Complete. Total Pulses Logged: ");
  Serial.println(pulse_count);
  delay(1500);

  // Test Phase 3: Real-Time Speed Tracking Loop
  Serial.println("\n[PHASE 3] Live Stream: Monitoring Clicks Per Second...");
  driveMotor(200, "forward"); // Keep motor spinning constant
  
  for (int i = 0; i < 5; i++) {
    pulse_count = 0; // Reset every second to calculate speed
    delay(1000);     // Wait exactly 1 second
    Serial.print("  Second ");
    Serial.print(i + 1);
    Serial.print(": Clicks seen = ");
    Serial.println(pulse_count);
  }
  
  driveMotor(0, "stop");
  Serial.println("\nDiagnostic round complete! Restarting sequence in 5 seconds...");
  delay(5000);
}

// --- MOTOR CONTROL HELPER FUNCTION ---
void driveMotor(int speed, String direction) {
  analogWrite(MOTOR_PWM_PIN, speed); // Sends the PWM speed signal to L293D Pin 1
  
  if (direction == "forward") {
    digitalWrite(MOTOR_IN1_PIN, HIGH);
    digitalWrite(MOTOR_IN2_PIN, LOW);
  } 
  else if (direction == "backward") {
    digitalWrite(MOTOR_IN1_PIN, LOW);
    digitalWrite(MOTOR_IN2_PIN, HIGH);
  } 
  else { // Default to stop safety state
    digitalWrite(MOTOR_IN1_PIN, LOW);
    digitalWrite(MOTOR_IN2_PIN, LOW);
    analogWrite(MOTOR_PWM_PIN, 0);
  }
}