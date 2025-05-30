#!/bin/bash

BROKER="172.16.16.217"
PORT="1883"
TOPIC="sunglasses/commands"
MESSAGE='{"command": "start"}'

rpicam-vid -t 0 --camera 0 --nopreview --codec yuv420 --width 1280 --height 720 --framerate 10 --inline --listen -o - | \
ffmpeg -f rawvideo -pixel_format yuv420p -video_size 1280x720 -framerate 10 -i - -vcodec libx264 -preset ultrafast -tune zerolatency -f rtsp -rtsp_transport tcp rtsp://172.16.16.15:8554/cam1 &

VID_PID=$!
echo $VID_PID > /home/pi5/stream/temp.txt

sleep 5

mosquitto_pub -h "$BROKER" -p "$PORT" -t "$TOPIC" -m "$MESSAGE"
