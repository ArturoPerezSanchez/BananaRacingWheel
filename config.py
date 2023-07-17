import tkinter as tk
import cv2
from PIL import ImageTk, Image
import json
import numpy as np

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

class GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GUI with Sliders and Webcam Frames")
        
        # Create left frame
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Create right frame
        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Create sliders in the left frame
        self.slider1 = tk.Scale(self.left_frame, from_=0, to=255, orient=tk.HORIZONTAL, label="Red", tickinterval=50,
                                length=300, showvalue=1, command=self.update_values)
        self.slider1.pack(pady=5)
        
        self.slider2 = tk.Scale(self.left_frame, from_=0, to=255, orient=tk.HORIZONTAL, label="Green", tickinterval=50,
                                length=300, showvalue=1, command=self.update_values)
        self.slider2.pack(pady=5)
        
        self.slider3 = tk.Scale(self.left_frame, from_=0, to=255, orient=tk.HORIZONTAL, label="Blue", tickinterval=50,
                                length=300, showvalue=1, command=self.update_values)
        self.slider3.pack(pady=5)

        self.color_box = tk.Canvas(self.left_frame, width=150, height=50)
        self.color_box.pack(side=tk.LEFT, padx=10, pady=25)

        # Create Accept button
        self.accept_button = tk.Button(self.left_frame, text="Accept", command=self.accept_values,  width=15, height=3)
        self.accept_button.pack(pady=25)
        
        # Load initial slider values from config file or use default values
        try:
            with open("config.json", "r") as file:
                config = json.load(file)
                self.slider1.set(config.get("red", 0))
                self.slider2.set(config.get("green", 0))
                self.slider3.set(config.get("blue", 0))
        except (FileNotFoundError, json.JSONDecodeError):
            # Use default values if config file doesn't exist or has invalid format
            self.slider1.set(0)
            self.slider2.set(0)
            self.slider3.set(0)
        
        # Initialize the slider values
        self.red = self.slider1.get()
        self.green = self.slider2.get()
        self.blue = self.slider3.get()
        
        # Load and display webcam frames in the right frame
        self.frame1_label = tk.Label(self.right_frame)
        self.frame1_label.pack(side=tk.TOP)
        
        self.frame2_label = tk.Label(self.right_frame)
        self.frame2_label.pack(side=tk.BOTTOM)
        
        # Initialize the webcam capture
        self.cap = cv2.VideoCapture(0)
        
        # Start updating the frames
        self.update_frames() 
    
    def update_values(self, _):
        # Get the current slider values
        self.red = self.slider1.get()
        self.green = self.slider2.get()
        self.blue = self.slider3.get()
        
        # Update the color box
        self.color_box.configure(bg=f"#{self.red:02x}{self.green:02x}{self.blue:02x}")
    
    def accept_values(self):
        # Save the slider values to the config file
        config = {
            "red": self.red,
            "green": self.green,
            "blue": self.blue
        }
        with open("config.json", "w") as file:
            json.dump(config, file)
        
        self.root.destroy()  # Close the Tkinter window
    
    def update_frames(self):
        # Read a frame from the webcam
        ret, frame = self.cap.read()
        
        if ret:
            # Convert the frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Flip the frame horizontally
            frame = flipImg(frame)

            # Create a mask highlighting the selected color
            mask = createMask(frame, r=self.red, g=self.green, b=self.blue, treshold=50)
            
            # Resize the frame to fit the GUI
            frame_resized = cv2.resize(frame, (320, 240))

            # Resize the mask to fit the GUI
            mask_resized = cv2.resize(mask, (320, 240))
            
            # Convert the frame to ImageTk format
            img = Image.fromarray(frame_resized)
            img_tk = ImageTk.PhotoImage(image=img)

            # Convert the mask to ImageTk format
            mask_img = Image.fromarray(mask_resized)
            mask_img_tk = ImageTk.PhotoImage(image=mask_img)
            
            # Update the labels with the new frames
            self.frame1_label.configure(image=img_tk)
            self.frame1_label.image = img_tk
            
            self.frame2_label.configure(image=mask_img_tk)
            self.frame2_label.image = mask_img_tk
        
        # Schedule the next frame update
        self.root.after(10, self.update_frames)

# Create the Tkinter root window
root = tk.Tk()

# Create the GUI instance
gui = GUI(root)

# Start the Tkinter event loop
root.mainloop()

# Access the slider values after the window is closed
red_value = gui.red
green_value = gui.green
blue_value = gui.blue

print("Red value:", red_value)
print("Green value:", green_value)
print("Blue value:", blue_value)
