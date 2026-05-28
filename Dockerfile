FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Asia/Shanghai \
    PORT=8080

# ========== 系统依赖 ==========
RUN apt update && apt install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    curl wget ca-certificates git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# ========== Node.js 20.x ==========
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# ========== MediaMTX (从本地文件) ==========
COPY mediamtx_linux.tar.gz /tmp/mediamtx.tar.gz
RUN tar -xzf /tmp/mediamtx.tar.gz -C /usr/local/bin/ && rm /tmp/mediamtx.tar.gz

# ========== Python 依赖 ==========
RUN python3 -m pip install --break-system-packages --no-cache-dir \
    fastapi uvicorn python-multipart \
    ultralytics torch --index-url https://download.pytorch.org/whl/cpu \
    opencv-python-headless insightface numpy \
    && python3 -m pip install --break-system-packages --no-cache-dir mediapipe 2>/dev/null || true

# ========== 工作目录 ==========
WORKDIR /app

# 复制应用代码
COPY . /app/

# 配置文件
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ========== 启动 ==========
EXPOSE 8080
CMD ["/entrypoint.sh"]
