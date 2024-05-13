import line_notify
import requests


def check_response_Line(last_screenshot_time, image):
    url = "https://notify-api.line.me/api/notify"

    token = ""

    # token = "OLYczNdlOmAzBQ8ztc07mIan87MHfkJfPHuBvW4XQXk" #備用token 宗燁和家南的
    headers = {
        "Authorization": f"Bearer {token}"
    }
    message = "有人跌倒！"  # 提醒已啟動
    payload = {
        "message": message + str(last_screenshot_time)
    }

    # image = open('examples/HSB.jpg', 'rb')    # 以二進位方式開啟圖片
    image = open(image, 'rb')    # 以二進位方式開啟圖片

    imageFile = {'imageFile': image}   # 設定圖片資訊

    # 做 API 呼叫
    response = requests.post(url, headers=headers,
                             data=payload, files=imageFile)

    # 檢查 HTTP 狀態碼
    if response.status_code == 200:
        print("API 呼叫成功！")
    else:
        print("API 呼叫失敗，狀態碼：", response.status_code)

    # 打印API回應
    print(response.text)

    print("_____________________________________")
