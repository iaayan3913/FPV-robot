import socket
import sys
import pygame
import cv2

# --- HARDWARE TARGET INTERFACES ---
NANO_ESP32_IP = "192.168.0.34"  # this is the nanos ip address when connected to the wifi 
UDP_PORT = 9999                 # The control port matching the Nano ESP32 code

# Initialize high-speed UDP network socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
droidcam_url = "http://192.168.0.36:4747/video"

# Initialize Pygame window to capture keyboard vectors
pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("FPV Modular Dual-Core Control Suite")

print("-" * 50)
print(f"Targeting Motor Board Vector: {NANO_ESP32_IP}:{UDP_PORT}")
print("Click inside this window, then use WASD keys to drive!")
print("-" * 50)

print("Connecting to DroidCam stream...")
cap = cv2.VideoCapture(droidcam_url)

if not cap.isOpened():
    print("Error: Could not open DroidCam. Check IP/Port or app status.")
    exit()

print("Connected successfully!")

def send_vector(command):
    sock.sendto(command.encode(), (NANO_ESP32_IP, UDP_PORT))

running = True
current_command = "S" # System begins in a Safe Stop state

while running:

    ret, frame = cap.read()
    if not ret:
        print("Dropped frame or lost connection to phone.")
        break
        
    # Rotate frame for horizontal processing layout
    rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
    # Resize frame to keep network processing lag low
    display_frame = cv2.resize(rotated_frame, (640, 480))
    
    # Render the video stream frame onto your desktop
    cv2.imshow("Robot FPV Cockpit", display_frame)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    # Continuous key-state matrix scanning
    keys = pygame.key.get_pressed()
    new_command = "S" # Fail-safe: Default to stop if keys are released
    
    if keys[pygame.K_w]:
        new_command = "F" # Forward
    elif keys[pygame.K_s]:
        new_command = "B" # Backward
    elif keys[pygame.K_a]:
        new_command = "L" # Left Turn
    elif keys[pygame.K_d]:
        new_command = "R" # Right Turn

    # Only fire across the wireless network if the user changes inputs
    if new_command != current_command:
        current_command = new_command
        print(f"Dispatched Vector Shift: [ {current_command} ]")
        send_vector(current_command)

pygame.quit()
sys.exit()