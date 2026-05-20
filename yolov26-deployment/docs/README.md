# YOLOv26 目标检测部署项目

基于 Ultralytics YOLOv26 的完整目标检测部署方案，包含后端 API 服务和前端演示页面。

## 📋 项目结构

```
yolov26-deployment/
├── backend/                 # 后端服务
│   ├── main.py             # FastAPI 主程序
│   ├── requirements.txt    # Python 依赖
│   └── models/             # 模型存放目录
├── frontend/               # 前端页面
│   ├── index.html         # 主页面
│   └── app.js            # 前端逻辑
├── docs/                   # 文档
│   └── README.md         # 本文件
├── scripts/                # 脚本
│   ├── install.sh         # 安装脚本
│   └── start.sh          # 启动脚本
└── docker-compose.yml     # Docker 部署配置
```

## 🚀 快速开始

### 方式一：本地部署（推荐用于开发）

#### 1. 环境要求

- Python 3.8+
- pip
- (可选) GPU 支持需要 CUDA 11.8+

#### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

#### 3. 启动服务

```bash
cd backend
python main.py
```

服务将在 `http://localhost:8000` 启动，自动打开前端页面。

### 方式二：Docker 部署（推荐用于生产）

#### 1. 构建并启动

```bash
docker-compose up -d
```

#### 2. 访问服务

打开浏览器访问 `http://localhost:8000`

## 📚 API 文档

### 1. 健康检查

```
GET /health
```

响应示例：
```json
{
  "status": "healthy",
  "service": "yolov26-api"
}
```

### 2. 目标检测

```
POST /predict
```

参数：
- `file`: 图片文件（必需）
- `model_name`: 模型名称（可选，默认: yolo26n.pt）
- `conf`: 置信度阈值（可选，默认: 0.25）
- `iou`: IoU 阈值（可选，默认: 0.7）

响应示例：
```json
{
  "success": true,
  "detections": [
    {
      "class": 0,
      "class_name": "person",
      "confidence": 0.89,
      "bbox": [100, 200, 300, 400]
    }
  ],
  "count": 1,
  "result_image": "runs/predict/api_result/image.jpg"
}
```

### 3. 训练模型

```
POST /train
```

参数：
- `model_name`: 预训练模型名称（可选，默认: yolo26n.pt）
- `data`: 数据集配置文件路径（可选，默认: coco8.yaml）
- `epochs`: 训练轮次（可选，默认: 100）
- `imgsz`: 图片尺寸（可选，默认: 640）

### 4. 导出模型

```
POST /export
```

参数：
- `model_name`: 模型名称（可选，默认: yolo26n.pt）
- `format`: 导出格式（可选，默认: onnx）
- `end2end`: 是否使用一对一头（可选，默认: true）

支持的导出格式：
- `onnx`: ONNX 格式（通用）
- `tensorrt`: TensorRT 格式（NVIDIA GPU 加速）
- `tflite`: TensorFlow Lite 格式（移动端）
- `coreml`: CoreML 格式（Apple 设备）
- `openvino`: OpenVINO 格式（Intel 设备）

## 🎯 支持的模型

| 模型名称 | 任务类型 | 描述 |
|---------|---------|------|
| yolo26n.pt | 目标检测 | Nano 版本，速度最快 |
| yolo26s.pt | 目标检测 | Small 版本 |
| yolo26m.pt | 目标检测 | Medium 版本 |
| yolo26l.pt | 目标检测 | Large 版本，精度较高 |
| yolo26x.pt | 目标检测 | XLarge 版本，精度最高 |
| yolo26n-seg.pt | 实例分割 | Nano 分割模型 |
| yolo26n-pose.pt | 姿态估计 | Nano 姿态估计模型 |
| yolo26n-obb.pt | 旋转检测 | Nano 旋转目标检测模型 |
| yolo26n-cls.pt | 图像分类 | Nano 图像分类模型 |

## 🔧 配置说明

### 后端配置

编辑 `backend/main.py` 中的配置：

```python
# 主机地址（默认: 0.0.0.0）
host="0.0.0.0"

# 端口（默认: 8000）
port=8000

# CORS 配置
allow_origins=["*"]  # 生产环境建议设置为具体域名
```

### 前端配置

编辑 `frontend/app.js` 中的 API 地址（如果需要连接到不同的后端）：

```javascript
// 默认使用相对路径，自动连接到同域名后端
const response = await fetch('/predict', {
    method: 'POST',
    body: formData
});
```

## 🐳 Docker 部署

### 1. 构建镜像

```bash
docker build -t yolov26-api:latest .
```

### 2. 运行容器

```bash
docker run -d \
  --name yolov26-api \
  -p 8000:8000 \
  -v $(pwd)/runs:/app/runs \
  yolov26-api:latest
```

### 3. 使用 docker-compose（推荐）

```bash
docker-compose up -d
```

## 📊 性能优化

### 1. GPU 加速

确保安装了正确版本的 CUDA 和 cuDNN：

```bash
# 检查 PyTorch 是否支持 GPU
python -c "import torch; print(torch.cuda.is_available())"
```

### 2. 模型选择

- **开发/测试**: 使用 `yolo26n.pt` 或 `yolo26s.pt`
- **生产环境**: 根据精度和速度需求选择 `yolo26m.pt` 或 `yolo26l.pt`
- **高精度需求**: 使用 `yolo26x.pt`

### 3. 批量处理

对于大量图片，建议使用批量处理接口（需要自行扩展）。

## 🔒 安全建议

### 生产环境部署

1. **启用身份验证**: 添加 API Key 或 JWT 认证
2. **限制文件上传**: 限制文件大小和类型
3. **使用 HTTPS**: 配置 SSL 证书
4. **CORS 配置**: 设置具体的允许域名
5. **速率限制**: 添加请求速率限制
6. **日志记录**: 启用访问日志和错误日志

示例（添加基础认证）：

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

@app.post("/predict")
async def predict(
    credentials: HTTPBasicCredentials = Depends(security),
    file: UploadFile = File(...)
):
    # 验证用户名和密码
    if not (credentials.username == "admin" and credentials.password == "password"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    # ... 原有逻辑
```

## 🐛 常见问题

### 1. 模型下载失败

**问题**: 首次运行时模型下载失败

**解决**:
```bash
# 手动下载模型
python -c "from ultralytics import YOLO; YOLO('yolo26n.pt')"
```

### 2. CUDA 内存不足

**问题**: GPU 内存不足

**解决**:
- 使用更小的模型（如 yolo26n.pt）
- 减小输入图片尺寸（imgsz）
- 使用 CPU 推理（速度较慢）

### 3. 端口被占用

**问题**: 8000 端口已被占用

**解决**:
```bash
# 修改端口
export PORT=8001
python backend/main.py
```

## 📝 开发指南

### 添加新功能

1. 在 `backend/main.py` 中添加新的 API 端点
2. 在 `frontend/app.js` 中添加对应的前端逻辑
3. 更新本文档

### 调试模式

```bash
# 启用自动重载
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📄 许可证

- **代码**: MIT License
- **YOLOv26 模型**: AGPL-3.0（开源使用）/ 商业许可证（商业使用）

商业使用需要申请企业许可证，详情参考：https://www.ultralytics.com/license

## 🔗 相关链接

- Ultralytics 官方文档: https://docs.ultralytics.com/
- YOLOv26 模型文档: https://docs.ultralytics.com/zh/models/yolo26/
- GitHub 仓库: https://github.com/ultralytics/ultralytics
- API 文档（Swagger）: http://localhost:8000/docs

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 发送邮件: your-email@example.com

---

**部署时间**: 2026-05-19
**版本**: 1.0.0
**作者**: AI Assistant
