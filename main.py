import cv2
import numpy as np


# Define the range of blue color in HSV
lower_color = np.array([100, 70, 70])
upper_color = np.array([130, 255, 255])

# Create a VideoCapture object to access the webcam
cap = cv2.VideoCapture(0)


def addBlackBox(img, box_height=300):
    height, width, _ = img.shape
    black_box = np.zeros((box_height, width, 3), dtype=np.uint8)
    return np.concatenate((img, black_box), axis=0)

def flipImg(img):
    return cv2.flip(img, 1)

def addTextToImg(img):
    text = 'Press Q or ESC to quit'
    height, width, _ = img.shape
    text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
    text_width = text_size[0]
    text_height = text_size[1]
    text_position_x = 10
    text_position_y = int(height / 2) + (text_height // 2) + 10
    cv2.putText(img, text, (text_position_x, text_position_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    return img

def createMask(frame):

    # Convert the image from BGR to HSV color space
    hsv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask of the blue pixels
    mask = cv2.inRange(hsv_image, lower_color, upper_color)

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

    return mask, result, average_position

def count_objects(mask, kernel_size=(10, 10)):
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
        object_pixels = []
        for point in contour:
            x, y = point[0]
            object_pixels.append((x, y))
        objects.append(object_pixels)

    return len(objects)



while True:
    # Read frame-by-frame from the webcam
    _, frame = cap.read()
 
    # Flip the frame horizontally
    frame = flipImg(frame)

    # Create a mask highlighting the selected color
    mask, result, avg_position = createMask(frame)

    # Create a black image of the same size as the frame
    frame = addBlackBox(frame)

    # Add a text overlay to the frame
    frame = addTextToImg(frame)
    
    # Draw a red circle on the image
    frame = cv2.circle(frame, avg_position, 20, (0, 0, 255), -1)

    # Display the original image, the blue pixels mask, and the resulting image
    cv2.imshow('Blue Pixels Mask', mask)
    cv2.imshow('Result', result)
    cv2.imshow('Webcam', frame)


    # Check for the conditions to exit the loop
    c = cv2.waitKey(1)
    if (c == 27 or c==ord('q')) or (cv2.getWindowProperty('Webcam', cv2.WND_PROP_VISIBLE) < 1):
        break

# Release the VideoCapture object and close the window
cap.release()
cv2.destroyAllWindows()
