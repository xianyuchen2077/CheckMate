import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "CheckMate"

PROJECT_DIR = Path(__file__).resolve().parent
MAIN_FILE = PROJECT_DIR / "main.py"
ASSETS_DIR = PROJECT_DIR / "assets"
ICON_FILE = PROJECT_DIR / "assets" / "icons" / "checkmate_icon.ico"

# PyInstaller 临时构建目录
BUILD_DIR = PROJECT_DIR / "build"

# 最终发布目录，之后只运行这里面的 exe
RELEASE_DIR = PROJECT_DIR / "release"

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

        # 明确指定临时构建目录
        "--workpath",
        str(BUILD_DIR),

        # 明确指定最终输出目录
        "--distpath",
        str(RELEASE_DIR),
    ]

    if ICON_FILE.exists():
        command.extend(["--icon", str(ICON_FILE)])
        print(f"将使用程序图标：{ICON_FILE}")
    else:
        print("未找到 .ico 图标文件，跳过 exe 图标设置。")

    if ASSETS_DIR.exists():
        command.extend([
            "--add-data",
            f"{ASSETS_DIR};assets"
        ])
        print(f"将打包资源文件夹：{ASSETS_DIR}")
    else:
        print("未找到 assets 文件夹，跳过资源打包。")

    command.append(str(MAIN_FILE))

    run_command(command)


def check_build_result():
    exe_path = RELEASE_DIR / APP_NAME / f"{APP_NAME}.exe"

    # PyInstaller onedir 模式下，Python DLL 通常会在 _internal 目录中
    python_dll_candidates = list((RELEASE_DIR / APP_NAME).glob("_internal/python*.dll"))

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
    clean_old_build()
    build_exe()
    check_build_result()
    clean_temp_build_dir()


if __name__ == "__main__":
    main()