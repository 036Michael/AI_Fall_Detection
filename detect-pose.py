import cv2
from ultralytics import YOLO
import time
from datetime import datetime
import pandas as pd
 
# 匯入自定義常數
from constants import body_parts_colors 

# 匯入自己的函式庫
from utils import timeFormat,draw_text
from logic import fall_detection

# Load YOLOv8 pose model
model = YOLO('yolov8m-pose.pt')

# 將顏色轉換為 OpenCV 格式
colors = [color[::-1] for color in body_parts_colors.values()] # 將顏色轉換為 RGB 格式
body_parts_names = [names[::1] for names in body_parts_colors.keys()] # 部位名稱

with open("fall.txt", "a") as f:
    f.write("23行開始\n")

cap = cv2.VideoCapture(0) 

def process_frame(frame):
    global fall_start_time  # 確保可以修改全域變數 fall_start_time

    # Predict using YOLO model

    results = model.track(source=frame, conf=0.7)
    _, ss, label = timeFormat()

    draw_text(frame, ss + label, font_scale=1,
                  pos=(10, 10), text_color_bg=(255, 0, 0))

    # 偵測跌倒

    # 偵測人臉
    # Extract keypoints and bounding boxes from the results
    for result in results:
        if len(result.keypoints) > 0 and len(result.boxes) > 0:
            keypoints = result.keypoints.xy.tolist()[0]  # Assuming only one person is detected
            boxes = result.boxes.xyxy.tolist()[0]

            frame = result.plot(kpt_line=True,boxes=False,labels=False)

            # Draw keypoints and bounding boxes
            for i, (x, y) in enumerate(keypoints):
                x = int(x)
                y = int(y)
                cv2.circle(frame, (x, y), 4, colors[i], -1)
                cv2.putText(frame, str(i), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i], 2)

            frame = fall_detection(frame,keypoints,boxes) 
            
    return frame

def main():
    """主函數，處理影像流"""
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 處理影像並顯示
        frame = process_frame(frame)
        cv2.imshow('Fall Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()