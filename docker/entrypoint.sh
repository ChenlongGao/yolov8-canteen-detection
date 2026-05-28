#!/bin/bash
set -e

echo "=== YOLOv26 检测系统启动 ==="

# 启动 MediaMTX
echo "[1/4] 启动 MediaMTX..."
mediamtx /app/mediamtx.yml > /tmp/mediamtx.log 2>&1 &
sleep 2

# 启动 FFmpeg (如果视频文件存在)
if [ -f /app/video.mp4 ]; then
    echo "[2/4] 启动 FFmpeg 推流..."
    ffmpeg -re -stream_loop -1 -i /app/video.mp4 \
        -vf "scale=1280:720" \
        -c:v libx264 -preset ultrafast -tune zerolatency \
        -b:v 2M -maxrate 2M -bufsize 4M \
        -pix_fmt yuv420p \
        -c:a aac -ar 44100 -ac 1 -b:a 64k \
        -rtsp_transport tcp -f rtsp \
        "rtsp://localhost:8554/mystream" > /tmp/ffmpeg.log 2>&1 &
else
    echo "[2/4] 无视频文件，跳过 FFmpeg"
fi

# 启动 YOLO API
echo "[3/4] 启动 YOLO API..."
cd /app/yolov26-deployment/backend
python3 main.py > /tmp/yolo_api.log 2>&1 &

# 启动 Node.js 代理
echo "[4/4] 启动前端代理 (端口: ${PORT:-8080})..."
cd /app
exec node hls_proxy.js
