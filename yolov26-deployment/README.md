# YOLOv26 目标检测部署项目

![YOLOv26](https://img.shields.io/badge/YOLOv26-Ultralytics-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-teal)

基于 Ultralytics YOLOv26 的完整目标检测部署方案，包含后端 API 服务和前端演示页面。

## 🎯 项目特点

- ✅ **一键部署**: 支持本地部署和 Docker 部署
- ✅ **完整功能**: 目标检测、训练、导出等完整功能
- ✅ **友好界面**: 现代化的 Web 演示界面
- ✅ **高性能**: 支持 GPU 加速，YOLOv26 一对一头无需 NMS
- ✅ **易扩展**: 基于 FastAPI，易于添加新的 API 端点

## 📸 演示截图

（待添加演示截图）

## 🚀 快速开始

### 方式一：本地部署（推荐用于开发）

```bash
# 1. 运行安装脚本
./scripts/install.sh

# 2. 启动服务
./scripts/start.sh

# 3. 访问服务
# 打开浏览器访问: <ADDRESS_REMOVED>
```

### 方式二：Docker 部署（推荐用于生产）

```bash
# 1. 构建并启动
docker-compose up -d

# 2. 访问服务
# 打开浏览器访问: <ADDRESS_REMOVED>
```

## 📚 功能列表

### 1. 目标检测

- 支持多种 YOLOv26 模型（Nano、Small、Medium、Large、XLarge）
- 支持多种任务（检测、分割、姿态估计、旋转检测、分类）
- 可调节置信度阈值和 IoU 阈值
- 实时显示检测结果和统计信息

### 2. 模型训练

- 支持自定义数据集训练
- 可配置训练参数（轮次、图片尺寸等）
- 自动保存训练结果

### 3. 模型导出

- 支持多种导出格式（ONNX、TensorRT、TFLite、CoreML 等）
- 支持一对一头和一对多头导出
- 适配不同部署场景

## 🔧 API 文档

启动服务后，访问 `http://localhost:8000/docs` 查看完整的 Swagger API 文档。

### 主要端点

- `GET /`: API 信息
- `GET /health`: 健康检查
- `POST /predict`: 目标检测
- `POST /train`: 训练模型
- `POST /export`: 导出模型
- `GET /models`: 可用模型列表

## 📁 项目结构

```
yolov26-deployment/
├── backend/                 # 后端服务
│   ├── main.py            # FastAPI 主程序
│   └── requirements.txt   # Python 依赖
├── frontend/               # 前端页面
│   ├── index.html        # 主页面
│   └── app.js           # 前端逻辑
├── docs/                   # 文档
│   └── README.md        # 详细文档
├── scripts/                # 脚本
│   ├── install.sh        # 安装脚本
│   └── start.sh         # 启动脚本
├── Dockerfile              # Docker 镜像构建文件
├── docker-compose.yml      # Docker Compose 配置
└── README.md             # 本文件
```

## 🔬 技术栈

### 后端

- **FastAPI**: 现代、快速的 Web 框架
- **Ultralytics YOLOv26**: 最新的目标检测模型
- **Uvicorn**: ASGI 服务器

### 前端

- **HTML5**: 页面结构
- **CSS3**: 样式设计（渐变、动画、响应式）
- **Vanilla JavaScript**: 前端逻辑

### 部署

- **Docker**: 容器化部署
- **Docker Compose**: 多容器编排
- **Nginx**: 反向代理（可选）

## 📊 性能对比

| 模型 | 输入尺寸 | mAP50-95 | CPU 延迟 | GPU 延迟 |
|------|---------|----------|----------|----------|
| YOLOv26-Nano | 640 | 37.6 | 12ms | 1.7ms |
| YOLOv26-Small | 640 | 45.5 | 22ms | 2.3ms |
| YOLOv26-Medium | 640 | 51.8 | 45ms | 3.8ms |
| YOLOv26-Large | 640 | 54.8 | 72ms | 5.2ms |
| YOLOv26-XLarge | 640 | 56.5 | 98ms | 6.8ms |

*注: GPU 延迟基于 NVIDIA T4，CPU 延迟基于 Intel Xeon*

## 🔒 安全建议

生产环境部署时，请务必：

1. **启用身份验证**: 添加 API Key 或 JWT 认证
2. **限制文件上传**: 限制文件大小和类型
3. **使用 HTTPS**: 配置 SSL 证书
4. **CORS 配置**: 设置具体的允许域名
5. **速率限制**: 添加请求速率限制
6. **日志记录**: 启用访问日志和错误日志

详见 `docs/README.md` 中的安全配置章节。

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
3. 更新文档

### 调试模式

```bash
# 启用自动重载
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📄 许可证

- **代码**: MIT License
- **YOLOv26 模型**: AGPL-3.0（开源使用）/ 商业许可证（商业使用）

商业使用需要申请企业许可证，详情参考：https://www.ultralytics.com/license

## 🔗 相关链接

- [Ultralytics 官方文档](https://docs.ultralytics.com/)
- [YOLOv26 模型文档](https://docs.ultralytics.com/zh/models/yolo26/)
- [GitHub 仓库](https://github.com/ultralytics/ultralytics)
- [API 文档（Swagger）](http://localhost:8000/docs)

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 发送邮件: your-email@example.com

---

**部署时间**: 2026-05-19  
**版本**: 1.0.0  
**作者**: AI Assistant

---

## ⭐ 鸣谢

感谢 [Ultralytics](https://www.ultralytics.com/) 团队开发的 YOLOv26 模型和相关工具。
