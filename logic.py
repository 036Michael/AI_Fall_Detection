import math
import cv2
import time 
import test
import pandas as pd
import os 

from excel import simulate_and_write_to_excel
from utils import create_folder , timeFormat


_, ss, _ = timeFormat()
current_path = os.getcwd()  # 獲取當前路徑
target_path = (f"{current_path}\\screenshots\\cam1\\{ss}") 
new_folder = create_folder(target_path)
image_counter = 0  # 定義為全局變量

fall_start_time, fall_end_time, fall_duration = 0, 0, 0

def fall_detection(frame, keypoints, boxes):
    global fall_start_time, fall_end_time, fall_duration
    color_box = (0, 255, 0)
    """偵測跌倒動作，根據腿部角度計算並判斷是否發出警告"""
    global image_counter
    x1, y1, x2, y2 = map(int, boxes)
    left_leg_angle, right_leg_angle = get_leg_angles(keypoints)    

    if left_leg_angle is not None and right_leg_angle is not None:
        print(f'角度！！！{abs(left_leg_angle), abs(right_leg_angle)}') 
        is_fall_risk = abs(left_leg_angle) > 30 or abs(right_leg_angle) > 30

        if is_fall_risk and check_fall_duration(y2, y1, x2, x1) == False :#橘色
            if fall_start_time is 0:
                fall_start_time = time.time() # 開始時間
            color_box = (0, 204, 255) # 橘色
            cv2.rectangle(frame, (x1, y1), (x2, y2), color_box , 2)
            if check_fall_duration(y2, y1, x2, x1): # 紅色
                color_box = (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color_box , 2)
                fall_end_time = time.time() # 結束時間
                fall_duration = fall_end_time - fall_start_time
                return frame

            else :  # 橘色 or 綠色
                if is_fall_risk and check_fall_duration(y2, y1, x2, x1) == False: #橘色
                    color_box = (0, 204, 255) # 橘色
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color_box , 2)
                    return frame
                
                else: # 綠色
                    color_box = (0, 255, 0) # 綠色
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color_box , 2)
                    fall_start_time, fall_end_time, fall_duration = 0, 0, 0
                    return frame
                    
        else: # 紅色 或 綠色
            if check_fall_duration(y2, y1, x2, x1) :# 紅色
                color_box = (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color_box , 2)
                fall_end_time = time.time() # 結束時間
                fall_duration = fall_end_time - fall_start_time
                if fall_start_time != 0 and fall_duration < 0.8:
                    test.play_sound()
                return frame
 
            else : # 綠色
                color_box = (0, 255, 0)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color_box , 2)
                
                fall_start_time, fall_end_time, fall_duration = 0, 0, 0
                return frame

    else: #沒偵測到腳的 keypoint
        fall_start_time, fall_end_time, fall_duration = 0, 0, 0
        cv2.rectangle(frame, (x1, y1), (x2, y2), color_box, 2)
        cv2.putText(frame, 'No keypoints', (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
        return frame

def get_leg_angles(keypoints):
    """計算左、右腿的角度，若點不存在返回 None"""
    left_leg_angle = calculate_angle(keypoints[11], keypoints[13], keypoints[15])  # 左腿
    right_leg_angle = calculate_angle(keypoints[12], keypoints[14], keypoints[16])  # 右腿
    return left_leg_angle, right_leg_angle

def calculate_angle(pointA, pointB, pointC):
    """計算三個點之間的角度，若有一點不存在則返回 None"""
    if any(p[0] == 0 or p[1] == 0 for p in [pointA, pointB, pointC]):
        return None

    AB, BC = [pointB[i] - pointA[i] for i in range(2)], [pointC[i] - pointB[i] for i in range(2)]
    magnitude_AB = math.sqrt(sum(x ** 2 for x in AB))
    magnitude_BC = math.sqrt(sum(x ** 2 for x in BC))
    
    if magnitude_AB == 0 or magnitude_BC == 0:
        return None

    dot_product = sum(AB[i] * BC[i] for i in range(2))
    cos_angle = max(-1, min(1, dot_product / (magnitude_AB * magnitude_BC)))
    angle_deg = math.degrees(math.acos(cos_angle))
    
    print("-----------------------" * 4)
    print(f"角度（弧度）: {math.acos(cos_angle)}")
    print(f"角度（度數）: {angle_deg}")
    print("-----------------------" * 4)
    return angle_deg

def display_warning(frame, left_angle, right_angle, box):
    color_box = (0, 204, 255)
    """顯示跌倒風險警告訊息及框線"""
    x1, y1, x2, y2 = box
    cv2.putText(frame, f"left:{left_angle:.2f}", (10, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
    cv2.putText(frame, f"right:{right_angle:.2f}", (400, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color_box , 2)

def check_fall_duration(y2, y1, x2, x1):
    """檢查跌倒時間是否滿足條件，返回是否跌倒"""
    return y2 - y1 < x2 - x1 

def log_fall_event(frame, duration):
    """記錄跌倒事件，包括存檔與輸出訊息"""
    global image_counter
    test.play_sound()
    simulate_and_write_to_excel({'fall_duration': duration, 'timestamp': pd.Timestamp.now()})
    cv2.imwrite(f"{new_folder}/{image_counter}.jpg", frame)
    image_counter += 1
    print("跌倒時間：", duration)