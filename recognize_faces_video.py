# python recognize_faces_video.py --encodings encodings2.pickle --output output/ --display 1 --detection-method hog
# import the necessary packages
from imutils.video import VideoStream
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import lineNotify
import time
from datetime import datetime
import exceldata
import insertime

def timeFormat():
    formatted_time = datetime.now().strftime("%Y年%m月%d日%H時%M分%S秒")
    year = formatted_time[:4]
    month = formatted_time[5:7]
    day = formatted_time[8:10]
    hour = formatted_time[11:13]
    minute = formatted_time[14:16]
    second = formatted_time[17:19]
    return formatted_time	
 # print(f"{o},{year}年{month}月{day}日,{hour}時{minute}分{second}秒")
	# lineNotify.check_response_Line(class_name,formatted_time)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-e", "--encodings", required=True,
	help="path to serialized db of facial encodings")
ap.add_argument("-o", "--output", type=str,
	help="path to output video")
ap.add_argument("-y", "--display", type=int, default=1,
	help="whether or not to display output frame to screen") #是否輸出到screen上面  1是 0否
ap.add_argument("-d", "--detection-method", type=str, default="cnn",
	help="face detection model to use: either `hog` or `cnn`")
args = vars(ap.parse_args())

# load the known faces and embeddings
print("[INFO] loading encodings...")
data = pickle.loads(open(args["encodings"], "rb").read())
# initialize the video stream and pointer to output video file, then
# allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
writer = None
time.sleep(2.0)

# Initialize accuracy variables
total_frames = 0
correct_recognitions = 0
success_stats = 0
namelist = []
for name in data['names']:
        if name not in namelist:
            namelist.append(name)
print("name lists:", namelist)


last_screenshot_time = time.time()
o = 0

# loop over frames from the video file stream
while True:
	# grab the frame from the threaded video stream
	frame = vs.read()
	
	# convert the input frame from BGR to RGB then resize it to have
	# a width of 750px (to speedup processing)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
	# rgb = imutils.resize(frame, width=750)
	r = frame.shape[1] / float(rgb.shape[1])
	# detect the (x, y)-coordinates of the bounding boxes
	# corresponding to each face in the input frame, then compute
	# the facial embeddings for each face
	boxes = face_recognition.face_locations(rgb,
		model=args["detection_method"])
	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []
 
    # loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"],
			encoding,tolerance=0.4)
		name = "Unknown"
		# check to see if we have found a match
		if True in matches:
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}
			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1
			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
			name = max(counts, key=counts.get)
		
		# update the list of names
		names.append(name)
    # loop over the recognized faces
	for ((top, right, bottom, left), name) in zip(boxes, names):
		# rescale the face coordinates
		top = int(top * r)
		right = int(right * r)
		bottom = int(bottom * r)
		left = int(left * r)
		# draw the predicted face name on the image
		cv2.rectangle(frame, (left, top), (right, bottom),
			(0, 255, 0), 2)
		
		y = top - 15 if top - 15 > 15 else top + 15
		# cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
		# 	0.75, (0, 255, 0), 2)
		# if success_stats == 0:
		if name != 'Unknown':
			face_distances = face_recognition.face_distance(data["encodings"], encoding)
			min_distance = min(face_distances)
			similarity_percentage = (1-min_distance) * 100 * 1.15
			if similarity_percentage < 75:
				name = "Unknown"
				# text = f"{name}({similarity_percentage:.2f}%)"
				# print(text)
			cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
			y = top - 15 if top - 15 > 15 else top + 15
			text = f"{name} ({similarity_percentage:.2f}%)" if name != "Unknown" else "Unknown"
			print(f"辨識率: ({similarity_percentage:.2f}%)")
			cv2.putText(frame, text, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
			
		# else:
		# 	text = 'Unknown'
		# cv2.putText(frame,text,(left,y),cv2.FONT_HERSHEY_SIMPLEX,0.75,(0,255,0),2)
            
  
		if (name == 'Unknown'): #陌生人
			cv2.putText(frame, "Unknown", (left, y), cv2.FONT_HERSHEY_SIMPLEX,
						0.75, (0, 255, 0), 2)
			cv2.imwrite("screenshot.jpg",frame)
			current_time = time.time()
			if current_time - last_screenshot_time >=5:
				t_formatted = timeFormat()
				o += 1
				last_screenshot_time = current_time
				insertime.insertTime(t_formatted,"screenshot.jpg")
				print("_____________________________________")
				print()
				print("有陌生人闖進！已發送Line-Notify到群組！")

				lineNotify.check_response_Line(name,t_formatted)

		else: #自己人
			cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
					0.75, (0, 255, 0), 2)
			print("_____________________________________")
			print()
			print("歡迎回家~~~",name)
			total_frames += 1
			if name in namelist:
				correct_recognitions+=1
			# print(result.replace(",","",6))
			# print(result[3:])

			result = exceldata.get_data_by_name(name, "info.xlsx")
			print(result)


  	# if the video writer is None *AND* we are supposed to write
	# the output video to disk initialize the writer
	if writer is None and args["output"] is not None:
		fourcc = cv2.VideoWriter_fourcc(*"MJPG")
		writer = cv2.VideoWriter(args["output"], fourcc, 20,
			(frame.shape[1], frame.shape[0]), True)
	# if the writer is not None, write the frame with recognized
	# faces to disk
	if writer is not None:
		writer.write(frame)
    # check to see if we are supposed to display the output frame to
	# the screen
	if args["display"] > 0:
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
		# if the `q` key was pressed, break from the loop
		if key == ord("q"):
			break

# if total_frames > 0:   #正確率
#     accuracy = (correct_recognitions / total_frames) * 100
#     print(f"Accuracy: {accuracy:.2f}%")

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
# check to see if the video writer point needs to be released
if writer is not None:
	writer.release()