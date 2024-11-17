import os
import cv2
from datetime import datetime


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
    cv2.rectangle(img, pos, (x + text_w , y + text_h), text_color_bg, -1)
    cv2.putText(img, text, (x, y + text_h + font_scale - 1),
                font, font_scale, text_color, font_thickness)
    return text_size

def toCSV(data,filename,option):
    """
    Writes data to a CSV file.

    Parameters
    ----------
    data : str
        The data to be written to the CSV file.
    filename : str
        The filename of the CSV file to be written.
    option : str
        The option for writing the file. 'w' for overwrite, 'a' for append.

    Returns
    -------
    None
    """
    with open(filename, option) as file:
        file.write(data)

        
def printSymbol(text , batch = 50):
    print(text* batch)


