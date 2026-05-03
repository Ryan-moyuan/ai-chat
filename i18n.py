"""国际化 - i18n 多语言支持"""
import json
import os
import sys

# 当前语言
_current_lang = "en"

# 所有翻译
_LANGS = {}

# PyInstaller 打包后使用 sys._MEIPASS 获取资源路径
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

LANG_DIR = os.path.join(BASE_PATH, "lang")


def load_language(lang_code):
    """加载语言文件"""
    lang_path = os.path.join(LANG_DIR, f"{lang_code}.json")
    if os.path.exists(lang_path):
        with open(lang_path, "r", encoding="utf-8") as f:
            return json.load(f)
    # 降级到英文
    if lang_code != "en":
        return load_language("en")
    return {}


def set_language(lang_code):
    """设置当前语言"""
    global _current_lang
    _current_lang = lang_code
    _LANGS[lang_code] = load_language(lang_code)


def get_language():
    """获取当前语言代码"""
    return _current_lang


def t(key, **kwargs):
    """翻译文本"""
    if _current_lang not in _LANGS:
        _LANGS[_current_lang] = load_language(_current_lang)

    text = _LANGS[_current_lang].get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text


def init():
    """初始化 - 确保默认语言加载"""
    if "en" not in _LANGS:
        _LANGS["en"] = load_language("en")
    if "zh" not in _LANGS:
        _LANGS["zh"] = load_language("zh")
    if "ja" not in _LANGS:
        _LANGS["ja"] = load_language("ja")
