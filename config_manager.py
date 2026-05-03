import json
import sys
from pathlib import Path


def get_app_dir():
    """
    获取配置文件保存目录。
    开发环境：项目根目录
    打包环境：exe 所在目录
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


CONFIG_PATH = get_app_dir() / "config.json"


DEFAULT_CONFIG = {
    "pet": {
        "opacity": 1.0,
        "show_on_startup": True,
        "always_on_top": True,
        "x": None,
        "y": None
    }
}


def load_config():
    """
    读取配置文件。
    如果配置文件不存在，就返回默认配置。
    """
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            config = json.load(file)
    except Exception:
        return DEFAULT_CONFIG.copy()

    return merge_config(DEFAULT_CONFIG, config)


def save_config(config):
    """
    保存配置文件。
    """
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(CONFIG_PATH, "w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False, indent=4)


def merge_config(default_config, user_config):
    """
    合并默认配置和用户配置。
    防止以后新增配置项时旧 config.json 缺字段。
    """
    result = default_config.copy()

    for key, value in user_config.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = merge_config(result[key], value)
        else:
            result[key] = value

    return result


def get_pet_config():
    config = load_config()
    return config["pet"]


def update_pet_config(**kwargs):
    """
    更新宠物配置。

    用法：
        update_pet_config(opacity=0.8)
        update_pet_config(x=100, y=200)
    """
    config = load_config()

    for key, value in kwargs.items():
        config["pet"][key] = value

    save_config(config)