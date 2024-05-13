@echo off
call "C:\Users\MC\miniconda3\Scripts\activate.bat" d:\coding-project\AI_Fall_Detection\.conda
start python D:\coding-project\AI_Fall_Detection\detect_cam1.py
start python D:\coding-project\AI_Fall_Detection\detect_cam2.py
pause


