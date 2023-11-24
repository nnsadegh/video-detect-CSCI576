from collections import Counter
import numpy as np
import librosa
import cv2
from sub_signature import SubSignature

class ComputeSubSignature(SubSignature):
    def __init__(self, video_path, cluster_size=200, frame_sample_rate=30):
        super().__init__(video_path)
        self.cluster_size = cluster_size
        self.frame_sample_rate = frame_sample_rate
        self.signature = None

    def dominant_colors(self, frame):
        data = np.float32(frame).reshape((-1, 3))
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, labels, centers = cv2.kmeans(data, self.cluster_size, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        return centers

    #EXTRACTION
    def extract_features(self):
        cap = cv2.VideoCapture(self.video_path)
        colors = []

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame_count % self.frame_sample_rate != 0:
                break

            dominant_colors = self.dominant_colors(frame)
            colors.extend(dominant_colors)

            frame_count += 1

        cap.release()

        color_counts = Counter(map(tuple, colors))
        most_common_colors = color_counts.most_common(self.cluster_size)
        self.signature = [color for color, _ in most_common_colors]
        
    # def extract_motion_features(self):
    #     # print("Extracting motion features...")
    #     cap = cv2.VideoCapture(self.video_path)
    #     frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    #     motion_values = []

    #     for _ in range(frame_count - 1):
    #         ret, frame1 = cap.read()
    #         ret, frame2 = cap.read()

    #         if not ret:
    #             break

    #         # Compute motion as the absolute difference between frames
    #         diff = cv2.absdiff(frame1, frame2)
    #         motion_value = np.sum(diff)  # You can customize this metric based on your needs

    #         # Debugging print statements
    #         # print("Motion Value:", motion_value)
            
    #         motion_values.append(motion_value)

    #     cap.release()
    #     self.motion_signature = motion_values
    #     # print("Motion features extracted.")
        
    def extract_audio_features(self):
        # print("Extracting audio features...")
        # Attempt to load audio using librosa
        y, sr = librosa.load(self.video_path)
        # print("Audio loaded successfully.")

        # Extract the mean of the chroma_stft features
        chroma_stft = librosa.feature.chroma_stft(y=y, sr=sr)
        chroma_stft_mean = np.mean(chroma_stft, axis=1)

        # Extract the mean of the mfcc features
        mfcc = librosa.feature.mfcc(y=y, sr=sr)
        mfcc_mean = np.mean(mfcc, axis=1)
        
        # Debugging print statements
        # print("Chroma STFT Shape:", chroma_stft.shape)
        # print("MFCC Shape:", mfcc.shape)

        # Combine the features into a single signature
        self.audio_signature = np.concatenate((chroma_stft_mean, mfcc_mean))
        # print("Audio features extracted.")

    #COMPARISON
    def compare(self, other_signature, margin=6):
        if not self.signature:
            raise ValueError("Signature not generated. Call extract_features() first.")

        matching_colors = 0
        total_query_colors = len(self.signature)

        for query_color in self.signature:
            if any(self.is_color_within_margin(query_color, db_color, margin) for db_color in other_signature.signature):
                matching_colors += 1

        if total_query_colors == 0:
            return 100  # Avoid division by zero
        return (matching_colors / total_query_colors) * 100
    
    # def compare_motion(self, other_motion_signature):
    #     if isinstance(self.motion_signature, list):
    #         self.motion_signature = np.array(self.motion_signature)
    #     if isinstance(other_motion_signature, list):
    #         other_motion_signature = np.array(other_motion_signature)

    #     print("Motion Signature Shapes:", self.motion_signature.shape, other_motion_signature.shape)
    #     return np.corrcoef(self.motion_signature, other_motion_signature)[0, 1]

    
    def compare_audio(self, other_audio_signature):
        # Compare audio signatures by computing a similarity metric
        # You can use any appropriate method based on your requirements
        if self.audio_signature is None:
            self.extract_audio_features()  # Adjust this based on how you compute audio features
        if other_audio_signature is None:
            other_audio_signature = self.extract_audio_features()  # Adjust this based on how you compute audio features

        print("Audio Signature Shapes:", self.audio_signature.shape, other_audio_signature.shape)
        return np.corrcoef(self.audio_signature, other_audio_signature)[0, 1]

    @staticmethod
    def is_color_within_margin(query_color, db_color, margin=6):
        return all(abs(query_component - db_component) <= margin for query_component, db_component in zip(query_color, db_color))
