#!/bin/bash
while [ 1 ]
do
    set -e
    URL=$(python3 main.py)
    set +e
    ffmpeg -i $URL -c:v libx264  -f segment -segment_time 300 -g 10 -sc_threshold 0 -reset_timestamps 1 -strftime 1 /download/%Y-%m-%d_%H-%M-%S-Garage.mp4
done