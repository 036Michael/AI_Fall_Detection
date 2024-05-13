import cv2
import torch

x = torch.rand(5, 3)
print(x)


# Open the first camera connected to the computer.
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error opening video stream or file")

# Read and display frames in a loop until the user closes the window or presses ESC
while (cap.isOpened()):
    ret, frame = cap.read()
    if ret:
        print("Frame read correctly")
        print(torch.cuda.is_available())
        print(torch.cuda.get_device_name(0))
        cv2.imshow('Frame', frame)

        # Press ESC on keyboard to exit
        if cv2.waitKey(25) & 0xFF == 27:
            break
    else:
        break

# Release the video capture and close windows
cap.release()
cv2.destroyAllWindows()
