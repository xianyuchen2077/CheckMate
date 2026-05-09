import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "CheckMate"

# 必须和 app_identity.py 里的 APP_USER_MODEL_ID 保持一致
APP_USER_MODEL_ID = "CheckMate"

PROJECT_DIR = Path(__file__).resolve().parent
MAIN_FILE = PROJECT_DIR / "main.py"

# 资源目录
ASSETS_DIR = PROJECT_DIR / "assets"
REMINDER_SOUNDS_DIR = ASSETS_DIR / "sounds" / "reminders"

# exe 程序图标
ICON_PNG_FILE = PROJECT_DIR / "assets" / "icons" / "checkmate_icon.png"
ICON_ICO_FILE = PROJECT_DIR / "assets" / "icons" / "checkmate_icon.ico"

# 快捷方式图标
SHORTCUT_ICON_PNG_FILE = PROJECT_DIR / "assets" / "icons" / "checkmate_shortcut_icon.png"
SHORTCUT_ICON_ICO_FILE = PROJECT_DIR / "assets" / "icons" / "checkmate_shortcut_icon.ico"

# PyInstaller 临时构建目录
BUILD_DIR = PROJECT_DIR / "build"

# 最终发布目录，之后只运行这里面的 exe
RELEASE_DIR = PROJECT_DIR / "release"

# release 快捷方式输出位置
SHORTCUT_FILE = RELEASE_DIR / f"{APP_NAME}.lnk"

# 开始菜单快捷方式位置
START_MENU_DIR = (
    Path.home()
    / "AppData"
    / "Roaming"
    / "Microsoft"
    / "Windows"
    / "Start Menu"
    / "Programs"
)

START_MENU_SHORTCUT_FILE = START_MENU_DIR / f"{APP_NAME}.lnk"

# PyInstaller 默认会生成 spec 文件
SPEC_FILE = PROJECT_DIR / f"{APP_NAME}.spec"


def run_command(command):
    print("\n执行命令：")
    print(" ".join(command))
    print("-" * 60)

    result = subprocess.run(command, cwd=PROJECT_DIR)

    if result.returncode != 0:
        raise RuntimeError("命令执行失败，请查看上方错误信息。")


def check_main_file():
    if not MAIN_FILE.exists():
        raise FileNotFoundError(f"找不到入口文件：{MAIN_FILE}")


def ensure_pyinstaller():
    try:
        subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        print("PyInstaller 已安装。")
    except Exception:
        print("未检测到 PyInstaller，正在安装...")
        run_command([sys.executable, "-m", "pip", "install", "-U", "pyinstaller"])


def ensure_pywin32():
    """
    确保 pywin32 可用，用于创建 Windows 快捷方式和写入 AppUserModelID。
    """
    try:
        import win32com.client  # noqa: F401
        print("pywin32 已安装。")
    except ImportError:
        print("未检测到 pywin32，正在安装...")
        run_command([sys.executable, "-m", "pip", "install", "pywin32"])


def ensure_ico_file(png_file, ico_file, label="图标"):
    """
    确保存在可用的 .ico 图标。

    如果 ico 已存在，则直接使用。
    如果 ico 不存在，但 png 存在，则自动从 png 生成 ico。
    """
    if ico_file.exists():
        print(f"已找到 {label} ico 图标：{ico_file}")
        return True

    if not png_file.exists():
        print(f"未找到 {label} PNG 图标，也未找到 ICO 图标：{png_file}")
        return False

    try:
        from PIL import Image
    except ImportError:
        print("未检测到 Pillow，正在安装...")
        run_command([sys.executable, "-m", "pip", "install", "pillow"])
        from PIL import Image

    ico_file.parent.mkdir(parents=True, exist_ok=True)

    image = Image.open(png_file).convert("RGBA")

    image.save(
        ico_file,
        format="ICO",
        sizes=[
            (16, 16),
            (24, 24),
            (32, 32),
            (48, 48),
            (64, 64),
            (128, 128),
            (256, 256),
        ]
    )

    print(f"已根据 PNG 生成 {label} ico 图标：{ico_file}")
    return True


def ensure_icon_files():
    """
    确保 exe 图标和快捷方式图标都存在。
    """
    ensure_ico_file(
        ICON_PNG_FILE,
        ICON_ICO_FILE,
        label="exe"
    )

    ensure_ico_file(
        SHORTCUT_ICON_PNG_FILE,
        SHORTCUT_ICON_ICO_FILE,
        label="快捷方式"
    )


def ensure_sound_dirs():
    """
    确保提醒音效目录存在。

    即使当前没有音频文件，也保留这个目录结构，
    方便后续往 assets/sounds/reminders/ 中添加音效。
    """
    REMINDER_SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"提醒音效目录检查通过：{REMINDER_SOUNDS_DIR}")


def clean_old_build():
    print("\n清理旧打包文件...")

    for path in [BUILD_DIR, RELEASE_DIR, SPEC_FILE]:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
                print(f"已删除文件夹：{path}")
            else:
                path.unlink()
                print(f"已删除文件：{path}")


def build_exe():
    command = [
        sys.executable,
        "-m",
        "PyInstaller",

        # 文件夹模式，适合 PySide6 项目
        "--onedir",

        # GUI 程序，不弹出黑色控制台
        "--windowed",

        # 应用名称
        "--name",
        APP_NAME,

        # 覆盖旧文件
        "--noconfirm",

        # 清理 PyInstaller 缓存
        "--clean",

        # PySide6 多媒体模块：提醒音效需要 QMediaPlayer / QAudioOutput
        "--hidden-import",
        "PySide6.QtMultimedia",

        "--hidden-import",
        "PySide6.QtMultimediaWidgets",

        "--collect-submodules",
        "PySide6.QtMultimedia",

        "--collect-data",
        "PySide6.QtMultimedia",

        # 明确指定临时构建目录
        "--workpath",
        str(BUILD_DIR),

        # 明确指定最终输出目录
        "--distpath",
        str(RELEASE_DIR),
    ]

    if ICON_ICO_FILE.exists():
        command.extend(["--icon", str(ICON_ICO_FILE)])
        print(f"将使用程序图标：{ICON_ICO_FILE}")
    else:
        print("未找到 .ico 图标文件，跳过 exe 图标设置。")

    if ASSETS_DIR.exists():
        # 注意：
        # 这里打包整个 assets 文件夹。
        # assets/sounds/reminders/ 会随 assets 一起进入 release。
        command.extend([
            "--add-data",
            f"{ASSETS_DIR};assets"
        ])
        print(f"将打包资源文件夹：{ASSETS_DIR}")
    else:
        print("未找到 assets 文件夹，跳过资源打包。")

    command.append(str(MAIN_FILE))

    run_command(command)


def get_release_app_dir():
    """
    获取 onedir 模式下的应用输出目录。
    """
    return RELEASE_DIR / APP_NAME


def get_release_exe_path():
    """
    获取 release 中的 exe 路径。
    """
    return get_release_app_dir() / f"{APP_NAME}.exe"


def find_release_assets_dir():
    """
    查找 release 中的 assets 目录。

    PyInstaller onedir 模式下，不同版本可能放在：
        release/CheckMate/_internal/assets
    或：
        release/CheckMate/assets
    """
    release_app_dir = get_release_app_dir()

    possible_assets_dirs = [
        release_app_dir / "_internal" / "assets",
        release_app_dir / "assets",
    ]

    for assets_dir in possible_assets_dirs:
        if assets_dir.exists():
            return assets_dir

    return None


def check_build_result():
    exe_path = get_release_exe_path()

    # PyInstaller onedir 模式下，Python DLL 通常会在 _internal 目录中
    python_dll_candidates = list(get_release_app_dir().glob("_internal/python*.dll"))

    print("\n" + "=" * 60)

    if not exe_path.exists():
        print("打包命令已结束，但没有找到 exe。")
        print("请检查 release 文件夹或上方日志。")
        print("=" * 60)
        return

    print("打包成功！")
    print(f"exe 位置：{exe_path}")

    if python_dll_candidates:
        print("Python DLL 检查通过：")
        for dll in python_dll_candidates:
            print(f"  {dll}")
    else:
        print("警告：没有在 _internal 中找到 python*.dll。")
        print("如果运行 exe 报 Failed to load Python DLL，请重新打包或检查杀毒软件是否隔离了文件。")

    print("\n请运行这个文件：")
    print(exe_path)
    print("\n不要运行 build 文件夹里的任何 exe。")
    print("=" * 60)


def check_assets_result():
    """
    检查 release 中是否包含 assets 和提醒音效目录。
    """
    print("\n资源文件检查：")

    assets_dir = find_release_assets_dir()

    if assets_dir is None:
        print("警告：release 中没有找到 assets 文件夹。")
        print("请检查 PyInstaller 的 --add-data 参数。")
        return

    print(f"assets 已打包：{assets_dir}")

    icons_dir = assets_dir / "icons"

    if icons_dir.exists():
        print(f"图标目录已打包：{icons_dir}")

        expected_icons = [
            "checkmate_icon.png",
            "checkmate_icon.ico",
            "checkmate_shortcut_icon.png",
            "checkmate_shortcut_icon.ico",
            "notify_reminder.png",
            "notify_done.png",
            "notify_snooze.png",
            "notify_warning.png",
            "notify_success.png",
        ]

        for icon_name in expected_icons:
            icon_path = icons_dir / icon_name

            if icon_path.exists():
                print(f"  √ {icon_name}")
            else:
                print(f"  × 缺少 {icon_name}")
    else:
        print("警告：release 中没有找到 assets/icons。")

    sound_dir = assets_dir / "sounds" / "reminders"

    if not sound_dir.exists():
        print("警告：release 中没有找到 assets/sounds/reminders。")
        print("如果你使用提醒音效下拉框，release 中可能无法读取音频文件。")
        return

    print(f"提醒音效目录已打包：{sound_dir}")

    sound_files = [
        path.name
        for path in sound_dir.iterdir()
        if path.is_file()
    ]

    if not sound_files:
        print("提醒音效目录存在，但当前没有音频文件。")
        return

    print("已包含提醒音效：")
    for file_name in sorted(sound_files, key=str.lower):
        print(f"  - {file_name}")


def set_shortcut_app_user_model_id(shortcut_path):
    """
    给 Windows 快捷方式写入 AppUserModelID。

    作用：
        1. 让 Windows 通知系统能把通知归类到 CheckMate。
        2. 避免通知顶部显示 NotifyIconGeneratedAumid_xxx。
        3. 有助于通知顶部小图标识别。
    """
    if not shortcut_path.exists():
        print(f"快捷方式不存在，无法写入 AppUserModelID：{shortcut_path}")
        return

    try:
        import pythoncom
        from win32com.propsys import propsys, pscon

        stgm_readwrite = getattr(pythoncom, "STGM_READWRITE", 0x00000002)

        property_store = propsys.SHGetPropertyStoreFromParsingName(
            str(shortcut_path),
            None,
            stgm_readwrite,
            propsys.IID_IPropertyStore
        )

        try:
            value = propsys.PROPVARIANTType(
                APP_USER_MODEL_ID,
                pythoncom.VT_LPWSTR
            )
        except TypeError:
            value = propsys.PROPVARIANTType(APP_USER_MODEL_ID)

        property_store.SetValue(pscon.PKEY_AppUserModel_ID, value)
        property_store.Commit()

        print(f"已写入 AppUserModelID：{APP_USER_MODEL_ID}")
        print(f"目标快捷方式：{shortcut_path}")

    except Exception as e:
        print("警告：写入 AppUserModelID 失败。")
        print(f"快捷方式：{shortcut_path}")
        print(f"错误信息：{e}")


def create_shortcut(shortcut_file, label):
    """
    创建一个指向 release/CheckMate/CheckMate.exe 的快捷方式。

    快捷方式图标优先使用 exe 内嵌图标：
        IconLocation = release/CheckMate/CheckMate.exe,0

    这样发布时不依赖开发目录下的 ico 文件。
    """
    exe_path = get_release_exe_path()

    if not exe_path.exists():
        print(f"\n未找到 exe，无法创建{label}快捷方式：")
        print(exe_path)
        return

    try:
        import win32com.client
    except ImportError:
        print("\n未安装 pywin32，无法创建快捷方式。")
        print("请先运行：pip install pywin32")
        return

    shortcut_file.parent.mkdir(parents=True, exist_ok=True)

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortcut(str(shortcut_file))

    shortcut.TargetPath = str(exe_path)
    shortcut.WorkingDirectory = str(exe_path.parent)
    shortcut.Description = "CheckMate - 不要成为咸鱼"

    # 快捷方式优先使用专用 shortcut 图标
    if SHORTCUT_ICON_ICO_FILE.exists():
        shortcut.IconLocation = str(SHORTCUT_ICON_ICO_FILE)
        print(f"{label}快捷方式将使用专用图标：{SHORTCUT_ICON_ICO_FILE}")
    elif ICON_ICO_FILE.exists():
        shortcut.IconLocation = str(ICON_ICO_FILE)
        print(f"{label}快捷方式未找到专用图标，回退使用 exe 图标文件：{ICON_ICO_FILE}")
    else:
        shortcut.IconLocation = f"{exe_path},0"
        print(f"{label}快捷方式未找到 ico 文件，回退使用 exe 内嵌图标。")

    shortcut.Save()

    print(f"\n已创建{label}快捷方式：")
    print(shortcut_file)

    set_shortcut_app_user_model_id(shortcut_file)


def create_release_shortcut():
    """
    在 release 目录下创建 CheckMate 快捷方式。

    快捷方式位置：
        release/CheckMate.lnk

    指向：
        release/CheckMate/CheckMate.exe
    """
    create_shortcut(
        SHORTCUT_FILE,
        label="release"
    )


def create_start_menu_shortcut():
    """
    在当前用户开始菜单中创建 CheckMate 快捷方式。

    这个快捷方式对 Windows 通通知别 AppUserModelID 很重要。
    """
    create_shortcut(
        START_MENU_SHORTCUT_FILE,
        label="开始菜单"
    )


def clean_temp_build_dir():
    """
    删除 PyInstaller 临时 build 目录，避免误运行 build 里的文件。
    """
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
        print(f"\n已删除临时构建目录：{BUILD_DIR}")


def main():
    print("=" * 60)
    print(f"开始打包 {APP_NAME}")
    print("=" * 60)

    check_main_file()
    ensure_pyinstaller()
    ensure_pywin32()
    ensure_icon_files()
    ensure_sound_dirs()

    clean_old_build()
    build_exe()
    check_build_result()
    check_assets_result()
    create_release_shortcut()
    create_start_menu_shortcut()
    clean_temp_build_dir()


if __name__ == "__main__":
    main()