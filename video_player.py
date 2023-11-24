import tkinter as tk
from PIL import Image, ImageTk
import cv2
import os

class VideoPlayer:
    def __init__(self, video_path, title):
        self.root = tk.Tk()
        self.root.title(title)

        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.after_id = None

        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height)
        self.canvas.pack()

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

    def play(self):
        ret, frame = self.cap.read()
        if not ret or not self.is_playing:
            return

        current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
        self.photo = self.convert_to_photo(frame)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)

        self.after_id = self.root.after(30, self.play)

    def play_video(self):
        self.is_playing = True
        self.play()

    def pause_video(self):
        self.is_playing = False
        if self.after_id:
            self.root.after_cancel(self.after_id)

    def reset_video(self):
        self.is_playing = True
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.play()

    def convert_to_photo(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        return ImageTk.PhotoImage(image=img)
