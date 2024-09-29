import cv2
from ultralytics import YOLO

# Load YOLOv8 pose model
model = YOLO('yolov8n-pose.pt')

# Start video capture
cap = cv2.VideoCapture(2)  # Use the webcam as the source (index may vary)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Predict using YOLO model
    results = model.predict(source=frame, conf=0.8, show=False)

    # Extract keypoints and bounding boxes from the results
    for result in results:
        # Check if any persons are detected
        if len(result.keypoints) > 0 and len(result.boxes) > 0:
            # Extract keypoints and bounding box
            keypoints = result.keypoints.xy.tolist()[0]  # Assuming only one person is detected
            boxes = result.boxes.xyxy.tolist()[0]  # Extract the bounding box for the detected person
            x1, y1, x2, y2 = map(int, boxes)  # Convert the bounding box to integer values

            # Find coordinates of the keypoint (e.g., keypoints[0])
            if len(keypoints) > 0:
                head_x, head_y = keypoints[0]  # Coordinates of the specific keypoint (e.g., head)

                # Draw a gray rectangle from the keypoint down to the bottom of the bounding box
                top_left = (x1, int(head_y))
                bottom_right = (x2, y2)
                cv2.rectangle(frame, top_left, bottom_right, (128, 128, 128), thickness=-1)

            # Overlay the keypoints and other results on the frame
            frame = result.plot()

            # Debugging: print keypoints
            print("=" * 80)
            print("點：", keypoints)
            print("=" * 80)

    # Display the processed frame
    cv2.imshow('Grayscale Person Detection', frame)

    # Exit loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close display window
cap.release()
cv2.destroyAllWindows()
