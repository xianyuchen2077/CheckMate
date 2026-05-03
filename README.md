````markdown
# CheckMate / 不要成为咸鱼

> 一个带桌面宠物提醒的本地打卡督促小程序。  
> 今天也别悄悄变成咸鱼。

CheckMate 是一个使用 **Python + PySide6 + SQLite** 开发的 Windows 桌面端打卡工具。  
它支持任务管理、每日打卡、定时提醒、后台托盘运行、桌面宠物互动、自定义宠物图片、开机自启动和自动打包。

这个项目目前主要用于个人练手和持续迭代，目标是做成一个轻量、可爱、实用的桌面效率小工具。

---

## 项目定位

CheckMate 的核心定位是：

- 不是复杂的项目管理软件
- 不是团队协作工具
- 而是一个面向个人学习、习惯养成和日常任务督促的小工具

它希望解决的问题很简单：

> 到点提醒你该做事，别让任务被拖延悄悄吃掉。

---

## 当前功能

### 任务管理

- 添加任务
- 编辑任务
- 删除任务
- 暂停 / 启用任务
- 支持任务备注
- 支持设置提醒时间
- 支持不设置提醒时间的普通任务

### 打卡功能

- 每日任务打卡
- 今日完成统计
- 连续打卡天数统计
- 本月完成率统计
- 咸鱼值计算
- 历史打卡记录

### 提醒功能

- 到点弹出提醒窗口
- 今日已完成任务不会重复提醒
- 暂停任务不会触发提醒
- 没有设置提醒时间的任务不会触发提醒
- 支持稍后提醒
- 支持自定义稍后提醒时间
- 支持“今天不再提醒”

### 稍后提醒选项

点击提醒弹窗中的“稍后提醒”后，可以选择：

- 再给我5分钟~
- 向天再借600秒
- 先拖半小时
- 一个小时后之后再戳我
- 不干了！今天不干了！
- 说吧，你想拖多久

其中：

| 选项                 | 功能                               |
| -------------------- | ---------------------------------- |
| 再给我5分钟~         | 5 分钟后再次提醒                   |
| 向天再借600秒        | 10 分钟后再次提醒                  |
| 先拖半小时           | 30 分钟后再次提醒                  |
| 一个小时后之后再戳我 | 60 分钟后再次提醒                  |
| 不干了！今天不干了！ | 今天不再提醒该任务                 |
| 说吧，你想拖多久     | 打开时间选择器，自定义下次提醒时间 |

### 后台运行

- 关闭主窗口后程序不会退出
- 程序会缩到系统托盘
- 托盘菜单支持显示主窗口
- 托盘菜单支持显示桌面宠物
- 托盘菜单支持退出程序
- 支持开机自启动

### 桌面宠物

- 桌面浮窗显示
- 支持拖动
- 支持双击打开主窗口
- 支持右键菜单
- 支持隐藏 / 显示
- 支持回到右下角
- 支持显示今日进度
- 支持切换宠物角色
- 支持随机语录
- 支持单击切换语录
- 支持定时切换语录
- 支持 PNG 静态图片
- 支持 GIF 动画
- 支持根据咸鱼值切换状态

### 桌面宠物状态

当前支持以下状态资源：

| 状态     | 文件名                              |
| -------- | ----------------------------------- |
| 默认状态 | `pet_idle.png` / `pet_idle.gif`     |
| 提醒状态 | `pet_remind.png` / `pet_remind.gif` |
| 完成状态 | `pet_done.png` / `pet_done.gif`     |
| 拖延状态 | `pet_lazy.png` / `pet_lazy.gif`     |
| 休息状态 | `pet_sleep.png` / `pet_sleep.gif`   |

资源按角色分文件夹存放，例如：

```text
assets/
├── Morty/
│   ├── pet_idle.png
│   ├── pet_idle.gif
│   ├── pet_remind.png
│   ├── pet_remind.gif
│   ├── pet_done.png
│   ├── pet_done.gif
│   ├── pet_lazy.png
│   ├── pet_lazy.gif
│   ├── pet_sleep.png
│   └── pet_sleep.gif
└── Rick/
    ├── pet_idle.png
    ├── pet_idle.gif
    ├── pet_remind.png
    ├── pet_remind.gif
    ├── pet_done.png
    ├── pet_done.gif
    ├── pet_lazy.png
    ├── pet_lazy.gif
    ├── pet_sleep.png
    └── pet_sleep.gif
````

---

## 技术栈

| 模块       | 技术                   |
| ---------- | ---------------------- |
| 编程语言   | Python                 |
| GUI 框架   | PySide6                |
| 数据库     | SQLite                 |
| 定时器     | QTimer                 |
| 系统托盘   | QSystemTrayIcon        |
| 桌面宠物   | QWidget 无边框置顶窗口 |
| 图片显示   | QPixmap                |
| GIF 动画   | QMovie                 |
| 开机自启动 | Windows 注册表 Run 项  |
| 打包工具   | PyInstaller            |

---

## 推荐开发环境

推荐使用：

```text
Python 3.12
Windows 10 / Windows 11
PySide6
SQLite
PyInstaller
```

安装依赖：

```bash
pip install -r requirements.txt
```

如果还没有 `requirements.txt`，可以在虚拟环境中生成：

```bash
pip freeze > requirements.txt
```

---

## 运行方式

### 1. 创建虚拟环境

```bash
python -m venv .venv
```

### 2. 激活虚拟环境

Windows CMD：

```bash
.venv\Scripts\activate
```

PowerShell：

```powershell
.venv\Scripts\Activate.ps1
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行程序

```bash
python main.py
```

---

## 打包方式

项目提供了自动打包脚本：

```text
build_exe.py
```

运行：

```bash
python build_exe.py
```

打包完成后，程序会输出到：

```text
dist/CheckMate/CheckMate.exe
```

当前推荐使用 `--onedir` 模式打包，因为 PySide6 和图片 / GIF 资源较多，`onedir` 模式更稳定，也更方便排查资源路径问题。

---

## 项目结构

```text
CheckMate/
├── main.py
├── main_window.py
├── add_task_dialog.py
├── history_dialog.py
├── reminder_dialog.py
├── reminder_manager.py
├── tray_manager.py
├── pet_window.py
├── database.py
├── styles.py
├── auto_start.py
├── build_exe.py
├── requirements.txt
├── README.md
├── assets/
│   ├── background.png
│   ├── Morty/
│   │   ├── pet_idle.png
│   │   ├── pet_idle.gif
│   │   ├── pet_remind.png
│   │   ├── pet_remind.gif
│   │   ├── pet_done.png
│   │   ├── pet_done.gif
│   │   ├── pet_lazy.png
│   │   ├── pet_lazy.gif
│   │   ├── pet_sleep.png
│   │   └── pet_sleep.gif
│   └── Rick/
│       ├── pet_idle.png
│       ├── pet_idle.gif
│       ├── pet_remind.png
│       ├── pet_remind.gif
│       ├── pet_done.png
│       ├── pet_done.gif
│       ├── pet_lazy.png
│       ├── pet_lazy.gif
│       ├── pet_sleep.png
│       └── pet_sleep.gif
├── data/
│   └── checkmate.db
└── test/
    ├── test_reminder_dialog.py
    ├── test_snooze_dialog.py
    └── test_reminder_flow.py
```

---

## 文件说明

### `main.py`

程序入口文件。

主要职责：

* 创建 `QApplication`
* 设置全局字体
* 设置关闭最后一个窗口时不自动退出程序
* 创建并显示主窗口
* 启动 Qt 事件循环

`main.py` 只负责启动程序，不放具体业务逻辑。

---

### `main_window.py`

主窗口模块。

主要职责：

* 创建主界面
* 显示任务列表
* 显示打卡统计
* 显示任务详情
* 处理添加任务
* 处理编辑任务
* 处理删除任务
* 处理完成打卡
* 处理任务暂停 / 启用
* 初始化系统托盘
* 初始化桌面宠物
* 初始化提醒管理器
* 加载主窗口背景图片

主窗口是整个程序的核心界面，但不直接处理底层数据库 SQL，也不直接负责提醒弹窗 UI。

---

### `add_task_dialog.py`

添加 / 编辑任务弹窗模块。

主要职责：

* 输入任务名称
* 输入任务备注
* 可选设置提醒时间
* 返回任务数据给主窗口

它只负责输入界面，不直接写数据库。

---

### `history_dialog.py`

历史记录窗口模块。

主要职责：

* 显示最近若干天的打卡记录
* 显示每日任务完成情况
* 显示任务备注

历史记录数据由 `database.py` 提供。

---

### `reminder_dialog.py`

提醒弹窗 UI 模块。

主要职责：

* 显示主提醒弹窗 `ReminderDialog`
* 显示稍后提醒选项弹窗 `SnoozeDialog`
* 显示自定义稍后提醒时间弹窗 `CustomSnoozeTimeDialog`
* 管理提醒弹窗的样式
* 返回用户点击的结果

它只负责 UI，不负责业务逻辑。

也就是说：

```text
reminder_dialog.py 只管“弹窗长什么样，用户点了什么”
reminder_manager.py 才管“点完之后要做什么”
```

---

### `reminder_manager.py`

提醒业务管理模块。

主要职责：

* 使用 `QTimer` 定时检查任务
* 查询当前是否有到点且未完成的任务
* 调用 `ReminderDialog` 显示提醒
* 根据用户选择执行操作
* 完成打卡
* 打开主窗口
* 调用 `SnoozeDialog` 选择稍后提醒
* 安排下一次稍后提醒
* 处理“今天不再提醒”
* 通知桌面宠物切换状态
* 发送系统托盘通知

它不直接创建复杂 UI，复杂 UI 放在 `reminder_dialog.py`。

---

### `tray_manager.py`

系统托盘模块。

主要职责：

* 创建系统托盘图标
* 创建托盘右键菜单
* 显示主窗口
* 显示桌面宠物
* 开启 / 关闭开机自启动
* 退出程序
* 发送托盘通知

---

### `pet_window.py`

桌面宠物模块。

主要职责：

* 创建无边框、置顶、透明背景的宠物窗口
* 加载宠物图片和 GIF 动画
* 支持拖动
* 支持双击打开主窗口
* 支持右键菜单
* 支持切换 Rick / Morty 角色
* 支持隐藏宠物
* 支持宠物回到右下角
* 支持显示今日进度
* 支持随机语录
* 支持根据咸鱼值切换宠物状态

宠物图片资源默认从 `assets/<角色名>/` 中加载。

---

### `database.py`

数据库模块。

主要职责：

* 初始化 SQLite 数据库
* 创建任务表
* 创建打卡记录表
* 数据库字段迁移
* 添加任务
* 编辑任务
* 删除任务
* 暂停 / 启用任务
* 查询任务详情
* 查询今日任务状态
* 记录今日打卡
* 查询今日完成情况
* 查询连续打卡天数
* 查询本月完成率
* 查询历史记录
* 查询当前需要提醒的任务

数据库默认保存在：

```text
data/checkmate.db
```

打包为 exe 后，数据库会保存在 exe 同级目录下的：

```text
data/checkmate.db
```

---

### `styles.py`

样式模块。

主要职责：

* 存放主窗口 QSS 样式
* 存放添加任务弹窗 QSS 样式
* 支持主窗口背景图片
* 避免样式代码堆在主窗口逻辑中

---

### `auto_start.py`

开机自启动模块。

主要职责：

* 启用开机自启动
* 关闭开机自启动
* 检查当前是否已经设置开机自启动
* 生成开发环境和打包环境下不同的启动命令

Windows 下通过当前用户注册表 Run 项实现。

---

### `build_exe.py`

自动打包脚本。

主要职责：

* 检查 PyInstaller 是否安装
* 清理旧打包产物
* 打包主程序
* 将 `assets/` 资源文件夹一起打包
* 输出 Windows 可执行程序

运行：

```bash
python build_exe.py
```

---

### `test/`

测试脚本目录。

主要用于单独测试 UI 组件，而不用完整运行主程序。

当前建议包含：

```text
test/test_reminder_dialog.py
test/test_snooze_dialog.py
test/test_reminder_flow.py
```

说明：

| 文件                      | 用途                                       |
| ------------------------- | ------------------------------------------ |
| `test_reminder_dialog.py` | 单独测试主提醒弹窗                         |
| `test_snooze_dialog.py`   | 单独测试稍后提醒弹窗                       |
| `test_reminder_flow.py`   | 测试主提醒弹窗到稍后提醒弹窗的完整跳转流程 |

---

## 数据库设计

当前主要有两张表。

### `tasks`

任务表，用于保存长期存在的任务信息。

字段示意：

```text
id
title
description
remind_time
is_active
created_at
```

说明：

| 字段          | 含义             |
| ------------- | ---------------- |
| `id`          | 任务 ID          |
| `title`       | 任务名称         |
| `description` | 任务备注         |
| `remind_time` | 提醒时间，可为空 |
| `is_active`   | 是否启用         |
| `created_at`  | 创建时间         |

---

### `checkins`

打卡记录表，用于保存每日打卡记录。

字段示意：

```text
id
task_id
checkin_date
checkin_time
```

说明：

| 字段           | 含义         |
| -------------- | ------------ |
| `id`           | 打卡记录 ID  |
| `task_id`      | 对应任务 ID  |
| `checkin_date` | 打卡日期     |
| `checkin_time` | 具体打卡时间 |

同一个任务在同一天只能打卡一次。

---

## 程序运行流程

```text
main.py
  ↓
创建 QApplication
  ↓
创建 MainWindow
  ↓
初始化数据库
  ↓
加载任务列表
  ↓
初始化系统托盘
  ↓
初始化桌面宠物
  ↓
初始化提醒管理器
  ↓
进入 Qt 事件循环
```

---

## 关闭窗口后的行为

```text
点击主窗口关闭按钮
  ↓
触发 closeEvent
  ↓
主窗口隐藏
  ↓
程序继续在系统托盘运行
  ↓
到点仍会提醒
```

如果需要真正退出程序，需要通过系统托盘菜单点击：

```text
退出程序
```

---

## 提醒流程

```text
ReminderManager 定时检查
  ↓
database.get_due_tasks_now()
  ↓
发现到点且未完成任务
  ↓
显示托盘通知
  ↓
桌面宠物进入提醒状态
  ↓
弹出 ReminderDialog
  ↓
用户选择：
  ├── 完成打卡
  ├── 稍后提醒
  └── 打开主窗口
```

如果用户选择“稍后提醒”：

```text
ReminderDialog
  ↓
SnoozeDialog
  ↓
用户选择：
  ├── 5 分钟后
  ├── 10 分钟后
  ├── 30 分钟后
  ├── 60 分钟后
  ├── 今天不再提醒
  └── 自定义时间
```

---

## 资源路径说明

项目为了兼容源码运行和打包运行，资源路径需要同时支持：

```text
开发环境：
CheckMate/assets/

打包环境：
dist/CheckMate/assets/
```

因此代码中通常会判断：

```text
sys.frozen
```

如果是打包后的 exe，就从 exe 所在目录或 PyInstaller 临时目录查找资源；如果是源码运行，就从当前 `.py` 文件所在目录查找资源。

---

## Git 说明

不要上传 `.venv/`。

推荐 `.gitignore`：

```gitignore
.venv/
__pycache__/
*.pyc

build/
dist/
*.spec

data/*.db
data/*.db-journal

.DS_Store
Thumbs.db
```

应该上传：

```text
requirements.txt
README.md
源代码文件
assets 资源文件
```

不应该上传：

```text
.venv/
build/
dist/
data/checkmate.db
__pycache__/
```

---

## requirements.txt

`requirements.txt` 用来记录项目依赖。

生成方式：

```bash
pip freeze > requirements.txt
```

安装方式：

```bash
pip install -r requirements.txt
```

这样就不需要上传 `.venv/` 到 Git 仓库。

---

## 开发路线

### 已完成

* 基础主窗口
* 任务添加
* 任务编辑
* 任务删除
* 任务备注
* 任务暂停 / 启用
* 每日打卡
* SQLite 本地保存
* 今日统计
* 连续打卡统计
* 本月完成率统计
* 咸鱼值计算
* 历史记录窗口
* 主窗口任务详情面板
* 任务提醒时间
* 美化提醒弹窗
* 稍后提醒选项
* 自定义稍后提醒时间
* 系统托盘后台运行
* 开机自启动
* 桌面宠物浮窗
* 宠物图片 / GIF 加载
* 宠物右键菜单
* 宠物随机语录
* 宠物状态切换
* 主窗口背景图片
* 自动打包脚本

### 后续计划

* 更完整的设置页面
* 保存用户选择的宠物角色
* 保存宠物位置
* 保存窗口大小和位置
* 提醒音效
* 自定义提醒音效
* 任务分类 / 标签
* 任务优先级
* 更美观的历史记录页面
* 周报 / 月报统计
* 更完整的主题系统
* 应用图标
* 安装包制作
* 更完善的异常处理

---

## 可优化方向

### 1. 程序设置页面

可以新增一个设置窗口，用来管理：

* 是否开机自启动
* 默认宠物角色
* 默认稍后提醒时间
* 是否显示桌面宠物
* 提醒音效开关
* 背景图片选择
* 主题颜色选择

---

### 2. 宠物设置持久化

当前宠物角色、位置等信息可以进一步保存到配置文件中。

建议新增：

```text
config.json
```

保存内容：

```json
{
  "pet_skin": "Morty",
  "pet_x": 1200,
  "pet_y": 700,
  "show_pet": true,
  "auto_start": false
}
```

---

### 3. 提醒音效

可以在提醒弹窗出现时播放声音。

可选方案：

* 使用 `QSoundEffect`
* 使用 `winsound`
* 使用第三方音频库

---

### 4. 统计增强

可以继续增加：

* 最近 7 天完成率
* 最近 30 天完成率
* 单个任务完成趋势
* 最常拖延任务
* 最稳定任务
* 咸鱼值变化曲线

---

### 5. UI 美化

可以优化：

* 主窗口卡片布局
* 任务列表状态颜色
* 统计卡片样式
* 历史记录页面
* 提醒弹窗动画
* 统一图标系统
* 统一颜色主题

---

### 6. 打包发布

后续可以继续完善：

* 应用图标
* 版本号
* 自动清理旧版本
* 生成 zip 包
* 生成安装包
* 发布到 GitHub Releases

---

## 项目原则

1. 先完成功能闭环，再逐步美化 UI。
2. 每个文件只负责一类功能。
3. 数据库逻辑和界面逻辑分离。
4. 弹窗 UI 和提醒业务逻辑分离。
5. 桌面宠物作为增强体验，不影响核心打卡功能。
6. 本地优先，不依赖账号和云服务。
7. 保持项目轻量，适合作为桌面应用练手项目。

---

## 当前状态

CheckMate 目前已经可以作为一个本地打卡提醒工具使用。

它已经具备：

* 可用的任务系统
* 可用的每日打卡逻辑
* 可用的提醒系统
* 可用的桌面宠物
* 可用的后台托盘运行
* 初步的打包能力

后续重点可以放在：

1. 完善配置系统
2. 提升宠物互动体验
3. 优化 UI 视觉效果
4. 增强统计和复盘能力
5. 制作更正式的 Windows 发布版本

```
```
