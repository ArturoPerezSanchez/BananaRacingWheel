import logging
import subprocess
import tkinter as tk
from PIL import Image, ImageTk
try:
    import pyvjoy
    vjoy_installed = True
except ImportError:
    vjoy_installed = False

def setup_logging():
    # Create a logging configuration
    logging.basicConfig(
        level=logging.ERROR,
        filename="error.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s: %(message)s",
    )

def open_vjoy_website(root):
    import webbrowser
    webbrowser.open("https://vjoystick.sourceforge.io/")
    root.destroy()

def vjoy_install_request():
    root = tk.Tk()
    root.title("VJoy Installation Check")

    label = tk.Label(root, text='label_text', font=("Helvetica", 14))
    label.pack(padx=20, pady=30)

    label.config(text="VJoy is not installed on your system.\nClick the button to visit the official website.", fg="red")

    exit_button = tk.Button(root, text="EXIT", command=lambda: on_exit_click(root), cursor="hand2", bg="red", fg="white", font=("Helvetica", 12, "bold"))
    exit_button.place(relx=0.25, rely=0.8, anchor=tk.CENTER)

    vjoy_website_button = tk.Button(root, text="Download VJoy", command=lambda: open_vjoy_website(root), cursor="hand2", bg="blue", fg="white", font=("Helvetica", 12, "bold"))
    vjoy_website_button.place(relx=0.7, rely=0.8, anchor=tk.CENTER)

    root.geometry("400x200")
    root.mainloop()

def on_exit_click(root):
    root.destroy()

def on_config_click(root):
    try:
        subprocess.run(["python", "config.py"], check=True)
    except subprocess.CalledProcessError as e:
        # Log the error 
        logging.error(f"Error: {e}")


def on_play_click(root):
    try:
        subprocess.run(["python", "game.py"], check=True)
    except subprocess.CalledProcessError as e:
        # Log the error
        logging.error(f"Error: {e}")
    root.destroy()

def main_interface():
    root = tk.Tk()
    root.title("Banana Racing Wheel")

    # Load and resize the background image
    background_image = Image.open("images/background.png")
    width, height = 750, 500
    background_image = background_image.resize((width, height))
    background_image = ImageTk.PhotoImage(background_image)

    # Create a canvas to place the background image
    canvas = tk.Canvas(root, width=width, height=height)
    canvas.pack()
    canvas.create_image(0, 0, image=background_image, anchor=tk.NW)
    
    # Create buttons
    exit_button = tk.Button(root, text="EXIT", command=lambda: on_exit_click(root), width="8", cursor="hand2", bg="red", fg="white", font=("Helvetica", 18, "bold"))
    exit_button.place(relx=0.2, rely=0.8, anchor=tk.CENTER)

    config_button = tk.Button(root, text="CONFIG", command=lambda: on_config_click(root), width="8", cursor="hand2", bg="green", fg="white", font=("Helvetica", 18, "bold"))
    config_button.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

    play_button = tk.Button(root, text="PLAY", command=lambda: on_play_click(root), width="8", cursor="hand2", bg="#4a1", fg="white", font=("Helvetica", 18, "bold"))
    play_button.place(relx=0.8, rely=0.8, anchor=tk.CENTER)

    root.mainloop()

if __name__ == "__main__":
    setup_logging()
    if not vjoy_installed:
        logging.error(f"Error: VJoy not installed")
        vjoy_install_request()
    else:
        main_interface()
