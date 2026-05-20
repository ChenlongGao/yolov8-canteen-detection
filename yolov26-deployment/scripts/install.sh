#!/bin/bash

# YOLOv26 部署 - 安装脚本

set -e  # 遇到错误立即退出

echo "================================================"
echo "   YOLOv26 目标检测 - 安装脚本"
echo "================================================"
echo ""

# 检查 Python 版本
echo "[1/5] 检查 Python 版本..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3，请先安装 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python 版本: $PYTHON_VERSION"
echo ""

# 检查 pip
echo "[2/5] 检查 pip..."
if ! command -v pip3 &> /dev/null; then
    echo "❌ 错误: 未找到 pip3，请先安装 pip"
    exit 1
fi
echo "✅ pip 已安装"
echo ""

# 创建虚拟环境（可选）
echo "[3/5] 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境已创建"
else
    echo "✅ 虚拟环境已存在"
fi
echo ""

# 激活虚拟环境
echo "[4/5] 激活虚拟环境并安装依赖..."
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r backend/requirements.txt

echo "✅ 依赖安装完成"
echo ""

# 检查 CUDA（可选）
echo "[5/5] 检查 CUDA 支持..."
if python3 -c "import torch; print(torch.cuda.is_available())" 2>/dev/null | grep -q "True"; then
    echo "✅ CUDA 可用，将使用 GPU 加速"
else
    echo "⚠️  CUDA 不可用，将使用 CPU 推理（速度较慢）"
fi
echo ""

echo "================================================"
echo "   安装完成！"
echo "================================================"
echo ""
echo "下一步："
echo "  1. 启动服务: ./scripts/start.sh"
echo "  2. 访问地址: <ADDRESS_REMOVED>"
echo ""
echo "或使用 Docker 部署:"
echo "  docker-compose up -d"
echo ""
