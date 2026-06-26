import socket
import sys
import pygame
import cv2
import threading
import time
from ultralytics import YOLO

# --- HARDWARE TARGET INTERFACES ---
#NANO_ESP32_IP = "192.168.0.34"  # WIFI Nano ESP32 IP Address
NANO_ESP32_IP = "172.30.253.236" #Hotspot Nano ESP32 IP Address
UDP_PORT = 9999                 # The control port matching the Nano ESP32 code [cite: 6]
droidcam_url = "http://172.30.253.228:4747/video"

# 1. Initialize the lightweight AI Object Detection Model
print("Loading YOLOv8 Nano model...")
model = YOLO("yolov8n.pt")

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
pygame.display.set_caption("FPV Autonomous AI Tracking Cockpit")
font = pygame.font.SysFont("Arial", 18)

print("-" * 50)
print(f"Targeting Motor Board Vector: {NANO_ESP32_IP}:{UDP_PORT}")
print("AI Tracking Initialized. Keep the window focused to watch tracking states.")
print("-" * 50)

def send_vector(command):
    try:
        sock.sendto(command.encode(), (NANO_ESP32_IP, UDP_PORT))
    except Exception as e:
        print(f"Transmission Error: {e}")

current_command = "S" # System begins in a Safe Stop state
frame_count = 0
annotated_frame = None

# --- MAIN EXECUTOR LOOP ---
while running:
    # 1. Handle Window Closing Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 2. Process, Analyze, and Render the AI Video Frame inside Pygame
    if latest_raw_frame is not None:
        frame_count += 1
        
        # Copy frame locally to protect thread safety
        frame = latest_raw_frame.copy()
        
        # Apply your structural 3D-mount rotations and constraints
        rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        display_frame = cv2.resize(rotated_frame, (640, 480))
        
        # Default state: if no person is detected, look to stop the vehicle
        new_command = "S"
        
        # 3. Running Neural Network Inference (Every 3rd frame to optimize CPU load)
        if frame_count % 3 == 0 or annotated_frame is None:
            # imgsz=320 downsamples internally for a 3x processing boost
            results = model(display_frame, stream=True, imgsz=320, verbose=False)
            
            for r in results:
                # Grab a frame copy complete with YOLO's visual bounding boxes
                annotated_frame = r.plot()
                
                # Scan every single bounding box detected by the network
                for box in r.boxes:
                    class_id = int(box.cls[0]) # 0 = Person in COCO dataset
                    
                    if class_id == 0:
                        # Unpack boundary coordinates
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        
                        # Calculate center and pixel proximity width
                        person_center_x = (x1 + x2) / 2
                        person_box_width = x2 - x1
                        
                        # Draw a small blue marker on the target center point
                        cv2.circle(annotated_frame, (int(person_center_x), int((y1+y2)/2)), 6, (255, 0, 0), -1)
                        
                        # --- AUTONOMOUS ALIGNMENT AND CHASE LOGIC ---
                        if person_center_x < 270:
                            new_command = "L"  # Target left -> Spin left
                        elif person_center_x > 370:
                            new_command = "R"  # Target right -> Spin right
                        else:
                            # Target centered -> Check proximity safety threshold
                            if person_box_width < 370: 
                                new_command = "F"  # Far away -> Approach
                            elif person_box_width > 375:
                                new_command = "B"
                            else:
                                new_command = "S"  # Safe distance -> Brake
                        
                        # Target found. Break loop to stick to the primary subject
                        break

        # Render the current visual output buffer onto Pygame
        active_render_frame = annotated_frame if annotated_frame is not None else display_frame
        
        # Convert OpenCV BGR format to Pygame RGB format
        rgb_frame = cv2.cvtColor(active_render_frame, cv2.COLOR_BGR2RGB)
        
        # Convert the pixel array into a renderable Pygame Surface
        pygame_surface = pygame.surfarray.make_surface(rgb_frame.swapaxes(0, 1))
        screen.blit(pygame_surface, (0, 0))

    # 4. Render the Instruction Text Banner at the bottom
    pygame.draw.rect(screen, (30, 30, 30), (0, 480, 640, 60))
    
    hud_text = font.render("AI MODE: Autonomous Person Tracking Activated | Close Window to Quit", True, (255, 255, 255))
    vector_text = font.render(f"AI Dispatched Vector: [ {current_command} ]", True, (0, 255, 0) if current_command != "S" else (255, 0, 0))
    
    screen.blit(hud_text, (10, 490))
    screen.blit(vector_text, (10, 512))

    # 5. Continuous Network Dispatch Rule
    if new_command != current_command:
        current_command = new_command
        print(f"Autonomous Command Shift: [ {current_command} ]")
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