"""AI 桌面应用 - 入口"""
import sys
import os

# 确保项目根目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_loader import ensure_dirs
from core.memory_manager import init_db


def main():
    """主入口"""
    # 初始化
    ensure_dirs()
    init_db()

    # 启动 GUI
    from app import App
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
