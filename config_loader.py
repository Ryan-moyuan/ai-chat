"""配置加载器"""
import json
import os
import sys

# PyInstaller 打包后使用 sys._MEIPASS 获取资源路径
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_PATH, "config.json")
LANG_DIR = os.path.join(BASE_PATH, "lang")
DATA_DIR = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "AI-Desktop-Assistant", "data")
IMAGES_DIR = os.path.join(DATA_DIR, "generated_images")
CHROMA_DIR = os.path.join(DATA_DIR, "chroma_db")


def load_config():
    """加载配置文件"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(config):
    """保存配置文件"""
    # 打包后不能写入 sys._MEIPASS，改写到用户目录
    if getattr(sys, 'frozen', False):
        user_config_path = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "AI-Desktop-Assistant", "config.json")
        os.makedirs(os.path.dirname(user_config_path), exist_ok=True)
        with open(user_config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    else:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)


def ensure_dirs():
    """确保数据目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    os.makedirs(CHROMA_DIR, exist_ok=True)
