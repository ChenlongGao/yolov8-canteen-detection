#!/bin/bash

# YOLOv26 部署 - 启动脚本

echo "================================================"
echo "   YOLOv26 目标检测 - 启动服务"
echo "================================================"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 错误: 未找到虚拟环境，请先运行安装脚本:"
    echo "   ./scripts/install.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查端口是否被占用
PORT=8000
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  警告: 端口 $PORT 已被占用"
    echo "请停止占用该端口的进程，或修改 backend/main.py 中的端口配置"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "正在启动服务..."
echo "访问地址: <ADDRESS_REMOVED>"
echo "API 文档: http://localhost:$PORT/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo "================================================"
echo ""

# 启动服务
cd backend
python main.py
