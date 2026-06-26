import cv2
from ultralytics import YOLO

# 1. Load the pre-trained lightweight AI model
model = YOLO("yolov8n.pt") 

# 2. Target your Honor 10 Lite DroidCam stream
droidcam_url = ""
cap = cv2.VideoCapture(droidcam_url)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break
    
    # Optional: Rotate and resize just like your existing script
    rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    resized_frame = cv2.resize(rotated_frame, (640, 480))
    
    # 3. Pass the raw image directly into the Neural Network
    # stream=True optimizes the video buffer pipeline for real-time tracking
    results = model(resized_frame, stream=True)
    
    for r in results:
        # Generate an image with the AI's bounding boxes overlayed onto it
        annotated_frame = r.plot()
        
    # Display the AI's view in your cockpit window
    cv2.imshow("AI Object Detection Feed", annotated_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
