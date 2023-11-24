from abc import ABC, abstractmethod

class SubSignature(ABC):
    def __init__(self, video_path):
        """
        Initialize the SubSignature with a path to the video.

        :param video_path: String, path to the video file.
        """
        self.video_path = video_path

    @abstractmethod
    def extract_features(self):
        """
        Abstract method to extract features from the video.

        Implement this method in subclasses to extract specific types of features.
        """
        pass

    @abstractmethod
    def compare(self, other_signature):
        """
        Abstract method to compare this signature with another signature.

        :param other_signature: An instance of a subclass of SubSignature to compare with.
        :return: A value or object representing the comparison result.
        """
        pass
