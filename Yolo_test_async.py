import cv2
import threading
import time
import sys
from ultralytics import YOLO

# 1. Load the lightweight Nano AI model
model = YOLO("yolov8n.pt") 

# Target your phone's stream
#droidcam_url = ""

# hotspot ip
droidcam_url = ""

# Global variables for thread-safe memory sharing
latest_frame = None
running = True

def video_stream_worker():
    """Background Thread: Keeps the camera buffer completely clear to eliminate lag."""
    global latest_frame, running
    print("Connecting to DroidCam video stream...")
    cap = cv2.VideoCapture(droidcam_url)
    
    # Crucial low-latency configuration tweak
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("Error: Could not open camera stream.")
        running = False
        return

    print("Camera Stream Successfully Connected!")

    while running:
        ret, frame = cap.read()
        if not ret:
            print("Dropped frame or lost connection to phone.")
            running = False
            break
        
        # Instantly update the global pointer with the raw frame
        latest_frame = frame

    cap.release()

# Launch the background frame-consumer thread immediately
thread = threading.Thread(target=video_stream_worker, daemon=True)
thread.start()

# Give the hardware video channel a brief moment to stabilize
time.sleep(1)

frame_count = 0
annotated_frame = None

print("\n=== AI COCKPIT ONLINE ===")
print("Processing object detection... Press 'q' to exit safely.")

# --- MAIN ENGINE / DISPLAY LOOP ---
while running:
    if latest_frame is not None:
        frame_count += 1
        
        # Clone the latest frame safely to protect memory threads
        local_copy = latest_frame.copy()
        
        # Standard structural spatial transformations
        rotated_frame = cv2.rotate(local_copy, cv2.ROTATE_90_CLOCKWISE)
        resized_frame = cv2.resize(rotated_frame, (640, 480))
        
        # Only run the heavy YOLO neural network every 3rd frame
        if frame_count % 3 == 0 or annotated_frame is None:
            # imgsz=320 downsamples the inner array, speeding up processing by ~300%
            results = model(resized_frame, stream=True, imgsz=320, verbose=False)
            for r in results:
                annotated_frame = r.plot()
                
                # ==================================================
                # YOUR AUTONOMOUS STEERING CONTROLS LIVE HERE!
                # E.g., read r.boxes to send 'F', 'L', 'R', or 'S'
                # ==================================================

        # Display the AI-processed overlay frame if it exists
        if annotated_frame is not None:
            cv2.imshow("AI Object Detection Feed", annotated_frame)
        else:
            cv2.imshow("AI Object Detection Feed", resized_frame)

    # 2. THE OS CRASH FIX: waitKey(1) tells the OS the window is alive and healthy
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        print("\nShutting down AI engine dashboard...")
        running = False
        break

# Cleanup environment on execution finish
cv2.destroyAllWindows()
sys.exit()
