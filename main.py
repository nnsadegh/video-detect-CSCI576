import os
import pickle

from video_signature import VideoSignature
from video_player import VideoPlayer  # Import the VideoPlayer class


def main():
    os.makedirs('db_signatures', exist_ok=True)

    # Iterate through all videos in the database in db_videos folder
    for file in os.listdir('db_videos'):
        file_path = os.path.join('db_videos', file)
        if os.path.isfile(file_path):
            # Create a VideoSignature object for the video
            video_signature = VideoSignature(file_path)
            # Generate the signature for the video
            video_signature.generate_signature()
            # Save the signature to a file
            signature_file = os.path.join('db_signatures', f'{file}.pkl')
            with open(signature_file, 'wb') as f:
                pickle.dump(video_signature, f)

    # Load the Database signatures into an array
    db_signatures = []
    for file in os.listdir('db_signatures'):
        file_path = os.path.join('db_signatures', file)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                db_signatures.append(pickle.load(f))

    # Create a VideoSignature object for the query video
    query_video_path = 'queries/video3_1.mp4'
    query_video_signature = VideoSignature(query_video_path).generate_signature()

    # Compare the query video signature with each database video signature and save the results to a map where the key is the name of the database video and the value is the comparison result
    comparison_results = {}
    for db_signature in db_signatures:
        comparison_results[db_signature.video_name] = query_video_signature.compare(db_signature)

    # Get the maximum comparison result from the map and print the name of the database video with the maximum comparison result
    max_comparison_result = max(comparison_results, key=comparison_results.get)
    print(f"The closest match is: {max_comparison_result}")
    print("Displaying Matched Video...")
    
    # Create an instance of the VideoPlayer class and play the macthed video
    matched_video_path = os.path.join('db_videos', max_comparison_result)
    matched_player = VideoPlayer(video_path=matched_video_path, title="Detected Matched Video")
    matched_player.play_video()


if __name__ == "__main__":
    main()
