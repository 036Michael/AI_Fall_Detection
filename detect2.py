import cv2
import os
import time
from datetime import datetime
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator  # ultralytics.yolo.utils.plotting is deprecated
import lineNotify
from shapely.geometry import Polygon, Point

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
    return formatted_time,ss,label

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
    
# 創建文件夾
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
                # print(new_folder_path)
                return new_folder_path
            i += 1



# Load the YOLOv8 model
model = YOLO('yolov8n-pose.pt')

# Open the video file
# video_path =  "./assets/fall3.mp4"
video_path = 0
cap = cv2.VideoCapture(video_path)

# 定義地面多邊形

# 左上 右上 左下 右下
ground_points = [(100, 200), (500, 200), (500, 400), (100, 400)]
ground_polygon = Polygon(ground_points)
print("ground_polygon",ground_polygon)

last_screenshot_time = time.time() # 上次截圖時間
o = 0 # 截圖編號
frame_count = 0  # 計算幀數
start_time = time.time() # 開始時間


# 創建一個新的文件夾
formatted_time,ss,label= timeFormat()
new_folder = create_folder('C:/Users/AIDL-09/Desktop/fall_detection/fall/screenshots/{}'.format(ss))  # 創建一個新的文件夾


# Loop through the video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLOv8 tracking on the frame, persisting tracks between frames / 在幀上運行 YOLOv8 跟踪，在幀之間保留跟踪
        results = model.predict(frame,conf =0.8) 

        # FPS
        frame_count += 1
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time
        fps  = str(round(fps, 2))
        print(f"FPS: {fps}")
        f,ss,label= timeFormat()
        
        draw_text(frame, ss+label, font_scale=2, pos=(10, 20 ), text_color_bg=(255, 0, 0))

        # cv2.putText(frame, ss+label, (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        for r in results:
            kps = r.keypoints
            for kp in kps:
                list_p = kp.data.tolist()
                
        #         # print("###################")
        #         # print("im list_p",list_p[0])
        #         # print("###################")
                
        #         # if list_p != []:
        #         #     for p in list_p[:4]:
        #         #         cv2.circle(frame, ( int(p[0]), int(p[1])), 8, (0,255,0),-1)


        # """
        # for keypoint in results[0].keypoints.data:
        #     print("###################")
        #     left_eye = keypoint[1]
        #     right_eye = keypoint[2]
        #     print("left_eye",(left_eye[0],left_eye[1]))

        #     print("right_eye",(right_eye[0],right_eye[1]))
            
        #     print("keypoint 17:",keypoint)       
        #     cv2.circle(frame,( int(left_eye[0]), int(left_eye[1])) , 8, (0,255,0),-1)
        #     cv2.circle(frame,( int(right_eye[0]), int(right_eye[1])) , 8, (0,255,0),-1)
        #     print("###################")
        # """
        for i in range(len(ground_points)):
            pt1 = ground_points[i]
            pt2 = ground_points[(i+1) % len(ground_points)]
            cv2.line(frame, pt1, pt2, (0, 255, 0), 3)
                
        # fall detection / 跌倒偵測
        for i in results[0].boxes.xyxy:
            x1 = int(i[0])
            y1 = int(i[1])
            x2 = int(i[2])
            y2 = int(i[3])
            # print("###################")
            
            # print("boxes's i",i)
            # print("###################")
            
            annotator = Annotator(frame)
            
            
            conf = results[0].boxes.conf[0]
            conf = str(conf)
            conf = conf[6:11]
            
            classes = results[0].names[0]
            # print("resultssss:",classes)
            
            boxess = [{'bbox': [x1,y1,x2,y2]}]
            for obj in boxess:
                
                bbox = obj['bbox']
                if bbox is None:
                    continue
                
                object_center = Point(bbox[0] + (bbox[2] - bbox[0]) / 2, bbox[1] + (bbox[3] - bbox[1]) / 2)

                if ground_polygon.contains(object_center):
                    print("警報：有物件進入地面範圍內！")
                    
                    if y2 - y1 > x2 - x1 :                
                        text = f"{classes} {conf})standing".format(classes, conf)
                        print(text)
                        annotator.box_label(i, text, color=(255, 0, 0))                
                        # print("standing")
                    else:
                        text = f"{classes} {conf})fall down".format(classes, conf)
                        annotator.box_label(i, text, color=(255, 0, 0))
                        annotated_frame = annotator.result()
                        
                        cv2.rectangle(annotated_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 2)
                        
                        current_time = time.time()
                        if current_time - last_screenshot_time >= 10  :  # 每n秒截圖一次
                            cv2.imwrite(f"{new_folder}/{o}.jpg", annotated_frame)
                            image = f"{new_folder}/{o}.jpg"
                            o += 1
                            last_screenshot_time = current_time
                            t_formatted,ss,label = timeFormat()
                            print("_____________________________________")
                            print()
                            print("有人跌倒！已發送Line-Notify到群組！")
                            lineNotify.check_response_Line(t_formatted,image)
                            # print(f"{new_folder}/{o}.jpg")
                            # print("fall down")  


   
        # Display the annotated frame
        cv2.imshow("YOLOv8 Tracking", frame)
        


        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Break the loop if the end of the video is reached
        break
# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
