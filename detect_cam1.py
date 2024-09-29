import cv2
import os
import time
from datetime import datetime
from ultralytics import YOLO
from ultralytics.utils.plotting import Annotator
import lineNotify
import numpy as np
from shapely.geometry import Polygon, Point
import pygame

send_notify = True
inside_polygon = False  # 用于追踪人物是否在地面范围内
fall_start_time = None  # 跌倒开始时间
notified = False  # 用于追踪是否已经发送了通知
left_polygon_time = None  # 记录人物离开地面范围的时间

# # Read logo and resize
# logo = cv2.imread('./assets/falldown.png')
# size = 100
# logo = cv2.resize(logo, (size, size))

# # Create a mask of logo
# img2gray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
# ret, mask = cv2.threshold(img2gray, 1, 255, cv2.THRESH_BINARY)


# 初始化 pygame mixer
pygame.mixer.init()
# 加載音效文件
sound = pygame.mixer.Sound('assets/sound_effect/falldown_remind.mp3')


def play_sound():
    sound.play()


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
    cv2.putText(img, text, (x, y + text_h + font_scale - 1),
                font, font_scale, text_color, font_thickness)
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


# Load the Yolov8 model
model = YOLO('yolov8n-pose.pt')

video_path = 0
cap = cv2.VideoCapture(video_path)

# 定義地面多邊形
# 左上 右上 右下 左下
ground_points = [(113, 150), (560, 100), (1000, 600), (226, 450)]  # 1280x720
ground_polygon = Polygon(ground_points)

# 600x400
# ground_points = [(113, 150), (400, 150), (400, 500), (226, 450)]

last_screenshot_time = time.time()
o = 0
frame_count = 0
start_time = time.time()

formatted_time, ss, label = timeFormat()

current_path = os.getcwd()
target_path = (f"{current_path}\\screenshots\\cam1\\")

print(f"當前工作目錄是: {target_path}")

if not os.path.exists(target_path):
    os.makedirs(target_path)
    print(f"文件夾 '{target_path}' 創建成功")
else:
    print(f"文件夾已存在")

new_folder = create_folder(f'{target_path}/{ss}')

while cap.isOpened():
    success, frame = cap.read()

    # roi = frame[-size-10:-10, -size-10:-10]

    # # Set an index of where the mask is
    # roi[np.where(mask)] = 0
    # roi += logo

    if success:
        results = model.predict(frame, conf=0.8)
        frame_count += 1
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time
        fps = str(round(fps, 2))

        f, ss, label = timeFormat()
        draw_text(frame, ss + label, font_scale=2,
                  pos=(10, 20), text_color_bg=(255, 0, 0))

        for i in range(len(ground_points)):  # Draw ground polygon
            pt1 = ground_points[i]
            pt2 = ground_points[(i + 1) % len(ground_points)]
            cv2.line(frame, pt1, pt2, (0, 255, 0), 3)

        person_in_polygon = False

        for r in results:
            kps = r.keypoints
            for kp in kps:
                list_p = kp.data.tolist()
        # 提取邊框的坐標點
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

            boxess = [{'bbox': [x1, y1, x2, y2]}]
            for obj in boxess:

                bbox = obj['bbox']
                if bbox is None:
                    continue

                object_center = Point(
                    bbox[0] + (bbox[2] - bbox[0]) / 2, bbox[1] + (bbox[3] - bbox[1]) / 2)

                if ground_polygon.contains(object_center):
                    person_in_polygon = True

                    if y2 - y1 > x2 - x1:  # 非跌倒
                        text = f"{classes} {conf})non-fall".format(
                            classes, conf)
                        annotator.box_label(i, text, color=(255, 0, 0))
                        fall_start_time = None  # Reset fall start time
                    else:  # 跌倒
                        if fall_start_time is None:
                            fall_start_time = time.time()  # Start counting fall duration
                        else:
                            fall_duration = time.time() - fall_start_time
                            text = f"{classes} {conf})fall down for {int(fall_duration)} seconds".format(
                                classes, conf)
                            annotator.box_label(i, text, txt_color=(
                                255, 255, 255), color=(0, 0, 255))
                            annotated_frame = annotator.result()
                            if fall_duration >= 3 and not notified:  # 跌倒超過3秒且尚未通知
                                text = f"{classes} {conf})fall down for {int(fall_duration)} seconds".format(
                                    classes, conf)
                                annotator.box_label(i, text, txt_color=(
                                    255, 255, 255), color=(0, 0, 255))
                                annotated_frame = annotator.result()

                                for i in range(len(ground_points)):
                                    pt1 = ground_points[i]
                                    pt2 = ground_points[(
                                        i+1) % len(ground_points)]
                                    cv2.line(frame, pt1, pt2, (0, 255, 0), 1)
                                    cv2.putText(
                                        frame, "alert", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                                cv2.rectangle(
                                    annotated_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 2)
                                current_time = time.time()
                                if send_notify:
                                    # if send_notify and current_time - last_screenshot_time >= 10:
                                    cv2.imwrite(
                                        f"{new_folder}/{o}.jpg", annotated_frame)
                                    image = f"{new_folder}/{o}.jpg"
                                    o += 1
                                    last_screenshot_time = current_time
                                    t_formatted, ss, label = timeFormat()
                                    print("_____________________________________")
                                    print("截圖:", o, "張")
                                    print("有人跌倒！已發送Line-Notify到群組！")
                                    lineNotify.check_response_Line(
                                        t_formatted, image)
                                    play_sound()
                                    notified = True  # 设置已通知标志

        if not person_in_polygon:
            if left_polygon_time is None:
                # Start counting the time since the person left the polygon
                left_polygon_time = time.time()
            elif time.time() - left_polygon_time >= 3:
                fall_start_time = None
                notified = False  # 重置已通知标志
                left_polygon_time = None  # 重置离开时间
        else:
            left_polygon_time = None  # Reset if the person is still inside the polygon

        cv2.imshow("cam 1", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
