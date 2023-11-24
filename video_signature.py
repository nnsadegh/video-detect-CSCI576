from collections import Counter
import numpy as np
import cv2
import librosa
from sub_signature import SubSignature
from compute_sub_signature import ComputeSubSignature 

class VideoSignature:
    def __init__(self, video_path, cluster_size=200, frame_sample_rate=30):
        self.video_path = video_path
        self.video_name = video_path.split('/')[-1]  # Extract the video name
        self.cluster_size = cluster_size
        self.frame_sample_rate = frame_sample_rate
        self.color_signature = ComputeSubSignature(video_path, cluster_size, frame_sample_rate)
        # self.motion_signature = None  # Placeholder for motion signature
        self.audio_signature = None  # Placeholder for audio signature 

    def generate_signature(self):
        self.color_signature.extract_features()
        # self.color_signature.extract_motion_features()
        self.color_signature.extract_audio_features()
        # Assign extracted features to motion and audio signatures
        # self.motion_signature = np.array(self.color_signature.motion_signature)
        self.audio_signature = np.array(self.color_signature.audio_signature)
        # Add additional calls for motion and audio feature extraction here
        return self  # Add this line to return the instance
    
    # def compare_motion(self, other_motion_signature):
    #     return self.color_signature.compare_motion(other_motion_signature)
    
    def compare_audio(self, other_audio_signature):
        return self.color_signature.compare_audio(other_audio_signature)

    def compare(self, other_video_signature):
        # Compare color signatures
        print("-------")
        color_similarity = self.color_signature.compare(other_video_signature.color_signature)
        print("color:", color_similarity)
        # Compare motion signatures
        # motion_similarity = self.compare_motion(other_video_signature.motion_signature)
        # print("motion:", motion_similarity)
        # Compare audio signatures
        audio_similarity = self.compare_audio(other_video_signature.audio_signature)
        print("audio:", audio_similarity)
        # Combine and return an overall similarity measure
        # print((color_similarity + motion_similarity + audio_similarity) / 3)
        # return (color_similarity + motion_similarity + audio_similarity) / 3
        print((color_similarity + audio_similarity) / 2)
        return (color_similarity + audio_similarity) / 2
    

# Additional imports and changes for shot boundary detection

def detect_shot_boundaries(video_path):
    cap = cv2.VideoCapture(video_path)
    shots = []

    while cap.isOpened():
        ret, frame1 = cap.read()
        ret, frame2 = cap.read()

        if not ret:
            break

        # Compute some metric to detect shot transition (e.g., frame difference)
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if len(contours) > 0:
            shots.append(cap.get(cv2.CAP_PROP_POS_FRAMES))

    cap.release()
    return shots