# Modular FPV Robotic Vehicle

A full-stack, decentralized mechatronics platform featuring a low-latency wireless First-Person View (FPV) cockpit and real-time remote teleoperation. This architecture decouples low-level hardware execution from high-level cognitive processing, serving as a platform ready for future projects such as advanced computer vision and autonomous navigation tasks.

---

## 🚀 System Architecture & Overview

This project implements a **Decentralized Control Architecture** to maximize computational efficiency. Instead of forcing an onboard chip to handle intensive processes, the workload is distributed across dedicated nodes over a network:

* **The Edge Node (Arduino Nano ESP32):** Manages time-sensitive, deterministic hardware tasks. It listens asynchronously to incoming network data buffers and immediately translates them into localized PWM duty cycles and motor direction states.
* **The Vision Node (Honor 10 Lite):** Operates as a hardware-accelerated IP streaming node, capturing and broadcasting live video frames over a high-bandwidth network.
* **The Host Node (Laptop Controller):** Acts as the central intelligence hub. It handles the video decompression, manages the graphical user interface, and captures continuous keyboard matrix inputs without blocking network pathways.

---

## 🛠️ Hardware Specifications

| Component | Purpose / Configuration |
| :--- | :--- |
| **Microcontroller** | Arduino Nano ESP32 (3.3V Native Logic, Built-in Wi-Fi) |
| **Motor Driver** | TB6612FNG Dual H-Bridge (High-Efficiency MOSFET Stage) |
| **Actuators** | Interchangeable Drivetrain (6V Plastic TT Motors / 1:90 Metal Encoder Motors) |
| **Power Supply** | 9.6V Rechargeable Battery Pack (Coil Power) + 5V USB/VBUS (Logic Power) |
| **Sensors / Cam** | Honor 10 Lite Smartphone (Streaming FPV feed via DroidCam over 5GHz Wi-Fi) |
| **Chassis** | Custom CAD-modeled, 3D-printed modular structural mounts |

---

## 🔌 Hardware Wiring Diagram
```
  +-------------------------------------------------------+
  |               9.6V Battery Pack (+)                   |
  +---------------------------+---------------------------+
                              |
                              v
                        [TB6612FNG VM]


[Arduino Nano ESP32]                                      [TB6612FNG Driver]
3V3 Pin  -------------------------------------------> VCC (Logic Power)
GND Pin  -------------------------------------------> GND (Common Ground)
Pin D4   -------------------------------------------> AIN1
Pin D5   -------------------------------------------> AIN2
Pin D6   (PWM Capable) -----------------------------> PWMA
Pin D7   -------------------------------------------> BIN1
Pin D8   -------------------------------------------> BIN2
Pin D10  (PWM Capable) -----------------------------> PWMB
Pin D9   -------------------------------------------> STBY (Standby)

[Drivetrain Outputs]
AO1 / AO2 ------------------------------------------> Left Motor Terminals
BO1 / BO2 ------------------------------------------> Right Motor Terminals
```

*Note: Ensure the negative line (-) of the 9.6V battery, the TB6612FNG ground pins, and the Nano ESP32 ground pins are all tied to a single common ground rail.*

---

## 🌐 Network Protocol & Communication

The host controller and edge node communicate using a custom, lightweight, fire-and-forget **UDP (User Datagram Protocol)** structure on port `9999`. Because UDP avoids the packet-delivery verification overhead inherent to TCP, control latency is kept down to single-digit milliseconds.

### Control Vectors Dispatched:
* `F` : Drive both motor channels forward
* `B` : Reverse both motor channels
* `L` : Axial spin left (Left reverse, Right forward)
* `R` : Axial spin right (Left forward, Right reverse)
* `S` : Fail-safe Hard Stop (Cuts power to motor coils; puts driver in Standby)

---
    
### 🎮 Driving Instructions

Click your mouse cursor **inside** the generated Pygame/OpenCV Cockpit window to give it active operating system focus. Use the standard **WASD** layout to drive, and release the keys or exit the frame window to engage the automatic software brakes.
