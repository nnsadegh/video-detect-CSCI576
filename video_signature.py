from color_sub_signature import ColorSubSignature  # Ensure this is correctly imported


class VideoSignature:
    def __init__(self, video_path):
        """
        Initialize the VideoSignature with a path to the video.

        :param video_path: String, path to the video file.
        :param cluster_size: Integer, number of color clusters for the signature.
        :param frame_sample_rate: Integer, rate at which frames are sampled from the video.
        """
        self.video_path = video_path
        self.video_name = video_path.split('/')[-1]  # Extract the video name
        self.color_signature = ColorSubSignature(video_path)

    def generate_signature(self):
        """
        Generate the video signature by extracting color features.
        """
        self.color_signature.extract_features()
        return self

    def compare(self, other_video_signature):
        """
        Compare this video signature with another video signature.

        :param other_video_signature: An instance of VideoSignature.
        :return: A value representing the comparison result.
        """
        if not isinstance(other_video_signature, VideoSignature):
            raise ValueError("The argument must be an instance of VideoSignature")

        return self.color_signature.compare(other_video_signature.color_signature)

