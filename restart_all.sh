#!/bin/bash
# 一键重启所有 YOLO 检测系统服务
set -e

echo "=== 停止旧服务 ==="
kill $(lsof -ti :8000) 2>/dev/null || true
kill $(lsof -ti :8554) 2>/dev/null || true
kill $(lsof -ti :8888) 2>/dev/null || true
pkill -f "ffmpeg.*mystream" 2>/dev/null || true
sleep 1

DIR="$(cd "$(dirname "$0")" && pwd)"
VIDEO="/Users/paocai/Desktop/yoloceshi/测试视频icyq.mp4"
VENV="$DIR/yolov26-deployment/venv/bin/activate"
BACKEND="$DIR/yolov26-deployment/backend"

echo "=== 启动 MediaMTX ==="
cd "$DIR"
nohup ./mediamtx mediamtx.yml > mediamtx.log 2>&1 &
sleep 2
lsof -i :8554 | grep -q LISTEN && echo "  MediaMTX ✓" || echo "  MediaMTX ✗"

echo "=== 启动 FFmpeg ==="
nohup ffmpeg -re -stream_loop -1 -i "$VIDEO" -c:v libx264 -preset ultrafast -tune zerolatency -c:a aac -rtsp_transport tcp -f rtsp rtsp://localhost:8554/mystream > /tmp/ffmpeg.log 2>&1 &
sleep 2
pgrep -f "ffmpeg.*mystream" > /dev/null && echo "  FFmpeg ✓" || echo "  FFmpeg ✗"

echo "=== 启动 YOLO API ==="
cd "$BACKEND"
source "$VENV"
nohup python3 main.py > /tmp/yolo_api.log 2>&1 &
sleep 5
curl -s http://localhost:8000/health | grep -q healthy && echo "  YOLO API ✓" || echo "  YOLO API ✗"

echo ""
echo "=== 全部启动完成 ==="
echo "  前端页面: http://localhost:8001/yolov26-rtsp-detection.html"
echo "  API 文档: http://localhost:8000/docs"
