# CSCI 576 Multimedia Project - Fall 2023

## Overview

The CSCI 576 Multimedia Project for Fall 2023 is a challenging and innovative venture into the world of multimedia processing and analysis. We developed a system capable of searching and indexing into video and audio, displaying results in an interactive media player. This project makes use of OpenCV and Qt to create a robust and efficient system.

### Instructor: **Parag Havaldar**

## Project Description

The project involves creating a system that can search and index video/audio data. Unlike simple media types like text, video and audio present unique challenges in indexing and searching due to their complex nature.

### Key Features
- **Database of Videos**: A collection of videos with synchronized audio, each longer than ten minutes.
- **Query Snippet**: A 20-40 second video (with synchronized audio) snippet, which should be an exact match to some content in a video in the database.
- **Digital Signatures**: Preprocess videos to create digital signatures and sub-signatures for efficient pattern matching.
- **Sub Signature Matching**: Develop a process to match the sub signature within all the signatures, pointing to the correct video and the exact frame offset.
- **Custom Video Player**: Display the output in a custom video player with basic functions like play, pause, and reset, along with audio/video synchronization.

### Execution Command
```hashing.py QueryVideoPath.mp4```

## Preprocessing and Signature Creation

Analyze the entire video to create a digital signature. This involves creating
a hash for each frame and performing a simple lookup once the query video is submitted.

## Output Display

The output will be displayed in a custom video player. The player should have the following functionalities:

- Play from the current frame
- Pause while the video is playing
- Reset to the start of the video
- Synchronizes audio and video seamlessly