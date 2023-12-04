import sys
import time
import cv2
import hashlib
import os
import pickle
from video_player import VideoPlayer


class VideoFrameHasher:
    def __init__(self):
        self.database = {}

    def process_video(self, video_path):
        """ Process a video and store its hashes in the database."""
        cap = cv2.VideoCapture(video_path)
        frame_count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            hash_value = self.compute_hash(frame)
            self.database[hash_value] = (video_path, frame_count)
            frame_count += 1

        cap.release()

    def compute_hash(self, frame):
        """ Compute the hash of a given frame."""
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return hashlib.md5(gray_frame.tobytes()).hexdigest()

    def find_match(self, query_frame):
        """ Find a match for a given query frame in the database."""
        query_hash = self.compute_hash(query_frame)
        result = self.database.get(query_hash, None)
        # Subtract 1 from the frame number because the frame number is 0-indexed
        if result:
            return result[0], result[1] - 1
        return self.database.get(query_hash, None)

    def process_query_video(self, query_video_path):
        """ Process a query video and find a match in the database."""
        cap = cv2.VideoCapture(query_video_path)
        ret, frame = cap.read()
        if not ret:
            return None

        cap.release()
        return self.find_match(frame)

    def process_directory(self, directory_path):
        """ Process all videos in a given directory. """
        for filename in os.listdir(directory_path):
            if filename.endswith('.mp4'):  # assuming video files are .mp4
                self.process_video(os.path.join(directory_path, filename))

    def save_database(self, file_path):
        """ Save the database using pickle. """
        with open(file_path, 'wb') as file:
            pickle.dump(self.database, file)

    def load_database(self, file_path):
        """ Load the database from a pickle file. """
        with open(file_path, 'rb') as file:
            self.database = pickle.load(file)


def main(query_filename):
    hasher = VideoFrameHasher()

    # Path to the directory containing database videos
    database_directory_path = 'db_videos'
    database_file_path = 'database/database.pkl'

    # Check if database file exists
    if os.path.exists(database_file_path):
        # Load the database
        hasher.load_database(database_file_path)
        print("Database loaded.")
    else:
        # Create the directory if it doesn't exist
        os.makedirs(database_directory_path, exist_ok=True)

        # Process all videos in the directory
        hasher.process_directory(database_directory_path)
        print("Database directory processed.")

        # Save the database
        os.makedirs('database', exist_ok=True)
        hasher.save_database(database_file_path)
        print("Database saved.")

    # Path to the query video
    query_video_path = os.path.join('queries', query_filename)
    start_time = time.time()  # Start time for processing
    match_info = hasher.process_query_video(query_video_path)
    end_time = time.time()  # End time for processing

    # Print the result and processing time
    if match_info:
        print(f"Match found in '{match_info[0]}' at frame number {match_info[1]} for {query_filename}.")
        # Play the matched video starting from the matched frame
        print(f"Processing time: {end_time - start_time:.2f} seconds\n")
        # VideoPlayer(match_info[0], start_frame=match_info[1]).play_video()
    else:
        print(f"No match found for {query_filename}.")

    # # Path to the directory containing query videos
    # query_directory_path = 'queries'
    #
    # # Process each query video in the directory
    # for filename in os.listdir(query_directory_path):
    #     if filename.endswith('.mp4'):
    #         query_video_path = os.path.join(query_directory_path, filename)
    #
    #         start_time = time.time()  # Start time for processing
    #         match_info = hasher.process_query_video(query_video_path)
    #         end_time = time.time()  # End time for processing
    #
    #         # Print the result and processing time
    #         if match_info:
    #             print(f"Match found in '{match_info[0]}' at frame number {match_info[1] - 1} for {filename}.")
    #         else:
    #             print(f"No match found for {filename}.")
    #         print(f"Processing time: {end_time - start_time:.2f} seconds\n")


if __name__ == "__main__":
    main(sys.argv[1])
