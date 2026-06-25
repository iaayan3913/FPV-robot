import cv2

# 1. Define the DroidCam stream endpoint (include the crucial /video suffix)
# Replace this with the exact IP address currently on your phone's screen
droidcam_url = "http://192.168.0.12:4747/video"

# 2. Connect OpenCV to the phone's network stream
print("Connecting to DroidCam stream...")
cap = cv2.VideoCapture(droidcam_url)

# Check if the stream opened successfully
if not cap.isOpened():
    print("Error: Could not open the DroidCam stream. Check your IP address or if DroidCam Client is still open.")
    exit()

print("Connected successfully! Press 'q' in the video window to quit.")

# 3. Start the real-time frame capture loop
while True:
    # Capture the latest frame from the phone
    ret, frame = cap.read()
    
    # If the frame was not grabbed correctly, break the loop
    if not ret:
        print("Dropped frame or lost connection to phone.")
        break
        
    # 4. ROTATE THE FRAME FOR VERTICAL PHONE MOUNTING
    # This turns the tall/skinny portrait view into a proper wide landscape view.
    # Options: cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE, or cv2.ROTATE_180
    rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
    # 5. Scale the window down to keep processing fast
    # We resize the ROTATED frame so it stays crisp and highly responsive for driving.
    display_frame = cv2.resize(rotated_frame, (640, 480))
    
    # 6. Display the feed in a dedicated window
    cv2.imshow("Robot FPV Cockpit", display_frame)
    
    # 7. Break the loop immediately if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 8. Clean up memory and close the window when exiting
cap.release()
cv2.destroyAllWindows()
print("Stream closed safely.")