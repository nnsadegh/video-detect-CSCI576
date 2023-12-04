import os
import pickle
from shot_boundary_detector import ShotBoundaryDetector
from video_signature import VideoSignature
from video_player import VideoPlayer  # Import the VideoPlayer class
import cv2
from scenedetect import detect, ContentDetector, split_video_ffmpeg
import time

from skimage.metrics import structural_similarity as ssim
import numpy as np



#This is all preprocessing, we would not run this function in the demo
#This will is to create the pickle file to act as the database of the dictionary
def process_videos():
    #Loops through every video in the database
    db_video_path = '/Users/piar/CSCI-576Project/Videos' # CHANGE THIS FOR YOU LOCAL
    videos_frames = {}
    for file in os.listdir(db_video_path):
        file_path = os.path.join(db_video_path, file)
    #     # Check if the file is an MP4 video
        if os.path.isfile(file_path) and file.lower().endswith('.mp4'):
            # if file_path == '/Users/piar/CSCI-576Project/Videos/video8.mp4': #This was for testing you can remove this
                #Creating the shotboundary of the video and outputting a list where each shot boundary start and end frame is
            cap = cv2.VideoCapture(file_path)
            scene_list = detect(file_path, ContentDetector(threshold=4.0, weights= ContentDetector.Components(delta_hue=0.0, delta_sat=0.0, delta_lum=1.0, delta_edges=0.0)))
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            for i, scene in enumerate(scene_list):
                frames = scene[1].get_frames() - scene[0].get_frames()
                startframe = scene[0].get_frames()
                print('Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
                    i+1,
                    scene[0].get_timecode(), scene[0].get_frames(),
                    scene[1].get_timecode(), scene[1].get_frames(),
                    ), 'Frames:', frames )

            #Creates an image for the first frame of each shot boundary and adds it to an output path
            cap.set(cv2.CAP_PROP_POS_FRAMES,startframe)
            ret, frame = cap.read()
            output_path= f'/Users/piar/CSCI-576Project/Videos/Frame_Path/{base_name}_{startframe}.png'  #CHANGE THIS FOR YOUR LOCAL
            cv2.imwrite(output_path, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            #This creates the dictionary Key: number of frames in shot Value: List of image paths where the shot boundary is the same number of frames
            if frames in videos_frames:
                        videos_frames[frames].append((startframe, output_path))
            else:
                # If the key doesn't exist, create a new array with the current element
                videos_frames[frames] = [(startframe, output_path)]

    #Loads dictionary into a pickle file to be accessed later 
    with open('my_dict.pkl', 'wb') as pickle_file:
            pickle.dump(videos_frames, pickle_file)

    # return videos_frames


#Compare images and returns a mean squared error of similarity
def compare_images(query_path,video_path):
    hsv_image1 = cv2.imread(query_path)
    hsv_image2 = cv2.imread(video_path)
    min_side = min(hsv_image2.shape[0], hsv_image2.shape[1], hsv_image1.shape[0], hsv_image1.shape[1])

    # Set the window size to an odd value less than or equal to the smaller side
    win_size = min(min_side, 7)
    # _, similarity_index = ssim(hsv_image1, hsv_image2, win_size=win_size, channel_axis=-1,multichannel=True,full=True)
    mse = np.sum((hsv_image1 - hsv_image2) ** 2) / float(hsv_image1.shape[0] * hsv_image1.shape[1])
    return mse

def main():
    start_time = time.time()
    # Input query file and create shot boundary
    query_file_path= '/Users/piar/CSCI-576Project/Queries/video8_1.mp4' #FIX THIS FOR YOUR LOCAL
    cap = cv2.VideoCapture(query_file_path)
    scene_list = detect(query_file_path, ContentDetector(threshold=3.0, weights= ContentDetector.Components(delta_hue=0.0, delta_sat=0.0, delta_lum=1.0, delta_edges=0.0)))

    #Dictonary to find max shot boundary within a query video and store the startframe of this shot
    frameNums = {}
    for i, scene in enumerate(scene_list):
        frames = scene[1].get_frames() - scene[0].get_frames()
        startframe = scene[0].get_frames()
        print('Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
            i+1,
            scene[0].get_timecode(), scene[0].get_frames(),
            scene[1].get_timecode(), scene[1].get_frames(),
            ), 'Frames:', frames )
        #skip first shot boundary as it might not be the starting boundary in the actual video
        if startframe!=0 and scene[1].get_timecode() != '00:00:20.000':
            #Store shot boundary in dictionary Key: startframe Value: # of frames in shot
            frameNums[startframe] = frames

    #Start frame of the shot within query with most frames
    max_shot_start = max(frameNums, key=lambda k: frameNums[k])    
    
    #Number of frames for the shot that has max frames in query 
    max_shot_frames = frameNums[max_shot_start]
   

    #Create image of the start frame from max frames
    cap.set(cv2.CAP_PROP_POS_FRAMES,max_shot_start)
    ret, frame = cap.read()
    #Output path of query start frame image
    query_image_file= f'/Users/piar/CSCI-576Project/Queries/{max_shot_start}.png'  #FIX TO MATCH YOUR LOCAL
    cv2.imwrite(query_image_file, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    #Only call if you need to preprocess videos 
    process_videos()

    #Opens preprocessed dictionary of frames, and start frame image file paths for shots with the same frame count
    with open('my_dict.pkl', 'rb') as pickle_file:
        frame_match = pickle.load(pickle_file)
    #dictionary for comparison
    comparison = {}
    #Find in dictionary the max number of frames for a shot within the query video
    for startframe, imgpath in frame_match[max_shot_frames]:
         #grabs each image path with the same frame number and compares the starting frame images
         comparison[imgpath] = compare_images(query_image_file,imgpath)
        #  print(comparison[imgpath] )
    
    #Finds the closest image
    best_image = min(comparison, key=lambda k: comparison[k])

    #Grabe video this image comes from
    base_name = os.path.splitext(os.path.basename(best_image))[0]
    # print("video: ", base_name)
    print(query_file_path)
    #Grab frame number from file path name
    name_parts = base_name.split("_")
    #Frame of the matching shot boundary
    bound_frame = name_parts[1]
    #Actual start frame of the query
    start_frame = int(bound_frame) - max_shot_start - 1 
    # print("shot bound start frame: ", bound_frame)
    print("Actual query start frame: ", start_frame)
    end_time = time.time()
    print(f"Function took {end_time - start_time} seconds to execute.")



if __name__ == "__main__":
    main()
