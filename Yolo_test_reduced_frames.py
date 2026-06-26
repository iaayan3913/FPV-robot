import cv2
from ultralytics import YOLO

# 1. Load the model
model = YOLO("yolov8n.pt") 

# Target your phone's stream
droidcam_url = ""
cap = cv2.VideoCapture(droidcam_url)

# Optimize OpenCV internal buffering
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

print("Starting AI Cockpit Core... Press 'q' to exit.")

frame_count = 0
annotated_frame = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Dropped frame or lost connection.")
        break
    
    frame_count += 1
    
    # Standard orientation transformations
    rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    resized_frame = cv2.resize(rotated_frame, (640, 480))
    
    # 2. FRAME SKIPPING SWITCH: Only run the heavy AI model every 4th frame
    if frame_count % 4 == 0 or annotated_frame is None:
        # Run inference with low resolution to maximize speed
        results = model(resized_frame, stream=True, imgsz=320, verbose=False)
        for r in results:
            annotated_frame = r.plot()
            
            # --- This is where your autonomous tracking logic lives! ---
            # (Loop through r.boxes here to send your 'L', 'R', 'F' commands)

    # 3. CRITICAL: Avoid window freezing by refreshing the UI instantly
    # We display the last known annotated frame to keep the video layout moving smoothly
    if annotated_frame is not None:
        cv2.imshow("AI Object Detection Feed", annotated_frame)
    else:
        cv2.imshow("AI Object Detection Feed", resized_frame)
        
    # Changing waitKey from 30ms to 1ms keeps the OS window responsive
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Cockpit closed safely.")
