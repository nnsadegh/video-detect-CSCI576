from collections import Counter
import numpy as np
import cv2
from sub_signature import SubSignature

class ColorSubSignature(SubSignature):
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

    @staticmethod
    def is_color_within_margin(query_color, db_color, margin=6):
        return all(abs(query_component - db_component) <= margin for query_component, db_component in zip(query_color, db_color))
