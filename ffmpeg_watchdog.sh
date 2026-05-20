#!/bin/bash
# FFmpeg 守护进程 - 崩溃自动重启
VIDEO="/Users/paocai/Desktop/yoloceshi/测试视频icyq.mp4"
LOG="/tmp/ffmpeg_watchdog.log"

echo "$(date) 守护启动" >> "$LOG"

while true; do
    if ! pgrep -f "ffmpeg.*mystream" > /dev/null; then
        echo "$(date) FFmpeg 已停止，重启..." >> "$LOG"
        nohup ffmpeg -re -stream_loop -1 -i "$VIDEO" \
            -c:v libx264 -preset ultrafast -tune zerolatency \
            -c:a aac -rtsp_transport tcp \
            -f rtsp rtsp://localhost:8554/mystream \
            > /tmp/ffmpeg.log 2>&1 &
    fi
    sleep 5
done
