from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# PyTorch 2.6+ 兼容性修复 - 必须在 ultralytics 导入之前
import torch
_orig_load = torch.load
def _patched_load(*args, **kwargs):
    kwargs.setdefault('weights_only', False)
    return _orig_load(*args, **kwargs)
torch.load = _patched_load

from ultralytics import YOLO
import shutil
import tempfile
import os
from pathlib import Path
from typing import Optional
import cv2
import numpy as np

app = FastAPI(title="YOLOv8 目标检测 API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局模型缓存
models = {}

def get_model(model_name: str = "yolov8n.pt"):
    """获取或加载模型"""
    if model_name not in models:
        try:
            models[model_name] = YOLO(model_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")
    return models[model_name]

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "message": "YOLOv26 目标检测 API 服务",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API 信息",
            "GET /health": "健康检查",
            "POST /predict": "目标检测",
            "POST /train": "训练模型",
            "POST /export": "导出模型",
            "GET /models": "可用模型列表"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "yolov8-api"}

@app.get("/models")
async def list_models():
    """列出可用的 YOLOv26 模型"""
    models_list = [
        {"name": "yolov8n.pt", "task": "检测", "description": "Nano 检测模型"},
        {"name": "yolov8s.pt", "task": "检测", "description": "Small 检测模型"},
        {"name": "yolov8m.pt", "task": "检测", "description": "Medium 检测模型"},
        {"name": "yolov8l.pt", "task": "检测", "description": "Large 检测模型"},
        {"name": "yolov8x.pt", "task": "检测", "description": "XLarge 检测模型"},
        {"name": "yolov8n-seg.pt", "task": "分割", "description": "Nano 分割模型"},
        {"name": "yolov8n-pose.pt", "task": "姿态", "description": "Nano 姿态估计模型"},
        {"name": "yolov8n-obb.pt", "task": "旋转检测", "description": "Nano 旋转目标检测模型"},
        {"name": "yolov8n-cls.pt", "task": "分类", "description": "Nano 图像分类模型"},
    ]
    return {"models": models_list}

@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    model_name: str = "yolov8n.pt",
    conf: float = 0.25,
    iou: float = 0.7
):
    """
    目标检测接口
    
    - **file**: 上传的图片文件
    - **model_name**: 模型名称 (默认: yolov8n.pt)
    - **conf**: 置信度阈值 (默认: 0.25)
    - **iou**: IoU 阈值 (默认: 0.7)
    """
    # 保存上传的文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # 加载模型
        model = get_model(model_name)
        
        # 执行预测
        results = model.predict(
            source=tmp_path,
            conf=conf,
            iou=iou,
            save=False,
            project="runs/predict",
            name="api_result"
        )
        
        result = results[0]
        
        # 读取处理后的图片
        save_dir = Path("runs/predict/api_result")
        if save_dir.exists():
            image_files = list(save_dir.glob("*.jpg"))
            result_image_path = str(image_files[0]) if image_files else None
        else:
            result_image_path = None
        
        # 提取检测信息
        detections = _extract_detections(result, model)
        
        return {
            "success": True,
            "detections": detections,
            "count": len(detections),
            "result_image": result_image_path
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")
    finally:
        os.unlink(tmp_path)


@app.post("/track")
async def track(
    file: UploadFile = File(...),
    model_name: str = "yolov8n.pt",
    conf: float = 0.25,
    iou: float = 0.7,
    track_threshold: float = 0.3
):
    """
    目标追踪接口（带 track_id）
    
    - **file**: 上传的图片文件
    - **model_name**: 模型名称，仅检测模型支持追踪
    - **conf**: 置信度阈值 (默认: 0.25)
    - **iou**: IoU 阈值 (默认: 0.7)
    - **track_threshold**: 追踪匹配阈值 (默认: 0.3)
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        model = get_model(model_name)
        
        # 执行追踪
        results = model.track(
            source=tmp_path,
            conf=conf,
            iou=iou,
            tracker="bytetrack.yaml",
            persist=True
        )
        
        result = results[0]
        
        detections = []
        if result.boxes is not None:
            boxes = result.boxes
            for i in range(len(boxes)):
                bbox = boxes.xyxy[i].tolist()
                cls_id = int(boxes.cls[i].item())
                det = {
                    "class": cls_id,
                    "class_name": model.names[cls_id],
                    "confidence": float(boxes.conf[i].item()),
                    "bbox": bbox,
                    "center": [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
                }
                if boxes.id is not None:
                    det["track_id"] = int(boxes.id[i].item())
                detections.append(det)
        
        return {
            "success": True,
            "detections": detections,
            "count": len(detections),
            "mode": "tracking"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"追踪失败: {str(e)}")
    finally:
        os.unlink(tmp_path)


def _extract_detections(result, model):
    """提取检测结果"""
    detections = []
    if result.boxes is not None:
        boxes = result.boxes
        for i in range(len(boxes)):
            bbox = boxes.xyxy[i].tolist()
            cls_id = int(boxes.cls[i].item())
            detection = {
                "class": cls_id,
                "class_name": model.names[cls_id],
                "confidence": float(boxes.conf[i].item()),
                "bbox": bbox,
                "center": [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
            }
            if boxes.id is not None:
                detection["track_id"] = int(boxes.id[i].item())
            detections.append(detection)
    return detections

@app.post("/train")
async def train(
    model_name: str = "yolov8n.pt",
    data: str = "coco8.yaml",
    epochs: int = 100,
    imgsz: int = 640
):
    """
    训练模型接口
    
    - **model_name**: 预训练模型名称
    - **data**: 数据集配置文件路径
    - **epochs**: 训练轮次
    - **imgsz**: 图片尺寸
    """
    try:
        model = get_model(model_name)
        
        results = model.train(
            data=data,
            epochs=epochs,
            imgsz=imgsz,
            project="runs/train",
            name="api_train"
        )
        
        return {
            "success": True,
            "message": "训练完成",
            "results": str(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"训练失败: {str(e)}")

@app.post("/export")
async def export(
    model_name: str = "yolov8n.pt",
    format: str = "onnx",
    end2end: bool = True
):
    """
    导出模型接口
    
    - **model_name**: 模型名称
    - **format**: 导出格式 (onnx, tensorrt, tflite, coreml 等)
    - **end2end**: 是否使用一对一头 (默认: True)
    """
    try:
        model = get_model(model_name)
        
        export_path = model.export(
            format=format,
            end2end=end2end
        )
        
        return {
            "success": True,
            "message": "模型导出成功",
            "export_path": str(export_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出失败: {str(e)}")

# 静态文件服务 (用于前端)
frontend_path = Path("../frontend")
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
