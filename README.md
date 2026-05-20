# YOLO 实时检测系统 - 餐饮就餐区监控

基于 YOLOv8 + MediaMTX + FFmpeg + FastAPI 的实时视频检测分析系统。

## 架构

```
测试视频(MP4) → FFmpeg(RTSP推流) → MediaMTX(RTSP/HLS) → 浏览器(HLS.js)
                                                              ↓
                                              YOLOv8 API(8000) ← 截帧上传
                                                              ↓
                                              前端 Canvas 覆盖层（检测框+追踪轨迹）
```

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| YOLOv8 API | 8000 | FastAPI 检测接口 |
| MediaMTX RTSP | 8554 | RTSP 推流 |
| MediaMTX HLS | 8888 | HLS 播放 |
| HTTP Server | 8001 | 前端静态页面 |

## 快速启动

```bash
# 1. 安装依赖
cd yolov26-deployment/backend
pip install -r requirements.txt

# 2. 下载模型（放到 backend/ 目录）
# yolov8n.pt, yolov8n-pose.pt

# 3. 一键启动
bash restart_all.sh
```

## 前端功能

- **Tab 布局**: 实时检测 + YOLO配置
- **检测过滤**: ROI区域、检测框尺寸、画线多边形
- **目标追踪**: IOU匹配 + 红色轨迹线（支持精度/长度配置）
- **配置持久化**: localStorage 自动保存，刷新不丢失
- **自动恢复**: HLS 断流自动重连

## 模型

使用 ultralytics YOLOv8 系列：
- `yolov8n.pt` - Nano 检测模型
- `yolov8n-pose.pt` - Nano 姿态估计模型
