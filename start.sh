#!/bin/bash
# AI 桌面助手 - 一键启动脚本
cd "$(dirname "$0")"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python 3，请先安装 Python 3.8+"
    exit 1
fi

# 检查依赖
echo "检查依赖..."
MISSING=""
python3 -c "import customtkinter" 2>/dev/null || MISSING="$MISSING customtkinter"
python3 -c "import anthropic" 2>/dev/null || MISSING="$MISSING anthropic"
python3 -c "import Pillow" 2>/dev/null || MISSING="$MISSING Pillow"

if [ -n "$MISSING" ]; then
    echo "安装缺失依赖:$MISSING"
    pip3 install -r requirements.txt
fi

echo "启动 AI 桌面助手..."
python3 main.py
