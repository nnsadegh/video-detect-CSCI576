import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import os

class VideoPlayer:
    def __init__(self, video_path, title, start_frame):
        self.root = tk.Tk()
        self.root.title(title)

        self.video_path = video_path
        if not os.path.exists(video_path):
            print(f"Error: Video file '{video_path}' not found.")
            self.root.destroy()
            return

        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print(f"Error: Failed to open video file '{video_path}'.")
            self.root.destroy()
            return

        self.after_id = None
        self.delay = 1  # set the delay to 1 millisecond

        self.start_frame = start_frame
        self.current_frame = start_frame

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()

        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.progress_bar = ttk.Scale(
            self.root, from_=0, to=self.total_frames, orient="horizontal", length=self.width,
            command=self.update_progress
        )
        self.progress_bar.pack()

        self.progress_bar.set(start_frame)

        self.btn_play = tk.Button(self.root, text="Play", command=self.play_video)
        self.btn_pause = tk.Button(self.root, text="Pause", command=self.pause_video)
        self.btn_reset = tk.Button(self.root, text="Reset", command=self.reset_video)

        self.btn_play.pack(side=tk.LEFT)
        self.btn_pause.pack(side=tk.LEFT)
        self.btn_reset.pack(side=tk.LEFT)

        self.is_playing = False
        self.after_id = None

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def on_close(self):
        self.is_playing = False
        self.cap.release()
        self.root.destroy()

    def update_progress(self, value):
        try:
            frame_number = int(float(value))
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        except ValueError:
            pass

    def play_video_loop(self):
        ret, frame = self.cap.read()
        if not ret or not self.is_playing:
            return

        self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.photo = self.convert_to_photo(frame)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.progress_bar.set(self.current_frame)  # Update progress bar dynamically

        self.after_id = self.root.after(30, self.play_video_loop)  # You can adjust this delay based on the frame rate of the video

    def play_video(self):
        self.is_playing = True
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.progress_bar.config(to=self.total_frames)
        self.play_video_loop()

    def pause_video(self):
        self.is_playing = False
        if self.after_id:
            self.root.after_cancel(self.after_id)

    def reset_video(self):
        self.is_playing = False  # Set is_playing to False when resetting
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.progress_bar.set(0)
        self.current_frame = 0
        self.play_video_loop()  # Start playing video from the beginning

    def convert_to_photo(self, frame):
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            return ImageTk.PhotoImage(image=img)
        except Exception as e:
            print(f"Error converting frame: {e}")
            return None