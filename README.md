# CheckMate / 不要成为咸鱼

> 一个带桌面宠物、任务提醒、重复提醒、宠物养成和数据安全保护的本地打卡督促小程序。  
> 今天也别悄悄变成咸鱼。

CheckMate 是一个使用 **Python + PySide6 + SQLite** 开发的 Windows 桌面端效率工具。

它的核心目标是：

- 管理每日任务和长期习惯
- 到点提醒用户完成任务
- 关闭主窗口后仍在后台运行
- 通过桌面宠物进行陪伴和督促
- 完成任务后获得宠物经验
- 通过升级、进化、历史记录和统计反馈形成正向激励
- 尽量保护本地数据不因更新、误删、覆盖或异常修改而丢失

---

## 项目定位

CheckMate 不是复杂的项目管理软件，也不是团队协作工具。

它更像是一个个人桌面陪伴型打卡工具：

- 到点提醒你该做事
- 完成任务后给宠物加经验
- 宠物会升级、进化
- 桌面宠物会通过状态和语录督促你
- 关闭窗口后仍能在系统托盘后台运行
- 用户数据保存在本地，不依赖账号和云服务

一句话：

> 你完成任务，宠物成长；你一直拖延，宠物陪你变咸。

---

## 当前功能概览

### 任务与习惯管理

CheckMate 当前支持两类事项：

| 类型 | 说明                                                               |
| ---- | ------------------------------------------------------------------ |
| 任务 | 一次性任务，只在创建当天显示；第二天自动归档，不再出现在今日任务中 |
| 习惯 | 长期习惯，每天保留，继续显示、提醒和统计                           |

当前支持：

- 添加任务 / 习惯
- 编辑任务 / 习惯
- 删除任务 / 习惯
- 任务备注
- 暂停 / 启用
- 可选提醒时间
- 可选重复提醒间隔
- 任务 / 习惯类型切换
- 今日任务列表显示类型图标
  - `📝` 一次性任务
  - `🌱` 长期习惯

---

### 每日打卡

- 每日任务打卡
- 今日完成统计
- 连续打卡天数统计
- 本月完成率统计
- 咸鱼值计算
- 历史打卡记录
- 任务详情面板
- 普通任务今日完成后不会重复打卡
- 重复提醒任务可以完成多轮

---

### 提醒功能

- 到点弹出提醒窗口
- 暂停任务不会触发提醒
- 未设置提醒时间的任务不会触发提醒
- 今日已完成的普通任务不会重复提醒
- 重复提醒任务不会因为今日已完成而停止后续提醒
- 支持稍后提醒
- 支持自定义稍后提醒时间
- 支持“今天不再提醒”
- 支持重复提醒任务继续安排下一轮提醒

---

### 重复提醒

任务或习惯可以设置重复提醒间隔。

例如：

- 每隔 5 分钟
- 每隔 10 分钟
- 每隔 30 分钟
- 每隔 1 小时
- 自定义分钟数

重复提醒任务的特点：

```text
到点提醒
↓
用户完成本轮
↓
宠物获得经验
↓
继续安排下一轮提醒
```

重复提醒任务不会因为当天已经打卡而停止后续提醒。

---

### 稍后提醒选项

点击提醒弹窗中的“稍后提醒”后，可以选择：

| 选项                 | 功能                               |
| -------------------- | ---------------------------------- |
| 再给我5分钟~         | 5 分钟后再次提醒                   |
| 向天再借600秒        | 10 分钟后再次提醒                  |
| 先拖半小时           | 30 分钟后再次提醒                  |
| 一个小时后之后再戳我 | 60 分钟后再次提醒                  |
| 不干了！今天不干了！ | 今天不再提醒该任务                 |
| 说吧，你想拖多久     | 打开时间选择器，自定义下次提醒时间 |

---

### 后台运行

- 关闭主窗口后程序不会退出
- 程序会缩到系统托盘
- 到点仍会提醒
- 托盘菜单支持显示主窗口
- 托盘菜单支持显示桌面宠物
- 托盘菜单支持退出程序
- 支持开机自启动

---

### 桌面宠物

- 桌面浮窗显示
- 支持拖动
- 支持双击打开主窗口
- 支持右键菜单
- 支持隐藏 / 显示
- 支持回到右下角
- 支持显示今日进度
- 支持随机语录
- 支持定时切换语录
- 支持 PNG 静态图片
- 支持 GIF 动画
- 支持不同状态切换图片
- 支持宠物等级、阶段、经验条显示
- 支持宠物窗口透明度设置
- 支持宠物窗口置顶设置
- 支持保存宠物当前位置

---

### 宠物养成系统

- 默认宠物：咸鱼仔
- 默认皮肤：`salty_fish`
- 完成任务后获得经验
- 经验满后自动升级
- 等级达到条件后自动进化
- 进化后可加载不同阶段的宠物资源
- 升级 / 进化时弹出成长提示窗口
- 宠物窗口显示等级、名字、阶段、经验条和经验数值

---

## 宠物成长规则

### 经验获取

当前经验奖励规则：

| 行为                 |      EXP |
| -------------------- | -------: |
| 完成普通任务         |      +10 |
| 完成带提醒时间的任务 |      +15 |
| 有连续打卡记录       |  额外 +5 |
| 完成当天全部任务     | 额外 +20 |

具体经验计算逻辑位于：

```text
pet_system/pet_growth.py
```

---

### 升级规则

当前升级所需经验：

```text
升级所需 EXP = 100 + 当前等级 × 20
```

示例：

| 当前等级 | 升下一级需要 |
| -------- | -----------: |
| Lv.1     |      120 EXP |
| Lv.2     |      140 EXP |
| Lv.3     |      160 EXP |
| Lv.4     |      180 EXP |
| Lv.5     |      200 EXP |

---

### 进化阶段

| 阶段    |      等级范围 | 阶段名         |
| ------- | ------------: | -------------- |
| Stage 1 |   Lv.1 - Lv.4 | 咸鱼苗         |
| Stage 2 |   Lv.5 - Lv.9 | 努力鱼         |
| Stage 3 | Lv.10 - Lv.19 | 自律鱼         |
| Stage 4 |        Lv.20+ | 时间管理大师鱼 |

---

## 宠物资源结构

当前宠物资源放在：

```text
assets/
└── pets/
    └── salty_fish/
        ├── stage_1/
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
        ├── stage_2/
        ├── stage_3/
        └── stage_4/
```

---

### 宠物状态文件命名

| 文件名                              | 用途                |
| ----------------------------------- | ------------------- |
| `pet_idle.png` / `pet_idle.gif`     | 默认状态            |
| `pet_remind.png` / `pet_remind.gif` | 提醒状态            |
| `pet_done.png` / `pet_done.gif`     | 完成任务状态        |
| `pet_lazy.png` / `pet_lazy.gif`     | 拖延 / 稍后提醒状态 |
| `pet_sleep.png` / `pet_sleep.gif`   | 休息状态            |

---

### 加载规则

程序会按照以下顺序查找资源：

```text
当前 stage 的 gif
当前 stage 的 png
stage_1 的 gif
stage_1 的 png
皮肤根目录的 gif
皮肤根目录的 png
```

例如当前宠物为 `salty_fish`，当前阶段为 `stage_2`，状态为 `done` 时，会依次查找：

```text
assets/pets/salty_fish/stage_2/pet_done.gif
assets/pets/salty_fish/stage_2/pet_done.png
assets/pets/salty_fish/stage_1/pet_done.gif
assets/pets/salty_fish/stage_1/pet_done.png
assets/pets/salty_fish/pet_done.gif
assets/pets/salty_fish/pet_done.png
```

如果都找不到，则显示默认 emoji：

```text
🐟
```

---

## 应用图标资源

应用图标建议放在：

```text
assets/
└── icons/
    ├── checkmate_icon.png
    └── checkmate_icon.ico
```

| 文件                 | 用途                             |
| -------------------- | -------------------------------- |
| `checkmate_icon.png` | 开发环境下用于窗口图标、托盘图标 |
| `checkmate_icon.ico` | 打包 exe 时用于程序图标          |

---

## 背景图片资源

### 主窗口背景

推荐路径：

```text
assets/backgrounds/main_bg.png
```

如果背景图片不存在，程序会使用默认浅色背景。

---

### 添加任务弹窗背景

推荐路径：

```text
assets/backgrounds/add_task_bg.png
```

如果添加任务弹窗背景图片不存在，程序会自动使用浅灰色背景作为兜底。

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
| 静态图片   | QPixmap                |
| GIF 动画   | QMovie                 |
| 进度条     | QProgressBar           |
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

```bat
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

项目提供自动打包脚本：

```text
build_exe.py
```

运行：

```bash
python build_exe.py
```

打包结果默认输出到：

```text
dist/CheckMate/CheckMate.exe
```

当前推荐使用 `--onedir` 模式，因为 PySide6 和图片 / GIF 资源较多，`onedir` 模式更稳定，也更方便排查资源路径问题。

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
├── repeat_reminder_widget.py
├── pet_growth_dialog.py
├── pet_settings_dialog.py
├── tray_manager.py
├── pet_window.py
├── database.py
├── config_manager.py
├── styles.py
├── auto_start.py
├── build_exe.py
├── requirements.txt
├── README.md
├── pet_system/
│   ├── __init__.py
│   └── pet_growth.py
├── data_guard/
│   ├── __init__.py
│   ├── paths.py
│   ├── backup_manager.py
│   ├── integrity_manager.py
│   ├── migration_manager.py
│   ├── startup_guard.py
│   ├── logger.py
│   └── README.md
├── assets/
│   ├── backgrounds/
│   │   ├── main_bg.png
│   │   └── add_task_bg.png
│   ├── icons/
│   │   ├── checkmate_icon.png
│   │   └── checkmate_icon.ico
│   └── pets/
│       └── salty_fish/
│           ├── stage_1/
│           ├── stage_2/
│           ├── stage_3/
│           └── stage_4/
└── test/
    ├── README.md
    ├── test_tamper_db.py
    ├── test_restore_latest_backup.py
    └── test_trust_current_database.py
```

---

## 文件说明

### `main.py`

程序入口文件。

主要职责：

- 创建 `QApplication`
- 设置全局字体
- 设置应用图标
- 设置关闭最后一个窗口时不自动退出程序
- 创建并显示主窗口
- 启动 Qt 事件循环

---

### `main_window.py`

主窗口模块。

主要职责：

- 创建主界面
- 显示任务列表
- 显示打卡统计
- 显示任务详情
- 处理添加任务
- 处理编辑任务
- 处理删除任务
- 处理完成打卡
- 处理任务暂停 / 启用
- 初始化系统托盘
- 初始化桌面宠物
- 初始化提醒管理器
- 加载主窗口背景图片
- 完成任务后触发宠物经验增长
- 启动时调用数据迁移、数据归档和数据安全检查

---

### `add_task_dialog.py`

添加 / 编辑任务弹窗模块。

主要职责：

- 输入任务名称
- 输入任务备注
- 可选设置提醒时间
- 可选设置重复提醒
- 支持任务 / 习惯切换
- 支持背景图片
- 背景图片不存在时使用浅灰色背景兜底
- 返回任务数据给主窗口

返回数据结构：

```python
title, remind_time, description, repeat_interval_minutes, task_type
```

其中：

```text
task_type = "task"   # 一次性任务
task_type = "habit"  # 长期习惯
```

---

### `repeat_reminder_widget.py`

重复提醒设置组件。

主要职责：

- 控制是否启用重复提醒
- 选择预设重复间隔
- 支持自定义重复间隔
- 根据是否设置提醒时间启用 / 禁用重复提醒设置

---

### `history_dialog.py`

历史记录窗口模块。

主要职责：

- 显示最近若干天的打卡记录
- 显示每日任务完成情况
- 显示任务备注
- 支持查看已归档的一次性任务在创建当天的完成情况

---

### `reminder_dialog.py`

提醒弹窗 UI 模块。

主要职责：

- 显示主提醒弹窗 `ReminderDialog`
- 显示稍后提醒选项弹窗 `SnoozeDialog`
- 显示自定义稍后提醒时间弹窗 `CustomSnoozeTimeDialog`
- 管理提醒弹窗样式
- 返回用户点击结果

它只负责 UI，不负责业务逻辑。

---

### `reminder_manager.py`

提醒业务管理模块。

主要职责：

- 使用 `QTimer` 定时检查任务
- 查询当前是否有到点且未完成的任务
- 调用 `ReminderDialog` 显示提醒
- 根据用户选择执行操作
- 完成打卡
- 打开主窗口
- 调用 `SnoozeDialog` 选择稍后提醒
- 安排下一次稍后提醒
- 处理“今天不再提醒”
- 处理重复提醒任务的下一轮提醒
- 通知桌面宠物切换状态
- 发送系统托盘通知
- 提醒弹窗完成任务后触发宠物经验增长

---

### `pet_growth_dialog.py`

宠物成长提示弹窗。

主要职责：

- 显示获得经验
- 显示升级结果
- 显示进化结果
- 显示等级变化
- 显示阶段变化

普通加经验时可以只更新主界面提示。  
升级或进化时弹出该窗口。

---

### `pet_settings_dialog.py`

宠物设置弹窗。

主要职责：

- 调整宠物窗口透明度
- 设置启动时是否显示宠物
- 设置宠物窗口是否始终置顶
- 保存宠物当前位置
- 让宠物回到右下角
- 恢复宠物默认设置

---

### `tray_manager.py`

系统托盘模块。

主要职责：

- 创建系统托盘图标
- 创建托盘右键菜单
- 显示主窗口
- 显示桌面宠物
- 开启 / 关闭开机自启动
- 退出程序
- 发送托盘通知

---

### `pet_window.py`

桌面宠物模块。

主要职责：

- 创建无边框、置顶、透明背景的宠物窗口
- 加载宠物图片和 GIF 动画
- 支持拖动
- 支持双击打开主窗口
- 支持右键菜单
- 支持隐藏宠物
- 支持宠物回到右下角
- 支持宠物设置窗口
- 支持显示今日进度
- 支持随机语录
- 支持根据咸鱼值切换宠物状态
- 显示宠物等级、名字、阶段、经验条和经验数值
- 根据数据库中的 `stage` 自动加载不同阶段的宠物资源

---

### `pet_system/pet_growth.py`

宠物养成核心逻辑模块。

主要职责：

- 定义默认宠物皮肤
- 定义默认宠物名字
- 计算升级所需经验
- 根据等级计算进化阶段
- 获取阶段名称
- 计算任务完成奖励经验
- 给宠物增加经验
- 自动升级
- 自动进化
- 构造成长结果信息

---

### `database.py`

数据库模块。

主要职责：

- 初始化 SQLite 数据库
- 创建任务表
- 创建打卡记录表
- 创建宠物状态表
- 数据库字段迁移
- 添加任务
- 编辑任务
- 删除任务
- 暂停 / 启用任务
- 查询任务详情
- 查询今日任务状态
- 记录今日打卡
- 查询今日完成情况
- 查询连续打卡天数
- 查询本月完成率
- 查询历史记录
- 查询当前需要提醒的任务
- 获取宠物状态
- 保存宠物状态
- 归档过期一次性任务

---

### `data_guard/`

数据安全模块。

主要职责：

- 统一管理数据路径
- 将数据库迁移到 AppData 用户数据目录
- 启动时自动备份数据库
- 计算并保存数据库完整性校验
- 检测数据库是否被外部修改
- 检测到可疑数据库时生成 suspicious 备份
- 从最近自动备份恢复数据库
- 强制信任当前数据库
- 清理特殊备份
- 记录数据安全日志

---

### `config_manager.py`

配置管理模块。

主要职责：

- 读取配置文件
- 保存配置文件
- 管理宠物显示配置
- 管理宠物窗口位置
- 管理宠物透明度
- 管理宠物是否置顶
- 管理宠物是否启动时显示

---

### `styles.py`

样式模块。

主要职责：

- 存放主窗口 QSS 样式
- 存放添加任务弹窗 QSS 样式
- 存放重复提醒组件 QSS 样式
- 支持主窗口背景图片
- 支持添加任务弹窗背景图片
- 集中管理文字颜色、输入框颜色、按钮颜色

---

### `auto_start.py`

开机自启动模块。

主要职责：

- 启用开机自启动
- 关闭开机自启动
- 检查当前是否已经设置开机自启动
- 生成开发环境和打包环境下不同的启动命令

Windows 下通过当前用户注册表 Run 项实现。

---

### `build_exe.py`

自动打包脚本。

主要职责：

- 检查 PyInstaller 是否安装
- 清理旧打包产物
- 打包主程序
- 将 `assets/` 资源文件夹一起打包
- 指定应用图标
- 输出 Windows 可执行程序

---

## 数据存储位置

CheckMate 的用户数据不会直接保存在程序目录中，而是保存在当前用户的本地应用数据目录。

Windows 下默认路径：

```text
%LOCALAPPDATA%\CheckMate\
```

实际示例：

```text
C:\Users\用户名\AppData\Local\CheckMate\
```

目录结构：

```text
%LOCALAPPDATA%\CheckMate\
├── data/
│   └── checkmate.db
├── data_backups/
│   ├── auto_checkmate_xxx.db
│   ├── suspicious_checkmate_xxx.db
│   ├── before_restore_checkmate_xxx.db
│   ├── integrity.json
│   └── migration_done.txt
├── logs/
│   └── data_guard.log
└── config.json
```

这样即使用户更新、删除或替换程序目录，任务、习惯、打卡记录和宠物进度也不会被一起删除。

---

## 数据库设计

当前主要包含三类表：

```text
tasks
checkins
pet_status
```

---

### `tasks`

任务表，用于保存任务和习惯信息。

字段示意：

```text
id
title
description
remind_time
repeat_interval_minutes
task_type
is_archived
is_active
created_at
```

| 字段                      | 含义                                              |
| ------------------------- | ------------------------------------------------- |
| `id`                      | 任务 ID                                           |
| `title`                   | 任务名称                                          |
| `description`             | 任务备注                                          |
| `remind_time`             | 提醒时间，可为空                                  |
| `repeat_interval_minutes` | 重复提醒间隔，可为空                              |
| `task_type`               | 类型，`task` 表示一次性任务，`habit` 表示长期习惯 |
| `is_archived`             | 是否归档，0 表示未归档，1 表示已归档              |
| `is_active`               | 是否启用                                          |
| `created_at`              | 创建时间                                          |

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

| 字段           | 含义         |
| -------------- | ------------ |
| `id`           | 打卡记录 ID  |
| `task_id`      | 对应任务 ID  |
| `checkin_date` | 打卡日期     |
| `checkin_time` | 具体打卡时间 |

同一个普通任务在同一天只能打卡一次。

---

### `pet_status`

宠物状态表，用于保存当前宠物的成长数据。

字段示意：

```text
id
pet_name
skin
level
exp
stage
mood
total_tasks_done
created_at
updated_at
```

| 字段               | 含义                           |
| ------------------ | ------------------------------ |
| `id`               | 固定为 1，第一版只支持一只宠物 |
| `pet_name`         | 宠物名称                       |
| `skin`             | 宠物皮肤，例如 `salty_fish`    |
| `level`            | 宠物等级                       |
| `exp`              | 当前等级内经验                 |
| `stage`            | 当前进化阶段                   |
| `mood`             | 当前心情 / 状态                |
| `total_tasks_done` | 累计完成任务数                 |
| `created_at`       | 创建时间                       |
| `updated_at`       | 更新时间                       |

---

## 任务 / 习惯刷新规则

### 一次性任务

```text
task_type = "task"
```

规则：

- 只在创建当天显示
- 只在创建当天提醒
- 第二天启动程序时自动归档
- 归档后不再出现在今日任务中
- 归档后不再触发提醒
- 不删除任务记录
- 不删除打卡记录
- 历史记录中仍能看到创建当天是否完成

归档字段：

```text
is_archived = 1
```

---

### 长期习惯

```text
task_type = "habit"
```

规则：

- 每天保留
- 每天显示
- 每天可以提醒
- 每天可以打卡
- 历史记录中持续显示

---

## 数据安全机制

CheckMate 当前包含一套本地数据安全保护机制，位于：

```text
data_guard/
```

目标不是做到绝对防破解，而是做到：

- 普通用户不容易误删数据
- 程序更新不容易覆盖数据
- 数据库被外部修改后能检测出来
- 出问题后可以从备份恢复
- 可疑数据库不会被自动登记为正常数据库

---

### 自动备份

程序启动时会自动备份数据库：

```text
auto_checkmate_xxx.db
```

默认保存在：

```text
%LOCALAPPDATA%\CheckMate\data_backups\
```

---

### 完整性校验

程序会计算当前数据库的 SHA256，并保存到：

```text
integrity.json
```

下次启动时重新计算数据库 hash，如果不一致，说明数据库可能被外部修改或损坏。

---

### 可疑数据库备份

检测到数据库异常时，会生成：

```text
suspicious_checkmate_xxx.db
```

并且不会刷新 `integrity.json`，避免把可疑数据库“洗白”。

---

### 恢复前备份

从备份恢复数据库前，会先保存当前数据库：

```text
before_restore_checkmate_xxx.db
```

这样即使恢复错了，也可以找回恢复前的数据。

---

### 数据迁移

旧版本数据库曾位于：

```text
CheckMate/data/checkmate.db
```

现在正式数据库位于：

```text
%LOCALAPPDATA%\CheckMate\data\checkmate.db
```

程序启动时会自动检查旧数据库是否存在，并在需要时迁移到 AppData 用户数据目录。

---

## 程序运行流程

```text
main.py
  ↓
创建 QApplication
  ↓
创建 MainWindow
  ↓
迁移旧数据库
  ↓
初始化数据库
  ↓
归档过期一次性任务
  ↓
运行数据安全检查
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

## 宠物成长流程

```text
用户完成任务
  ↓
database.mark_task_done_today(task_id)
  ↓
判断是否是今天第一次完成该任务
  ↓
pet_growth.add_exp_for_completed_task(task)
  ↓
计算获得经验
  ↓
增加宠物经验
  ↓
判断是否升级
  ↓
判断是否进化
  ↓
保存 pet_status
  ↓
刷新宠物窗口
  ↓
如果升级 / 进化，显示 PetGrowthDialog
```

重复提醒任务完成时不走每日唯一打卡限制，但仍然可以触发宠物经验增长和状态刷新。

---

## 测试脚本

测试脚本位于：

```text
test/
```

当前常用脚本：

| 文件                             | 用途                               |
| -------------------------------- | ---------------------------------- |
| `test_tamper_db.py`              | 模拟外部篡改数据库                 |
| `test_restore_latest_backup.py`  | 从最近自动备份恢复数据库           |
| `test_trust_current_database.py` | 强制信任当前数据库并刷新完整性记录 |

测试说明见：

```text
test/README.md
```

---

## UI 窗口稳定性规范

为了避免窗口拖动或重绘时出现控件压缩、文字变形，后续所有弹窗建议遵守：

```text
1. 外层窗口固定尺寸
2. 内部卡片固定尺寸
3. QLabel 设置固定高度或最小 / 最大高度
4. QPushButton 设置固定高度
5. Layout 设置 SetFixedSize
6. 不依赖 padding 单独撑开按钮高度
```

常用写法：

```python
self.setFixedSize(440, 300)
self.setMinimumSize(440, 300)
self.setMaximumSize(440, 300)
```

按钮高度：

```python
button.setFixedHeight(38)
```

布局固定：

```python
layout = self.layout()
if layout is not None:
    layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
```

---

## 常用 UI 颜色

```css
/* 黑色 */
color: #111827;

/* 白色 */
color: #ffffff;

/* 灰色 */
color: #6b7280;

/* 浅灰 */
color: #9ca3af;

/* 深灰 */
color: #374151;

/* 红色 */
color: #dc2626;

/* 橙色 */
color: #ea580c;

/* 黄色 */
color: #eab308;

/* 绿色 */
color: #16a34a;

/* 青色 */
color: #0891b2;

/* 蓝色 */
color: #2563eb;
```

推荐使用：

```css
/* 正文深色 */
color: #111827;

/* 次要文字 */
color: #6b7280;

/* 提醒 / 危险 */
color: #dc2626;

/* 完成 / 成功 */
color: #16a34a;

/* 主要按钮 / 强调 */
color: #2563eb;

/* 深色背景上的文字 */
color: #ffffff;
```

---

## Git 说明

不要上传虚拟环境、打包产物、本地数据库和用户数据。

推荐 `.gitignore`：

```gitignore
.venv/
__pycache__/
*.pyc

build/
dist/
*.spec

data/
data_backups/
logs/
*.db
*.db-journal
*.db-wal
*.db-shm

.DS_Store
Thumbs.db
```

应该上传：

```text
requirements.txt
README.md
源代码文件
assets 资源文件
test 测试脚本
```

不应该上传：

```text
.venv/
build/
dist/
data/
data_backups/
logs/
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

## 当前已完成

- 基础主窗口
- 任务添加
- 任务编辑
- 任务删除
- 任务备注
- 任务 / 习惯切换
- 一次性任务自动归档
- 每日打卡
- SQLite 本地保存
- AppData 数据目录迁移
- 数据自动备份
- 数据完整性校验
- 数据异常提醒
- 数据恢复测试脚本
- 今日统计
- 连续打卡统计
- 本月完成率统计
- 咸鱼值计算
- 历史记录窗口
- 主窗口任务详情面板
- 任务提醒时间
- 重复提醒
- 美化提醒弹窗
- 稍后提醒选项
- 自定义稍后提醒时间
- 系统托盘后台运行
- 开机自启动
- 桌面宠物浮窗
- 宠物图片 / GIF 加载
- 宠物右键菜单
- 宠物设置窗口
- 宠物随机语录
- 宠物状态切换
- 宠物等级显示
- 宠物经验条
- 宠物升级 / 进化逻辑
- 宠物成长提示弹窗
- 主窗口背景图片
- 添加任务弹窗背景图片
- 应用图标
- 自动打包脚本

---

## 后续计划

- 设置页面
- 数据管理 UI
  - 打开数据文件夹
  - 打开备份文件夹
  - 立即备份
  - 从备份恢复
  - 信任当前数据库
- 宠物详情窗口
- 任务分类 / 标签
- 任务优先级
- 更美观的历史记录页面
- 周报 / 月报统计
- 成就系统
- 更完整的主题系统
- 提醒音效
- 自定义提醒音效
- 安装包制作
- GitHub Releases 发布

---

## 可优化方向

### 1. 宠物详情窗口

右键宠物新增：

```text
宠物状态
```

点击后显示：

```text
名字：咸鱼仔
等级：Lv.5
阶段：努力鱼
经验：20 / 200
累计完成任务：32
当前皮肤：salty_fish
当前阶段：stage_2
```

---

### 2. 设置页面

可以新增设置窗口，用来管理：

- 是否开机自启动
- 默认宠物角色
- 默认稍后提醒时间
- 是否显示桌面宠物
- 提醒音效开关
- 背景图片选择
- 主题颜色选择
- 数据管理功能

---

### 3. 数据管理页面

后续可以在设置页面中加入：

```text
数据管理
├── 打开数据文件夹
├── 打开备份文件夹
├── 立即备份
├── 从最近备份恢复
└── 信任当前数据库
```

---

### 4. 提醒音效

可以在提醒弹窗出现时播放声音。

可选方案：

- `QSoundEffect`
- `winsound`
- 第三方音频库

---

### 5. 统计增强

可以继续增加：

- 最近 7 天完成率
- 最近 30 天完成率
- 单个任务完成趋势
- 最常拖延任务
- 最稳定任务
- 咸鱼值变化曲线

---

### 6. 打包发布

后续可以继续完善：

- 应用图标
- 版本号
- 自动清理旧版本
- 生成 zip 包
- 生成安装包
- 发布到 GitHub Releases

---

## 项目原则

1. 先完成功能闭环，再逐步美化 UI。
2. 每个文件只负责一类功能。
3. 数据库逻辑和界面逻辑分离。
4. 弹窗 UI 和提醒业务逻辑分离。
5. 宠物成长规则和宠物窗口显示分离。
6. 数据安全逻辑和业务功能分离。
7. 桌面宠物作为增强体验，不影响核心打卡功能。
8. 本地优先，不依赖账号和云服务。
9. 保持项目轻量，适合作为桌面应用练手项目。

---

## 当前状态

CheckMate 目前已经可以作为一个本地打卡提醒与宠物养成工具使用。

它已经具备：

- 可用的任务 / 习惯系统
- 可用的每日打卡逻辑
- 可用的重复提醒逻辑
- 可用的提醒系统
- 可用的桌面宠物
- 初步宠物养成系统
- 可用的后台托盘运行
- 初步数据安全保护
- 初步打包能力

后续重点可以放在：

1. 完善设置页面和数据管理入口
2. 完善宠物详情和成就系统
3. 提升 UI 视觉效果
4. 增强统计和复盘能力
5. 制作更正式的 Windows 发布版本