# UI 模块说明

该目录用于存放 CheckMate 的界面相关代码。

当前主要包括：

- 设置窗口
- 各类弹窗
- 可复用 UI 组件

后续计划逐步迁移以下文件：

- add_task_dialog.py
- history_dialog.py
- reminder_dialog.py
- repeat_reminder_widget.py
- pet_growth_dialog.py
- pet_settings_dialog.py

原则：

1. UI 文件只负责界面展示和用户交互。
2. 数据库读写统一通过 database.py。
3. 配置读写统一通过 config_manager.py。
4. 提醒业务逻辑统一通过 reminder_manager.py。
5. 宠物成长逻辑统一通过 pet_system/pet_growth.py。