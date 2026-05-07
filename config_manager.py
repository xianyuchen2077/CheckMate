import json
import shutil

from data_guard.paths import get_app_dir, get_user_data_root_dir


CONFIG_PATH = get_user_data_root_dir() / "config.json"
LEGACY_CONFIG_PATH = get_app_dir() / "config.json"


DEFAULT_CONFIG = {
    "general": {
        "show_main_window_on_startup": True,
        "minimize_to_tray_on_close": True,
        "confirm_before_exit": True,
        "show_tray_messages": True,
        "check_data_guard_on_startup": True,
        "refresh_tasks_on_startup": True,
    },
    "data_management": {
        "auto_backup_on_startup": True,
        "auto_backup_keep_count": 5,
    },
    "pet": {
        "visible": True,
        "opacity": 1.0,
        "show_on_startup": True,
        "always_on_top": True,
        "x": None,
        "y": None
    }
}


def migrate_legacy_config_if_needed():
    """
    如果 AppData 中还没有 config.json，
    但旧项目目录下存在 config.json，
    则复制旧配置到 AppData。
    """
    if CONFIG_PATH.exists():
        return False

    if not LEGACY_CONFIG_PATH.exists():
        return False

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(LEGACY_CONFIG_PATH, CONFIG_PATH)

    return True


def load_config():
    """
    读取配置文件。
    如果配置文件不存在，就返回默认配置。
    """
    migrate_legacy_config_if_needed()

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

def get_general_config():
    config = load_config()
    return config["general"]
def update_general_config(**kwargs):
    """
    更新常规配置。

    用法：
        update_general_config(show_main_window_on_startup=True)
        update_general_config(minimize_to_tray_on_close=True)
    """
    config = load_config()

    for key, value in kwargs.items():
        config["general"][key] = value

    save_config(config)

def get_data_management_config():
    """
    获取数据管理配置。
    """
    config = load_config()
    return config["data_management"]


def update_data_management_config(**kwargs):
    """
    更新数据管理配置。
    """
    config = load_config()

    for key, value in kwargs.items():
        config["data_management"][key] = value

    save_config(config)

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