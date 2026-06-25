import socket
import sys
import pygame
import cv2
import threading
import time

# --- HARDWARE TARGET INTERFACES ---
NANO_ESP32_IP = "NANO IP HERE"  # Nano ESP32 IP Address
UDP_PORT = 9999                #The control port matching the Nano ESP32 code [cite: 6]
droidcam_url = "DROIDCAM IP HERE"

# Initialize high-speed UDP network socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Global variables to share data across background threads safely
latest_raw_frame = None
running = True

def video_buffer_purger():
    """Background Thread: Keeps OpenCV's frame buffer entirely empty to eliminate lag."""
    global latest_raw_frame, running
    print("Connecting to DroidCam video stream...")
    cap = cv2.VideoCapture(droidcam_url)
    
    # Force OpenCV to drop backlogged frames instead of queuing them
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("Error: Could not open DroidCam. Check IP/Port configuration.")
        running = False
        return

    print("Video Stream Connected Successfully!")

    while running:
        ret, frame = cap.read()
        if not ret:
            print("Dropped frame or lost connection to phone.")
            running = False
            break
        latest_raw_frame = frame

    cap.release()

# Spin up the video consumer thread instantly
video_thread = threading.Thread(target=video_buffer_purger, daemon=True)
video_thread.start()

# Give the camera a brief moment to stabilize initialization
time.sleep(1)

# --- INITIALIZE PYGAME COCKPIT UI ---
pygame.init()
# We size the Pygame window to 640x540 (480px for video + 60px text instruction banner)
screen = pygame.display.set_mode((640, 540))
pygame.display.set_caption("FPV Unified Pygame Cockpit")
font = pygame.font.SysFont("Arial", 18)

print("-" * 50)
print(f"Targeting Motor Board Vector: {NANO_ESP32_IP}:{UDP_PORT}")
print("Click inside the Pygame window. Video and controls are fully merged!")
print("-" * 50)

def send_vector(command):
    try:
        sock.sendto(command.encode(), (NANO_ESP32_IP, UDP_PORT))
    except Exception as e:
        print(f"Transmission Error: {e}")

current_command = "S" # System begins in a Safe Stop state

# --- MAIN EXECUTOR LOOP ---
while running:
    # 1. Handle Window Closing Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Process and Render the Lag-Free Video Frame inside Pygame
    if latest_raw_frame is not None:
        # Copy frame locally to protect thread safety
        frame = latest_raw_frame.copy()
        
        # Apply your structural 3D-mount rotations and constraints
        rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        display_frame = cv2.resize(rotated_frame, (640, 480))
        
        # Convert OpenCV BGR format to Pygame RGB format
        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        
        # Convert the pixel array into a renderable Pygame Surface
        pygame_surface = pygame.surfarray.make_surface(rgb_frame.swapaxes(0, 1))
        
        # Draw the video feed surface at the top-left (0,0) corner
        screen.blit(pygame_surface, (0, 0))

    # 3. Render the Instruction Text Banner at the bottom
    # Draw a dark gray background rectangle for the HUD banner
    pygame.draw.rect(screen, (30, 30, 30), (0, 480, 640, 60))
    
    hud_text = font.render("CONTROLS: WASD to Drive | Release Keys to Stop | Close Window to Quit", True, (255, 255, 255))
    vector_text = font.render(f"Active Dispatch Vector: [ {current_command} ]", True, (0, 255, 0) if current_command != "S" else (255, 0, 0))
    
    screen.blit(hud_text, (10, 490))
    screen.blit(vector_text, (10, 512))

    # 4. Continuous Pygame Key Matrix Scanner
    keys = pygame.key.get_pressed()
    new_command = "S" # Fail-safe: Default to stop if keys are released
    
    if keys[pygame.K_w]:
        new_command = "F" #Forward
    elif keys[pygame.K_s]:
        new_command = "B" # Backward
    elif keys[pygame.K_a]:
        new_command = "L" # Left Turn
    elif keys[pygame.K_d]:
        new_command = "R" # Right Turn

    # Only transmit over Wi-Fi if your active control vector shifts
    if new_command != current_command:
        current_command = new_command
        print(f"Dispatched Vector Shift: [ {current_command} ]")
        send_vector(current_command)

    # Refresh the Pygame display monitor
    pygame.display.flip()
    
    # Cap loop execution speed to protect laptop CPU cycles
    time.sleep(0.01)

# Safe shutdown routine
print("\nClosing master control architecture...")
send_vector("S")
pygame.quit()
sock.close()
sys.exit()
