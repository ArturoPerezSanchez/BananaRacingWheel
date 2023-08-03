import cv2
import numpy as np
from utils import flipImg, createMask, loadJSON, detect_objects, addDashboard, addTextToImg, drawRedRectangle, drawRotationLine

def AnalyzeMask(frame, mask):

    # Find non-zero pixels in the mask
    non_zero_pixels = cv2.findNonZero(mask)

    # Calculate the average position
    if non_zero_pixels is not None:
        total_x = np.sum(non_zero_pixels[:, 0, 0])
        total_y = np.sum(non_zero_pixels[:, 0, 1])
        count = non_zero_pixels.shape[0]
        avg_x = int(total_x / count)
        avg_y = int(total_y / count)
        average_position = (avg_x, avg_y)
    else:
        average_position = None

    # Convert the mask to a three-channel image
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Apply the mask to the original image
    foreground = cv2.bitwise_and(frame, mask_bgr)

    # Convert the mask to a three-channel grayscale image
    mask_gray = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Convert the original image to grayscale
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Convert the grayscale image to a three-channel image
    gray_bgr = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)

    # Apply the inverse of the mask to the grayscale image
    background = cv2.bitwise_and(gray_bgr, cv2.bitwise_not(mask_gray))

    # Combine the foreground and background to get the final result
    result = cv2.add(foreground, background)

    return result, average_position

# Create a VideoCapture object to access the webcam
cap = cv2.VideoCapture(0)

while True:
    # Read frame-by-frame from the webcam
    _, frame = cap.read()

    # Flip the frame horizontally
    frame = flipImg(frame)

    # Obtain the selected color from the json file
    red, green, blue, speed_treshold = loadJSON()

    # Create a mask highlighting the selected color
    mask = createMask(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), r=red, g=green, b=blue, treshold=55)

    # Analyze the mask to get the object information
    result, avg_position = AnalyzeMask(frame, mask)

    # Add a text overlay to the result
    result = addTextToImg(result, "Press Q or ESC to quit")

    # Detect the tacked object
    banana = detect_objects(mask)

    if(banana is not None):
        result = drawRedRectangle(result, banana)
        result = drawRotationLine(result, banana)
        result = addDashboard(result, rotation=banana.getRotation(), s1=banana.getThrottle(speed_treshold), s2=banana.getBrake(speed_treshold))
    else:
        result = addDashboard(result)

    # Display the original image, the blue pixels mask, and the resulting image
    cv2.imshow('Webcam', frame)
    cv2.imshow('Mask', mask)
    cv2.imshow('Banana Racing Wheel', result)

    # Check for the conditions to exit the loop
    c = cv2.waitKey(1)
    if (c == 27 or c==ord('q')) or (cv2.getWindowProperty('Banana Racing Wheel', cv2.WND_PROP_VISIBLE) < 1):
        break

# Release the VideoCapture object and close the window
cap.release()
cv2.destroyAllWindows()
