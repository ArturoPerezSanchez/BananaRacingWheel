import tkinter as tk
import cv2
from PIL import ImageTk, Image
import json
from utils import flipImg, createMask, loadJSON, detect_objects, drawRedRectangle, drawRotationLine

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
        # Create a label for the text
        text_label = tk.Label(self.left_frame, text="Adjust the color bars until you see only\n the desired object on the screen below",
                              font=("Helvetica", 16), pady=10)
        text_label.pack()



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
        
        r, g, b = loadJSON()
        self.slider1.set(r)
        self.slider2.set(g)
        self.slider3.set(b)
        
        # Initialize the values
        self.red = r
        self.green = g
        self.blue = b
        
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
            
            # Try to detect the object
            banana = detect_objects(mask)

            # If detected, draw the container rectangle and the angle
            if(banana is not None):
                self.banana = banana
                frame = drawRedRectangle(frame, banana, color=(255,0,0))
                frame = drawRotationLine(frame, banana, color=(255,0,0))

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



def loadGUI():
    # Create the Tkinter root window
    root = tk.Tk()

    # Create the GUI instance
    gui = GUI(root)

    # Start the Tkinter event loop
    root.mainloop() 




loadGUI()