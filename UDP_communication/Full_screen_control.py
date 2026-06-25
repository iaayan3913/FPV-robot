import cv2
import socket

# ==========================================
# 1. HARDWARE NETWORK CONFIGURATION
# ==========================================
# Replace this with the exact IP your Arduino Nano ESP32 displays on startup:
ROBOT_IP = "INSERT ROBOT IP ADDRESS"  
ROBOT_PORT = 9999

# DroidCam stream URL from your Honor 10 Lite
droidcam_url = "INSERT DROIDCAM IP HERE"

# Initialize a standard, blazing-fast UDP Network Socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Helper function to safely transmit command characters over the network
def send_command(char_cmd):
    try:
        # Convert the string letter into raw bytes and send it
        udp_socket.sendto(char_cmd.encode('utf-8'), (ROBOT_IP, ROBOT_PORT))
    except Exception as e:
        print(f"Network Send Error: {e}")

# ==========================================
# 2. CONNECT TO CAMERA STREAM
# ==========================================
print("Connecting to DroidCam stream...")
cap = cv2.VideoCapture(droidcam_url)

if not cap.isOpened():
    print("Error: Could not open DroidCam. Check IP/Port or app status.")
    exit()

print("Connected successfully!")
print("\n=== DRIVING CONTROLS IN THE VIDEO WINDOW ===")
print("  W -> Forward  |  S -> Backward")
print("  A -> Turn Left |  D -> Turn Right")
print("  Spacebar ------> STOP")
print("  Q -------------> Quit Application")
print("============================================")

# Track the last sent command to avoid spamming duplicate network packets
last_command = 'X'

# ==========================================
# 3. MASTER REAL-TIME CONTROL LOOP
# ==========================================
while True:
    ret, frame = cap.read()
    if not ret:
        print("Dropped frame or lost connection to phone.")
        break
        
    # Rotate frame for horizontal processing layout
    rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
    # Resize frame to keep network processing lag low
    display_frame = cv2.resize(rotated_frame, (640, 480))
    
    # Render the video stream frame onto your desktop
    cv2.imshow("Robot FPV Cockpit", display_frame)
    
    # ------------------------------------------
    # 4. INTEGRATED KEYBOARD COMMAND ROUTER
    # ------------------------------------------
    # cv2.waitKey(20) waits 20 milliseconds for a key press inside the video window
    key = cv2.waitKey(20) & 0xFF
    
    current_command = None

    if key == ord('w'):
        current_command = 'W'
    elif key == ord('s'):
        current_command = 'S'
    elif key == ord('a'):
        current_command = 'A'
    elif key == ord('d'):
        current_command = 'D'
    elif key == ord(' '):  # Spacebar forces an emergency stop
        current_command = 'X'
    elif key == ord('q'):  # Safe script exit trigger
        print("\nExiting cockpit engine...")
        send_command('X') # Ensure robot stops moving when you close the app
        break

    # If a valid driving key was hit, and it's different from the last sent command, transmit it!
    if current_command and current_command != last_command:
        send_command(current_command)
        print(f"Sent Command -> [{current_command}]")
        last_command = current_command

# ==========================================
# 5. CLEANUP & SHUTDOWN
# ==========================================
cap.release()
cv2.destroyAllWindows()
udp_socket.close()
print("Stream and network channels closed safely.")
