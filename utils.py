
import cv2
import numpy as np
import json
from banana_class import banana

def createMask(hsv_image, r=50, g=50, b=205, treshold=100):
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
	r, g, b, s = 0, 0, 0, 0
	
	try:
		with open(filename, "r") as file:
			config = json.load(file)
			r = config.get("red", 0)
			g = config.get("green", 200)
			b = config.get("blue", 200)
			s = config.get("speed_treshold", 250)
	except (FileNotFoundError, json.JSONDecodeError):
		# Use default values if config file doesn't exist or has invalid format
		r = 0
		g = 200
		b = 200
		s = 100
	return r, g, b, s

def addTextToImg(img, text):
    height, width, _ = img.shape
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    text_width = text_size[0]
    text_height = text_size[1]
    text_position_x = 10
    text_position_y = 25
    cv2.putText(img, text, (text_position_x, text_position_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return img

def drawRedRectangle(image, banana, color=(0, 0, 255), thickness=2):
	point1, point2 = banana.getRectangle()
	cv2.rectangle(image, point1, point2, color, thickness)
	return image

def drawRotationLine(image, banana, color=(0, 0, 255), thickness=2):
	point1, point2 = banana.getLinePoints()
    # Draw circles at each point
	cv2.circle(image, point1, 10, color, -1)  # Green circle at point1
	cv2.circle(image, point2, 10, color, -1)  # Green circle at point2

	# Draw a line connecting the two points
	cv2.line(image, point1, point2, color, 2)

	return image

def detect_objects(mask, kernel_size=(5, 5)):
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
		avg_l = np.average(left) if (len(left) > 0) else 1
		avg_r = np.average(right) if (len(right) > 0) else 1
		detected_banana = banana(x_min, y_min, x_max, y_max, avg_l, avg_r)
		objects.append(detected_banana)
	
	objects.sort()
	if(not objects): return None
	detected_banana = objects[-1]
	# print('size: ', detected_banana.getSize())
	# print('Square: ', detected_banana.getSquare())
	# print('Rotation: ', detected_banana.getRotation())
	# print('Center: ', detected_banana.getCenter())
	# print('LinePoints: ', detected_banana.getLinePoints())
	return detected_banana

def addWheelImage(background, wheel_image, rotation=0):
    # Ensure that both images have an alpha channel
    if background.shape[2] == 3:
        background = np.dstack((background, np.ones((background.shape[0], background.shape[1], 1), dtype=np.uint8) * 255))
    if wheel_image.shape[2] == 3:
        wheel_image = np.dstack((wheel_image, np.ones((wheel_image.shape[0], wheel_image.shape[1], 1), dtype=np.uint8) * 255))

    # convert rotation to degrees
    rotation *= 90

    wheel_image_width = min(250, background.shape[1] // 2)

    # Resize the wheel_image
    wheel_image = cv2.resize(wheel_image, (wheel_image_width, wheel_image_width))

    # Rotate the wheel_image according to the given angle
    center = (int(wheel_image.shape[1] / 2), int(wheel_image.shape[0] / 2))  # Rotation center at the bottom-left corner

    rotation_matrix = cv2.getRotationMatrix2D(center, rotation, 1.0)
    rotated_wheel_image = cv2.warpAffine(wheel_image, rotation_matrix, (wheel_image.shape[1], wheel_image.shape[0]))

    # Add the text width the rotation angle
    font_scale = 0.7
    font_thickness = 1
    text_color = (255, 255, 255)
    text = f"Degrees: {rotation:0.2f}"
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)

    # Overlay the rotated image leaving a margin at the bottom and left sides
    margin_bottom = ((background.shape[0] - (wheel_image_width + text_size[1])) // 2) 
    margin_left = max(0, (background.shape[1] // 2 - wheel_image_width) // 2)

    background_alpha = 1.0 - rotated_wheel_image[:, :, 3] / 255.0
    overlay_alpha = rotated_wheel_image[:, :, 3] / 255.0
    for c in range(3):
        background[background.shape[0] - rotated_wheel_image.shape[0] - margin_bottom:background.shape[0] - margin_bottom,
                   margin_left:margin_left + rotated_wheel_image.shape[1], c] = \
            overlay_alpha * rotated_wheel_image[:, :, c] + background_alpha * background[
                background.shape[0] - rotated_wheel_image.shape[0] - margin_bottom:background.shape[0] - margin_bottom,
                margin_left:margin_left + rotated_wheel_image.shape[1], c]
    
    text_x = max(0, (background.shape[1] // 2 - text_size[0]) // 2)
    text_y = margin_bottom + text_size[1]
    cv2.putText(background, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness)
    
    # Discard the alpha channel since we dont need to use it any more
    background = cv2.cvtColor(background, cv2.COLOR_RGBA2BGR)
    return background

def drawProgressBar(image, s1=0, s2=0):
    # Verify that s1 and s2 are between 0 and 100
    s1 = max(0, min(100, s1))
    s2 = max(0, min(100, s2))

    # Rectangle position and size
    rect_width = 200
    rect_height = 20
    center_y = image.shape[0]//2
    center_x = image.shape[1]//2
    gap = 50
    border_width = 2
    rect1_x, rect1_y = center_x + (center_x - rect_width)//2, center_y - (gap//2 + rect_height + 2*border_width)
    rect2_x, rect2_y = rect1_x, center_y + gap//2 + 2*border_width

    rect1_width_filled = int(rect_width * s1 / 100)
    rect2_width_filled = int(rect_width * s2 / 100)

    # Fill the rectangles
    cv2.rectangle(image, (rect1_x, rect1_y), (rect1_x + rect1_width_filled, rect1_y + rect_height), (0, 200, 0), -1)
    cv2.rectangle(image, (rect2_x, rect2_y), (rect2_x + rect2_width_filled, rect2_y + rect_height), (200, 0, 0), -1)

    # Create the empty rectangles
    cv2.rectangle(image, (rect1_x, rect1_y), (rect1_x + rect_width, rect1_y + rect_height), (255, 255, 255), border_width)
    cv2.rectangle(image, (rect2_x, rect2_y), (rect2_x + rect_width, rect2_y + rect_height), (255, 255, 255), border_width)  

    # Font definition
    font_scale = 0.7
    font_thickness = 1
    text_color = (255, 255, 255)

    # Add the label of each bar
    cv2.putText(image, "Throttle", (rect1_x, rect1_y - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness)
    cv2.putText(image, "Brake", (rect2_x, rect2_y - 10), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, font_thickness)

    return image

def addDashboard(original_img, wheel_path="images/wheel.png", box_height=300, rotation=0, s1=0, s2=0):
    # Load wheel image
    wheel_image = cv2.imread(wheel_path, cv2.IMREAD_UNCHANGED)
    height, width, _ = original_img.shape

    blackbox = np.full((box_height, width, 3), (50, 50, 50), dtype=np.uint8)
    blackbox_with_wheel = addWheelImage(blackbox, wheel_image, rotation)
    dashboard = drawProgressBar(blackbox_with_wheel, s1, s2)
    result = np.concatenate((original_img, dashboard), axis=0)

    return result

def overlay_images(image1, image2):

	# Get the dimensions of the images
	height1, width1, channels = image1.shape
	height2, width2 = image2.shape
	image2 = cv2.merge((image2, image2, image2))

	# Calculate the position to overlay the second image
	x_offset = width1 - width2
	y_offset = 0

    # Overlay the second image on the bottom-right corner of the first image
	image1[y_offset:height2, x_offset:width1] = image2

	return image1