import cv2
from sub_signature import SubSignature


class ColorSubSignature(SubSignature):
    def __init__(self, parent_video_signature, video_path, frame_sample_rate=30):
        super().__init__(video_path)
        self.parent = parent_video_signature
        self.frame_sample_rate = frame_sample_rate
        self.signature = None

    def extract_hue_values(self, frame):
        # Convert frame to HSV
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Extract the Hue component
        hue_values = hsv_frame[:, :, 0]
        return hue_values

    def extract_features(self):
        cap = cv2.VideoCapture(self.video_path)
        hue_values_set = set()

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame_count % self.frame_sample_rate != 0:
                break

            hue_values = self.extract_hue_values(frame)
            hue_values_set.update(hue_values.flatten())

            frame_count += 1

        cap.release()

        # The signature is a unique set of hue values
        self.signature = list(hue_values_set)

    def compare(self, other_signature, margin=0):
        if not self.signature:
            raise ValueError("Signature not generated. Call extract_features() first.")

        matching_hues = 0
        total_query_hues = len(self.signature)

        for query_hue in self.signature:
            if any(abs(query_hue - db_hue) <= margin for db_hue in other_signature.signature):
                matching_hues += 1

        if total_query_hues == 0:
            return 0  # No hues in query signature
        return (matching_hues / total_query_hues) * 100

    @staticmethod
    def is_color_within_margin(query_hue, db_hue, margin=10):
        return abs(query_hue - db_hue) <= margin
