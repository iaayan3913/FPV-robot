// --- HARDWARE PIN CONFIGURATION ---
const int ENCODER_A_PIN = 2;  // Must be Pin 2 on the Uno for External Interrupts

// 'volatile' tells the processor that this number changes instantly inside the background interrupt routine
volatile unsigned long pulse_count = 0;

// Variables to handle printing the data exactly every 1 second
unsigned long last_print_time = 0;
unsigned long last_pulse_count = 0;

// --- HARDWARE INTERRUPT SERVICE ROUTINE ---
// This code is invisible and fires instantly every single time the magnet passes the sensor
void encoder_isr() {
  pulse_count++; 
}

void setup() {
  Serial.begin(9600);
  Serial.println("==================================================");
  Serial.println("          LIVE UNO ENCODER PULSE COUNTER          ");
  Serial.println("==================================================");
  Serial.println("Spin the wheel by hand to see the counts change...");

  // Configure the encoder pin with the internal pull-up resistor to prevent signal floating
  pinMode(ENCODER_A_PIN, INPUT_PULLUP);

  // Attach Pin 2 to our background counter function
  // RISING triggers on the leading edge of every digital pulse pulse
  attachInterrupt(digitalPinToInterrupt(ENCODER_A_PIN), encoder_isr, RISING);
}

void loop() {
  unsigned long current_time = millis();

  // Check if exactly 1000 milliseconds (1 second) have passed
  if (current_time - last_print_time >= 1000) {
    
    // Temporarily pause interrupts for a microsecond to safely read the volatile variables
    noInterrupts();
    unsigned long current_pulses = pulse_count;
    interrupts(); // Re-enable interrupts instantly

    // Calculate how many pulses happened just within this past second
    unsigned long pulses_this_second = current_pulses - last_pulse_count;

    // Print the diagnostics to the Serial Monitor
    Serial.print("Total Absolute Pulses: ");
    Serial.print(current_pulses);
    Serial.print("  |  Pulses in last second (Speed): ");
    Serial.println(pulses_this_second);

    // Save the current states for the next 1-second math check
    last_pulse_count = current_pulses;
    last_print_time = current_time;
  }
}