import cv2
import os
import time
from datetime import datetime
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
import lineNotify
from shapely.geometry import Polygon, Point

send_notify = True

def timeFormat():
    formatted_time = datetime.now().strftime("%Y年%m月%d日%H時%M分%S秒")
    year = formatted_time[:4]
    month = formatted_time[5:7]
    day = formatted_time[8:10]
    hour = formatted_time[11:13]
    minute = formatted_time[14:16]
    second = formatted_time[17:19]
    
    ss = (f"{year}-{month}-{day}")
    label = (f" {hour}:{minute}:{second}")
    return formatted_time, ss, label

def draw_text(img, text,
          font=cv2.FONT_HERSHEY_PLAIN,
          pos=(0, 0),
          font_scale=3,
          font_thickness=2,
          text_color=(0, 255, 0),
          text_color_bg=(0, 0, 0)
          ):
    
        x, y = pos
        text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
        text_w, text_h = text_size
        cv2.rectangle(img, pos, (x + text_w, y + text_h), text_color_bg, -1)
        cv2.putText(img, text, (x, y + text_h + font_scale - 1), font, font_scale, text_color, font_thickness)

        return text_size
    
def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"文件夾 '{folder_path}' 創建成功")
        return folder_path
    else:
        i = 1
        while True:
            new_folder_path = f"{folder_path}({i})"
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
                print(f"文件夾 '{new_folder_path}' 創建成功")
                return new_folder_path
            i += 1

model = YOLO('yolov8n-pose.pt')

video_path = 1
cap = cv2.VideoCapture(video_path)

ground_points = [(100, 100), (300, 90), (550, 350), (200, 300)]
ground_polygon = Polygon(ground_points)

last_screenshot_time = time.time()
o = 0
frame_count = 0
start_time = time.time()

formatted_time, ss, label = timeFormat()
new_folder = create_folder('C:/Users/AIDL-09/Desktop/fall_detection/fall/screenshots/{}'.format(ss))

fall_start_time = None

while cap.isOpened():
    success, frame = cap.read()

    if success:
        results = model.predict(frame, conf=0.8) 

        frame_count += 1
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time
        fps = str(round(fps, 2))

        f, ss, label = timeFormat()
        draw_text(frame, ss + label, font_scale=2, pos=(10, 20), text_color_bg=(255, 0, 0))

        for i in range(len(ground_points)): # Draw ground polygon
            pt1 = ground_points[i]
            pt2 = ground_points[(i + 1) % len(ground_points)]
            cv2.line(frame, pt1, pt2, (0, 255, 0), 1)
                
        for r in results:
            kps = r.keypoints
            for kp in kps:
                list_p = kp.data.tolist()

        for i in results[0].boxes.xyxy:
            x1 = int(i[0])
            y1 = int(i[1])
            x2 = int(i[2])
            y2 = int(i[3])
            
            annotator = Annotator(frame)
            
            conf = results[0].boxes.conf[0]
            conf = str(conf)
            conf = conf[6:11]

            classes = results[0].names[0]
            
            boxess = [{'bbox': [x1,y1,x2,y2]}]
            for obj in boxess:
                
                bbox = obj['bbox']
                if bbox is None:
                    continue
                
                object_center = Point(bbox[0] + (bbox[2] - bbox[0]) / 2, bbox[1] + (bbox[3] - bbox[1]) / 2)

                if ground_polygon.contains(object_center):
                    print("警報：有物件進入地面範圍內！")
                    
                    if y2 - y1 > x2 - x1 :   # 非跌倒        
                        text = f"{classes} {conf})non-fall".format(classes, conf)
                        print(text)
                        annotator.box_label(i, text, color=(255, 0, 0))
                        fall_start_time = None  # Reset fall start time
                    else: # 跌倒
                        if fall_start_time is None:
                            fall_start_time = time.time()  # Start counting fall duration
                        else:
                            fall_duration = time.time() - fall_start_time
                            text = f"{classes} {conf})fall down for {int(fall_duration)} seconds".format(classes, conf)
                            annotator.box_label(i, text, color=(255, 0, 0))
                            annotated_frame = annotator.result()
                            if fall_duration >= 3: # 跌倒超過3秒就執行
                                text = f"{classes} {conf})fall down for {int(fall_duration)} seconds".format(classes, conf)
                                annotator.box_label(i, text, color=(255, 0, 0))
                                annotated_frame = annotator.result()
                        
                                for i in range(len(ground_points)):
                                    pt1 = ground_points[i]
                                    pt2 = ground_points[(i+1) % len(ground_points)]
                                    cv2.line(frame, pt1, pt2, (0, 0, 255), 1)
                                    cv2.putText(frame, "alert", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                                cv2.rectangle(annotated_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 2)
                                current_time = time.time()
                                if send_notify and current_time - last_screenshot_time >= 10:
                                    cv2.imwrite(f"{new_folder}/{o}.jpg", annotated_frame)
                                    image = f"{new_folder}/{o}.jpg"
                                    o += 1
                                    last_screenshot_time = current_time
                                    t_formatted, ss, label = timeFormat()
                                    print("_____________________________________")
                                    print()
                                    print("截圖:" , o ,"張" )
                                    print("有人跌倒！已發送Line-Notify到群組！")
                                    lineNotify.check_response_Line(t_formatted,image)

        cv2.imshow("cam 2", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
