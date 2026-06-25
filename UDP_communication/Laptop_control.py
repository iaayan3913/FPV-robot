import socket
import sys
import pygame

# --- HARDWARE TARGET INTERFACES ---
NANO_ESP32_IP = "192.168.0.34"  # this is the nanos ip address when connected to the wifi 
UDP_PORT = 9999                 # The control port matching the Nano ESP32 code

# Initialize high-speed UDP network socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Initialize Pygame window to capture keyboard vectors
pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("FPV Modular Dual-Core Control Suite")

print("-" * 50)
print(f"Targeting Motor Board Vector: {NANO_ESP32_IP}:{UDP_PORT}")
print("Click inside this window, then use WASD keys to drive!")
print("-" * 50)

def send_vector(command):
    sock.sendto(command.encode(), (NANO_ESP32_IP, UDP_PORT))

running = True
current_command = "S" # System begins in a Safe Stop state

while running:
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