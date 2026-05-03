# CheckMate / 不要成为咸鱼

> 一个带桌面宠物提醒的本地打卡督促小程序。  
> 目标很简单：别让今天又悄悄变成一条咸鱼。

CheckMate 是一个使用 **Python + PySide6 + SQLite** 开发的桌面端打卡工具。  
它支持任务管理、每日打卡、定时提醒、后台托盘运行和桌面宠物督促。

这个项目目前主要用于个人练手和持续迭代，目标是做成一个轻量、可爱、实用的桌面效率小工具。

---

## 项目特点

- 本地运行，无需登录
- 使用 SQLite 保存任务和打卡记录
- 支持每日打卡
- 支持任务提醒时间
- 支持任务暂停 / 启用
- 支持关闭窗口后继续在后台运行
- 支持系统托盘菜单
- 支持桌面宠物提醒
- 支持自定义宠物图片资源
- 后续计划支持开机自启动和自动打包发布

---

## 当前功能

### 任务管理

- 添加任务
- 编辑任务
- 删除任务
- 暂停 / 启用任务
- 设置任务提醒时间
- 支持不设置提醒时间的普通任务

### 打卡功能

- 每日任务打卡
- 今日完成统计
- 连续打卡天数统计
- 本月完成率统计
- 咸鱼值计算

### 提醒功能

- 到点弹出提醒
- 今日已完成的任务不会重复提醒
- 暂停任务不会触发提醒
- 没有设置提醒时间的任务不会触发提醒
- 支持后台托盘运行

### 桌面宠物

- 桌面浮窗显示
- 支持拖动
- 支持双击打开主窗口
- 支持右键菜单
- 支持不同状态图片
- 支持隐藏宠物后从托盘重新显示

---

## 技术栈

| 模块     | 技术                   |
| -------- | ---------------------- |
| 编程语言 | Python                 |
| GUI 框架 | PySide6                |
| 数据库   | SQLite                 |
| 定时提醒 | QTimer                 |
| 后台托盘 | QSystemTrayIcon        |
| 桌面宠物 | QWidget 无边框置顶窗口 |
| 打包工具 | PyInstaller            |

---

## 项目结构

```text
CheckMate/
├── main.py
├── main_window.py
├── add_task_dialog.py
├── reminder_manager.py
├── tray_manager.py
├── pet_window.py
├── database.py
├── styles.py
├── auto_start.py
├── build_exe.py
├── assets/
│   ├── pet_idle.png
│   ├── pet_remind.png
│   ├── pet_done.png
│   ├── pet_lazy.png
│   └── pet_sleep.png
├── data/
│   └── checkmate.db
└── README.md