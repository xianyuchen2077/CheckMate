import os
import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "CheckMate"

PROJECT_DIR = Path(__file__).resolve().parent
MAIN_FILE = PROJECT_DIR / "main.py"
ASSETS_DIR = PROJECT_DIR / "assets"

BUILD_DIR = PROJECT_DIR / "build"
DIST_DIR = PROJECT_DIR / "dist"
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

    for path in [BUILD_DIR, DIST_DIR, SPEC_FILE]:
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

        # 生成文件夹模式，比 onefile 更适合 PySide6 + 图片资源
        "--onedir",

        # GUI 程序，不显示黑色控制台窗口
        "--windowed",

        # exe 名称
        "--name",
        APP_NAME,

        # 每次覆盖旧 spec
        "--noconfirm",

        # 清理 PyInstaller 缓存
        "--clean",
    ]

    # 把 assets 文件夹打包进去
    # Windows 下 --add-data 使用 分号 ; 分隔 source 和 dest
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


def show_result():
    exe_path = DIST_DIR / APP_NAME / f"{APP_NAME}.exe"

    print("\n" + "=" * 60)

    if exe_path.exists():
        print("打包成功！")
        print(f"exe 位置：{exe_path}")
        print("\n你可以双击运行：")
        print(exe_path)
    else:
        print("打包命令已结束，但没有找到 exe。")
        print("请检查 dist 文件夹或上方日志。")

    print("=" * 60)


def main():
    print("=" * 60)
    print(f"开始打包 {APP_NAME}")
    print("=" * 60)

    check_main_file()
    ensure_pyinstaller()
    clean_old_build()
    build_exe()
    show_result()


if __name__ == "__main__":
    main()