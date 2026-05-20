# YOLOv26 目标检测 API - Docker 镜像

FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# 创建必要的目录
RUN mkdir -p runs/predict/api_result

# 暴露端口
EXPOSE 8000

# 启动命令
WORKDIR /app/backend
CMD ["python", "main.py"]
