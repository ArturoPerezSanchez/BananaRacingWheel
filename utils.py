
import cv2
import numpy as np
import json
from banana_class import banana

def createMask(hsv_image, r=50, g=50, b=205, treshold=50):
    # Define the range of blue color in HSV
    lower_r = min(255, max(0,r-treshold))
    upper_r = min(255, max(0,r+treshold))

    lower_g = min(255, max(0,g-treshold))
    upper_g = min(255, max(0,g+treshold))

    lower_b = min(255, max(0,b-treshold))
    upper_b = min(255, max(0,b+treshold))

    lower_color = np.array([lower_r, lower_g, lower_b])
    upper_color = np.array([upper_r, upper_g, upper_b])

    # Create a mask of the blue pixels
    mask = cv2.inRange(hsv_image, lower_color, upper_color)

    return mask

def flipImg(img):
    return cv2.flip(img, 1)


def loadJSON(filename="config.json"):
	r, g, b = 0, 0, 0
	
	try:
		with open(filename, "r") as file:
			config = json.load(file)
			r = config.get("red", 0)
			g = config.get("green", 200)
			b = config.get("blue", 200)
	except (FileNotFoundError, json.JSONDecodeError):
		# Use default values if config file doesn't exist or has invalid format
		r = 0
		g = 200
		b = 200
	return r, g, b

def addBlackBox(img, box_height=300):
    height, width, _ = img.shape
    black_box = np.zeros((box_height, width, 3), dtype=np.uint8)
    return np.concatenate((img, black_box), axis=0)

def addTextToImg(img, text):
    height, width, _ = img.shape
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    text_width = text_size[0]
    text_height = text_size[1]
    text_position_x = 10
    text_position_y = int(height / 2) + (text_height // 2) + 10
    cv2.putText(img, text, (text_position_x, text_position_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return img

def detect_objects(mask, kernel_size=(10, 10)):
	# Convert the mask to binary (if it's not already binary)
	mask_binary = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)[1]

	# Apply morphological opening to remove small noise
	kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, kernel_size)
	mask_opened = cv2.morphologyEx(mask_binary, cv2.MORPH_OPEN, kernel)

	# Apply morphological closing to merge nearby regions
	mask_closed = cv2.morphologyEx(mask_opened, cv2.MORPH_CLOSE, kernel)

	# Find contours in the closed mask
	contours, _ = cv2.findContours(mask_closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# Extract pixel coordinates for each contour (object)
	objects = []
	for contour in contours:
		x_min, y_min = contour[0][0]
		x_max, y_max = contour[0][0]
		left = []
		right = []
		for point in contour:
			x, y = point[0]
			if x_min is None or x <= x_min:
				if(x < x_min):
					x_min = x
					left = []
				left.append(y)
			elif x_max is None or x >= x_max:
				if(x > x_min):
					x_max = x
					right = []
				right.append(y)


			if y_min is None or y < y_min: y_min = y
			elif y_max is None or y > y_max: y_max = y

		avg_l = np.average(left)
		avg_r = np.average(right)
		detected_banana = banana(x_min, y_min, x_max, y_max, avg_l, avg_r)
		objects.append(detected_banana)

	return len(objects)