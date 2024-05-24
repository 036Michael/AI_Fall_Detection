import os
current_path = os.getcwd()

target_path = (f"{current_path}\\screenshots")

print(f"當前工作目錄是: {target_path}")

if not os.path.exists(target_path):
    os.makedirs(target_path)
    print(f"文件夾 '{target_path}' 創建成功")

else:
    print(f"文件夾已存在")
