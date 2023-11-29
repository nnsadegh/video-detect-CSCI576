import cv2
import numpy as np
import sys

"""
Inspired by the following Github repository: https://github.com/HeliosZhao/Shot-Boundary-Detection
"""


class ShotBoundaryDetector:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
        self.frames = []
        self._read_frames()

    def _read_frames(self):
        success, frame = self.cap.read()
        i = 0
        while success:
            luv = cv2.cvtColor(frame, cv2.COLOR_BGR2LUV)
            curr_frame = luv
            if i > 0:
                prev_frame = self.frames[-1].luv
                diff = cv2.absdiff(curr_frame, prev_frame)
                diff_sum = np.sum(diff)
                diff_sum_mean = diff_sum / (diff.shape[0] * diff.shape[1])
            else:
                diff_sum_mean = 0

            self.frames.append(Frame(i, diff_sum_mean, luv))
            i += 1
            success, frame = self.cap.read()
        self.cap.release()

    def detect_shot_boundaries(self):
        possible_frames = []
        window_frame = []
        window_size = 30
        m_suddenJudge = 3
        m_MinLengthOfShot = 8
        start_id_spot = [0]
        end_id_spot = []

        length = len(self.frames)
        index = 0
        while index < length:
            frame_item = self.frames[index]
            window_frame.append(frame_item)
            if len(window_frame) < window_size:
                index += 1
                if index == length - 1:
                    window_frame.append(self.frames[index])
                continue

            max_diff_frame = self._get_max_diff_frame(window_frame)
            max_diff_id = max_diff_frame.id

            if not possible_frames:
                possible_frames.append(max_diff_frame)
                continue
            last_max_frame = possible_frames[-1]

            sum_start_id = last_max_frame.id + 1
            sum_end_id = max_diff_id - 1

            id_no = sum_start_id
            sum_diff = 0
            while id_no <= sum_end_id:
                sum_frame_item = self.frames[id_no]
                sum_diff += sum_frame_item.diff
                id_no += 1

            average_diff = sum_diff / (sum_end_id - sum_start_id + 1)
            if max_diff_frame.diff >= (m_suddenJudge * average_diff):
                possible_frames.append(max_diff_frame)
                window_frame = []
                index = possible_frames[-1].id + m_MinLengthOfShot
            else:
                index = max_diff_frame.id + 1
                window_frame = []

        for i in range(len(possible_frames)):
            start_id_spot.append(possible_frames[i].id)
            end_id_spot.append(possible_frames[i].id - 1)

        sus_last_frame = possible_frames[-1]
        last_frame = self.frames[-1]
        if sus_last_frame.id < last_frame.id:
            possible_frames.append(last_frame)
            end_id_spot.append(possible_frames[-1].id)

        return list(zip(start_id_spot, end_id_spot))

    def _get_max_diff_frame(self, frame_list):
        max_diff_frame = frame_list[0]
        for frame in frame_list:
            if frame.diff > max_diff_frame.diff:
                max_diff_frame = frame
        return max_diff_frame

    """
    A method that returns a list of tuples with the start and end timestamps of each shot boundary.
    """
    def get_shot_boundary_timestamps(self):
        shot_boundaries = self.detect_shot_boundaries()
        timestamps = [(start_frame / self.frame_rate, end_frame / self.frame_rate) for start_frame, end_frame in shot_boundaries]
        return timestamps

    """
    A method that returns a list of tuples with the start and end frame of each shot boundary.
    """
    def get_shot_boundary_frames(self):
        shot_boundaries = self.detect_shot_boundaries()
        frames = [(start_frame, end_frame) for start_frame, end_frame in shot_boundaries]
        return frames


class Frame:
    def __init__(self, id, diff, luv):
        self.id = id
        self.diff = diff
        self.luv = luv

    def __lt__(self, other):
        return self.id < other.id

    def __gt__(self, other):
        return self.id > other.id

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)