from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QComboBox,
)

import config_manager

class SettingsDialog(QDialog):
    """
    CheckMate 设置窗口。

    当前版本只完成 UI 壳子：
        - 常规设置
        - 提醒设置
        - 桌面宠物
        - 数据管理
        - 外观设置
        - 关于

    后续再逐步接入 config_manager、auto_start、data_guard 等真实逻辑。
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_window = parent

        # 宠物设置控件引用
        self.pet_visible_switch = None
        self.pet_startup_switch = None
        self.pet_top_switch = None
        self.pet_opacity_slider = None

        self.setWindowTitle("设置 - CheckMate")
        self.setFixedSize(780, 540)

        self.nav_list = None
        self.page_stack = None

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(14)

        # 左侧导航
        nav_card = QFrame()
        nav_card.setObjectName("navCard")
        nav_card.setFixedWidth(170)

        nav_layout = QVBoxLayout()
        nav_layout.setContentsMargins(12, 12, 12, 12)
        nav_layout.setSpacing(10)
        nav_card.setLayout(nav_layout)

        title_label = QLabel("设置")
        title_label.setObjectName("settingsTitle")

        subtitle_label = QLabel("CheckMate")
        subtitle_label.setObjectName("settingsSubtitle")

        self.nav_list = QListWidget()
        self.nav_list.setObjectName("settingsNav")
        self.nav_list.setSpacing(4)
        self.nav_list.setFrameShape(QFrame.Shape.NoFrame)

        nav_items = [
            "常规设置",
            "提醒设置",
            "桌面宠物",
            "数据管理",
            "外观设置",
            "关于",
        ]

        for text in nav_items:
            item = QListWidgetItem(text)
            item.setSizeHint(item.sizeHint())
            self.nav_list.addItem(item)

        self.nav_list.currentRowChanged.connect(self.switch_page)

        nav_layout.addWidget(title_label)
        nav_layout.addWidget(subtitle_label)
        nav_layout.addSpacing(8)
        nav_layout.addWidget(self.nav_list)
        nav_layout.addStretch()

        # 右侧页面
        content_card = QFrame()
        content_card.setObjectName("contentCard")

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_card.setLayout(content_layout)

        self.page_stack = QStackedWidget()
        self.page_stack.setObjectName("settingsStack")

        self.page_stack.addWidget(self.create_general_page())
        self.page_stack.addWidget(self.create_reminder_page())
        self.page_stack.addWidget(self.create_pet_page())
        self.page_stack.addWidget(self.create_data_page())
        self.page_stack.addWidget(self.create_appearance_page())
        self.page_stack.addWidget(self.create_about_page())

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(18, 0, 18, 16)

        self.reset_btn = QPushButton("恢复默认")
        self.reset_btn.setObjectName("secondaryButton")
        self.reset_btn.setFixedHeight(36)
        self.reset_btn.clicked.connect(self.on_reset_defaults)

        bottom_layout.addWidget(self.reset_btn)
        bottom_layout.addStretch()

        self.apply_btn = QPushButton("应用")
        self.apply_btn.setObjectName("secondaryButton")
        self.apply_btn.setFixedHeight(36)
        self.apply_btn.clicked.connect(self.on_apply_settings)

        self.save_btn = QPushButton("保存并关闭")
        self.save_btn.setObjectName("primaryButton")
        self.save_btn.setFixedHeight(36)
        self.save_btn.clicked.connect(self.on_save_and_close)

        bottom_layout.addWidget(self.apply_btn)
        bottom_layout.addWidget(self.save_btn)

        content_layout.addWidget(self.page_stack)
        content_layout.addLayout(bottom_layout)

        root_layout.addWidget(nav_card)
        root_layout.addWidget(content_card, 1)

        self.setLayout(root_layout)

        self.nav_list.setCurrentRow(0)

    def switch_page(self, index):
        if self.page_stack is None:
            return

        if index < 0:
            return

        self.page_stack.setCurrentIndex(index)

    # =========================
    # 页面创建
    # =========================

    def create_general_page(self):
        page = self.create_scroll_page("常规设置", "管理启动、托盘和程序基础行为。")

        container = page.findChild(QWidget, "pageContent")

        self.add_switch_row(
            container,
            title="开机自启动",
            description="Windows 登录后自动启动 CheckMate。",
            checked=False,
        )

        self.add_switch_row(
            container,
            title="启动时显示主窗口",
            description="打开程序时自动显示主窗口。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="启动时显示桌面宠物",
            description="打开程序时自动显示桌面宠物。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="关闭窗口时最小化到托盘",
            description="点击右上角关闭按钮时，程序继续在后台运行。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="退出程序前确认",
            description="通过托盘菜单退出时弹出确认提示，避免误退。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="启动时自动检查数据安全",
            description="程序启动时检查数据库完整性，并在异常时提醒。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="启动时自动执行每日刷新",
            description="打开程序时自动处理任务顺延、归档和习惯刷新。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="显示托盘提示",
            description="关闭主窗口、完成任务等操作后，在系统托盘显示简短提示。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="调试模式",
            description="显示更多运行日志和调试信息，方便排查问题。",
            checked=False,
        )

        self.add_hint_card(
            container,
            "说明",
            "当前页面先完成 UI 展示，后续会接入 auto_start.py 和 config_manager.py。"
        )

        return page

    def create_reminder_page(self):
        page = self.create_scroll_page("提醒设置", "管理提醒弹窗、系统通知和默认提醒行为。")

        container = page.findChild(QWidget, "pageContent")

        self.add_combo_row(
            container,
            title="默认提醒时间",
            description="新建任务时可使用的默认提醒时间。",
            items=["不设置", "08:00", "09:00", "12:00", "18:00", "22:00"],
            current_index=0,
        )

        self.add_combo_row(
            container,
            title="默认重复提醒间隔",
            description="新建任务时可使用的默认重复间隔。",
            items=["不重复", "5 分钟", "10 分钟", "30 分钟", "1 小时", "自定义"],
            current_index=0,
        )

        self.add_combo_row(
            container,
            title="默认稍后提醒时间",
            description="点击稍后提醒时优先使用的默认时间。",
            items=["5 分钟", "10 分钟", "30 分钟", "1 小时"],
            current_index=0,
        )

        self.add_switch_row(
            container,
            title="显示系统通知",
            description="到点时在 Windows 通知区域显示提醒。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="显示提醒弹窗",
            description="到点时弹出 CheckMate 提醒窗口。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="“今天不再提醒”前二次确认",
            description="避免误点后错过任务提醒。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="提醒弹窗置顶",
            description="提醒弹窗出现时保持在其他窗口上方。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="提醒弹窗自动聚焦",
            description="提醒弹窗出现时自动获得焦点，适合强提醒场景。",
            checked=False,
        )

        self.add_combo_row(
            container,
            title="错过提醒后的处理",
            description="如果提醒弹窗被关闭或没有响应，决定后续处理方式。",
            items=["不处理", "5 分钟后再次提醒", "按重复提醒规则继续", "今天不再提醒"],
            current_index=2,
        )

        self.add_switch_row(
            container,
            title="启用静默时段",
            description="在指定时间段内不弹出提醒，只保留任务状态。",
            checked=False,
        )

        self.add_combo_row(
            container,
            title="静默时段",
            description="静默期间不主动打扰，后续可接入自定义时间段。",
            items=["22:00 - 08:00", "23:00 - 07:00", "00:00 - 08:00", "自定义"],
            current_index=0,
        )

        self.add_switch_row(
            container,
            title="提醒音效",
            description="提醒弹窗出现时播放提示音。",
            checked=False,
        )

        self.add_hint_card(
            container,
            "说明",
            "提醒设置第一版建议只作为默认值和行为开关，具体任务自己的提醒时间仍然优先。"
        )

        return page

    def create_pet_page(self):
        page = self.create_scroll_page("桌面宠物", "管理桌面宠物显示、置顶、透明度和位置。")

        container = page.findChild(QWidget, "pageContent")

        pet_config = config_manager.get_pet_config()

        pet_visible = bool(pet_config.get("visible", True))
        pet_show_on_startup = bool(pet_config.get("show_on_startup", True))
        pet_always_on_top = bool(pet_config.get("always_on_top", True))
        pet_opacity = float(pet_config.get("opacity", 1.0))
        pet_opacity_percent = int(pet_opacity * 100)

        self.pet_visible_switch = self.add_switch_row(
            container,
            title="显示桌面宠物",
            description="关闭后隐藏桌面宠物，但不影响任务提醒功能。",
            checked=pet_visible,
        )

        self.pet_top_switch = self.add_switch_row(
            container,
            title="宠物窗口置顶",
            description="让宠物始终显示在其他窗口上方。",
            checked=pet_always_on_top,
        )

        self.pet_opacity_slider = self.add_slider_row(
            container,
            title="宠物透明度",
            description="调整桌面宠物窗口透明度。",
            value=pet_opacity_percent,
            minimum=30,
            maximum=100,
            suffix="%",
        )

        self.add_slider_row(
            container,
            title="宠物大小",
            description="调整桌面宠物显示大小。",
            value=100,
            minimum=60,
            maximum=160,
            suffix="%",
        )

        self.add_combo_row(
            container,
            title="宠物皮肤",
            description="选择当前使用的桌面宠物形象。",
            items=["咸鱼仔 salty_fish", "Rick", "Morty", "后续添加"],
            current_index=0,
        )

        self.pet_startup_switch = self.add_switch_row(
            container,
            title="启动时显示宠物",
            description="打开程序时自动显示桌面宠物。",
            checked=pet_show_on_startup,
        )

        self.add_switch_row(
            container,
            title="双击宠物打开主窗口",
            description="双击桌面宠物时打开 CheckMate 主窗口。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="显示今日进度",
            description="在宠物窗口中显示今日任务完成进度。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="显示等级和经验条",
            description="在宠物窗口中显示等级、阶段和经验条。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="启用随机语录",
            description="让宠物定时切换鼓励语录。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="提醒时切换宠物状态",
            description="任务到点时，宠物自动切换到提醒状态。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="完成后切换宠物状态",
            description="完成任务后，宠物短暂切换到完成状态。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="锁定宠物位置",
            description="开启后禁止拖动宠物，避免误触移动。",
            checked=False,
        )

        self.add_combo_row(
            container,
            title="语录切换间隔",
            description="随机语录自动切换的时间间隔。",
            items=["30 秒", "1 分钟", "3 分钟", "5 分钟"],
            current_index=1,
        )

        button_row = self.create_button_row(
            title="宠物位置",
            description="将宠物移动回默认位置，或清除保存的位置。",
            buttons=["回到右下角", "重置宠物位置"],
        )
        self.add_to_container(container, button_row)

        return page

    def create_data_page(self):
        page = self.create_scroll_page("数据管理", "查看数据位置，并提供备份与恢复入口。")

        container = page.findChild(QWidget, "pageContent")

        self.add_info_row(
            container,
            title="当前数据文件",
            value="%LOCALAPPDATA%\\CheckMate\\data\\checkmate.db",
        )

        self.add_info_row(
            container,
            title="备份文件夹",
            value="%LOCALAPPDATA%\\CheckMate\\data_backups\\",
        )

        self.add_info_row(
            container,
            title="最近备份",
            value="后续接入 backup_manager 后显示",
        )

        self.add_info_row(
            container,
            title="数据库状态",
            value="后续接入 integrity_manager 后显示：正常 / 可疑 / 需要恢复",
        )

        self.add_info_row(
            container,
            title="自动备份数量",
            value="后续接入 backup_manager 后显示",
        )

        self.add_switch_row(
            container,
            title="启动时自动备份",
            description="程序启动时自动备份当前数据库。",
            checked=True,
        )

        self.add_combo_row(
            container,
            title="自动备份保留数量",
            description="超过数量后可清理较旧的自动备份。",
            items=["保留 5 个", "保留 10 个", "保留 20 个", "不自动清理"],
            current_index=1,
        )

        folder_buttons = self.create_button_row(
            title="文件夹",
            description="快速打开数据文件夹和备份文件夹。",
            buttons=["打开数据文件夹", "打开备份文件夹"],
        )
        self.add_to_container(container, folder_buttons)

        backup_buttons = self.create_button_row(
            title="备份",
            description="手动创建当前数据库备份。",
            buttons=["立即备份"],
        )
        self.add_to_container(container, backup_buttons)

        export_buttons = self.create_button_row(
            title="导入 / 导出",
            description="导出当前数据，或从外部备份文件导入数据。后续接入真实逻辑。",
            buttons=["导出数据", "导入数据"],
        )
        self.add_to_container(container, export_buttons)

        cleanup_buttons = self.create_button_row(
            title="清理",
            description="清理旧备份和临时可疑备份。后续接入真实逻辑。",
            buttons=["清理旧备份", "清理可疑备份"],
        )
        self.add_to_container(container, cleanup_buttons)

        danger_buttons = self.create_button_row(
            title="危险操作",
            description="恢复备份和信任数据库需要二次确认，后续再接入真实逻辑。",
            buttons=["从最近备份恢复", "信任当前数据库"],
            danger=True,
        )
        self.add_to_container(container, danger_buttons)

        self.add_hint_card(
            container,
            "安全提示",
            "数据管理页面涉及正式数据库。第一版建议先实现打开文件夹和立即备份，恢复与信任操作后续再接入。"
        )

        return page

    def create_appearance_page(self):
        page = self.create_scroll_page("外观设置", "管理主题色、字体大小和显示密度。")

        container = page.findChild(QWidget, "pageContent")

        self.add_combo_row(
            container,
            title="主题色",
            description="选择主界面按钮和强调色。",
            items=["蓝色", "绿色", "橙色", "紫色"],
            current_index=0,
        )

        self.add_combo_row(
            container,
            title="字体大小",
            description="调整主界面和弹窗的基础字号。",
            items=["小", "默认", "大"],
            current_index=1,
        )

        self.add_combo_row(
            container,
            title="界面密度",
            description="控制任务列表、按钮和卡片的间距。",
            items=["舒适", "默认", "紧凑"],
            current_index=1,
        )

        self.add_slider_row(
            container,
            title="主窗口透明度",
            description="调整主窗口整体透明度。后续接入真实窗口属性。",
            value=100,
            minimum=70,
            maximum=100,
            suffix="%",
        )

        self.add_combo_row(
            container,
            title="圆角风格",
            description="控制卡片和按钮的圆角大小。",
            items=["小圆角", "默认圆角", "大圆角"],
            current_index=1,
        )

        self.add_switch_row(
            container,
            title="启用轻微动画",
            description="切换页面、按钮悬停时使用轻微动画效果。后续接入。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="显示卡片阴影",
            description="为设置卡片和主界面卡片增加轻微阴影。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="使用主窗口背景图片",
            description="开启后使用 assets/backgrounds/main_bg.png。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="使用添加任务弹窗背景图片",
            description="开启后使用 assets/backgrounds/add_task_bg.png。",
            checked=True,
        )

        self.add_switch_row(
            container,
            title="紧凑模式",
            description="减小卡片间距和按钮高度，适合小屏幕。",
            checked=False,
        )

        self.add_hint_card(
            container,
            "说明",
            "外观设置第一版建议先做 UI 展示，主题系统和自定义背景图片后续再接入。"
        )

        return page

    def create_about_page(self):
        page = self.create_scroll_page("关于", "CheckMate / 不要成为咸鱼")

        container = page.findChild(QWidget, "pageContent")

        about_card = QFrame()
        about_card.setObjectName("settingGroup")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        about_card.setLayout(layout)

        app_title = QLabel("CheckMate / 不要成为咸鱼")
        app_title.setObjectName("aboutTitle")

        version_label = QLabel("版本：v0.1.0-beta")
        version_label.setObjectName("settingDescription")

        desc = QLabel(
            "一个带桌面宠物、任务提醒、重复提醒、宠物养成和数据安全保护的本地打卡督促小程序。"
        )
        desc.setWordWrap(True)
        desc.setObjectName("settingDescription")

        tech = QLabel("技术栈：Python + PySide6 + SQLite")
        tech.setObjectName("settingDescription")

        data_path = QLabel("数据目录：%LOCALAPPDATA%\\CheckMate\\")
        data_path.setObjectName("settingDescription")

        status = QLabel("当前状态：核心打卡 / 提醒 / 刷新规则已完成阶段性稳定测试")
        status.setWordWrap(True)
        status.setObjectName("settingDescription")

        slogan = QLabel("今天也别悄悄变成咸鱼。")
        slogan.setObjectName("aboutSlogan")

        layout.addWidget(app_title)
        layout.addWidget(version_label)
        layout.addWidget(desc)
        layout.addWidget(tech)
        layout.addWidget(data_path)
        layout.addWidget(status)
        layout.addSpacing(6)
        layout.addWidget(slogan)

        self.add_to_container(container, about_card)

        link_buttons = self.create_button_row(
            title="相关链接",
            description="后续可以接入 GitHub 仓库、Release 页面和 README。",
            buttons=["打开 GitHub 仓库", "打开 Release 页面", "查看 README"],
        )
        self.add_to_container(container, link_buttons)

        return page

    # =========================
    # 通用 UI 组件
    # =========================
    def get_container_layout(self, container):
        """
        安全获取容器布局，避免 Pylance 认为 container.layout() 可能是 None。
        """
        layout = container.layout()

        if layout is None:
            raise RuntimeError("设置页面容器没有 layout。")

        return layout


    def add_to_container(self, container, widget):
        """
        安全地向设置页面容器中添加控件。
        """
        layout = self.get_container_layout(container)
        layout.addWidget(widget)

    def create_scroll_page(self, title, subtitle):
        outer = QWidget()
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer.setLayout(outer_layout)

        scroll_area = QScrollArea()
        scroll_area.setObjectName("settingsScroll")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        page = QWidget()
        page.setObjectName("settingsPage")

        page_layout = QVBoxLayout()
        page_layout.setContentsMargins(24, 22, 24, 20)
        page_layout.setSpacing(14)
        page.setLayout(page_layout)

        header_title = QLabel(title)
        header_title.setObjectName("pageTitle")

        header_subtitle = QLabel(subtitle)
        header_subtitle.setObjectName("pageSubtitle")
        header_subtitle.setWordWrap(True)

        content = QWidget()
        content.setObjectName("pageContent")

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 4, 0, 0)
        content_layout.setSpacing(12)
        content.setLayout(content_layout)

        page_layout.addWidget(header_title)
        page_layout.addWidget(header_subtitle)
        page_layout.addSpacing(4)
        page_layout.addWidget(content)
        page_layout.addStretch()

        scroll_area.setWidget(page)
        outer_layout.addWidget(scroll_area)

        return outer

    def add_switch_row(self, container, title, description, checked=False):
        row = QFrame()
        row.setObjectName("settingGroup")

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        row.setLayout(layout)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("settingTitle")

        desc_label = QLabel(description)
        desc_label.setObjectName("settingDescription")
        desc_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)

        check_button = QPushButton()
        check_button.setObjectName("settingCheckButton")
        check_button.setCheckable(True)
        check_button.setChecked(checked)
        check_button.setFixedSize(44, 44)
        check_button.setCursor(Qt.CursorShape.PointingHandCursor)

        if checked:
            check_button.setText("✓")
        else:
            check_button.setText("")

        check_button.toggled.connect(
            lambda is_checked, button=check_button: button.setText("✓" if is_checked else "")
        )

        check_button.toggled.connect(
            lambda checked_value, key=title: self.on_setting_changed(key, checked_value)
        )

        layout.addLayout(text_layout, 1)
        layout.addWidget(check_button)

        self.add_to_container(container, row)
        return check_button

    def add_combo_row(self, container, title, description, items, current_index=0):
        row = QFrame()
        row.setObjectName("settingGroup")

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        row.setLayout(layout)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("settingTitle")

        desc_label = QLabel(description)
        desc_label.setObjectName("settingDescription")
        desc_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)

        combo = QComboBox()
        combo.setObjectName("settingCombo")
        combo.addItems(items)
        combo.setCurrentIndex(current_index)
        combo.setFixedWidth(160)

        combo.currentTextChanged.connect(
            lambda value, key=title: self.on_setting_changed(key, value)
        )

        layout.addLayout(text_layout, 1)
        layout.addWidget(combo)

        self.add_to_container(container, row)
        return combo

    def add_slider_row(self, container, title, description, value, minimum, maximum, suffix=""):
        row = QFrame()
        row.setObjectName("settingGroup")

        layout = QHBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        row.setLayout(layout)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("settingTitle")

        desc_label = QLabel(description)
        desc_label.setObjectName("settingDescription")
        desc_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)

        slider_layout = QHBoxLayout()
        slider_layout.setContentsMargins(0, 0, 0, 0)
        slider_layout.setSpacing(8)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setObjectName("settingSlider")
        slider.setRange(minimum, maximum)
        slider.setValue(value)
        slider.setFixedWidth(130)

        value_label = QLabel(f"{value}{suffix}")
        value_label.setObjectName("sliderValue")
        value_label.setFixedWidth(46)

        slider.valueChanged.connect(
            lambda new_value: value_label.setText(f"{new_value}{suffix}")
        )

        slider.valueChanged.connect(
            lambda value, key=title: self.on_setting_changed(key, value)
        )

        slider_layout.addWidget(slider)
        slider_layout.addWidget(value_label)

        layout.addLayout(text_layout, 1)
        layout.addLayout(slider_layout)

        self.add_to_container(container, row)
        return slider

    def add_info_row(self, container, title, value):
        row = QFrame()
        row.setObjectName("settingGroup")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)
        row.setLayout(layout)

        title_label = QLabel(title)
        title_label.setObjectName("settingTitle")

        value_label = QLabel(value)
        value_label.setObjectName("pathLabel")
        value_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        self.add_to_container(container, row)
        return value_label

    def create_button_row(self, title, description, buttons, danger=False):
        row = QFrame()
        row.setObjectName("settingGroup")

        layout = QVBoxLayout()
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)
        row.setLayout(layout)

        title_label = QLabel(title)
        title_label.setObjectName("settingTitle")

        desc_label = QLabel(description)
        desc_label.setObjectName("settingDescription")
        desc_label.setWordWrap(True)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()

        for text in buttons:
            button = QPushButton(text)
            button.setFixedHeight(34)
            button.setObjectName("dangerButton" if danger else "secondaryButton")
            button.clicked.connect(
                lambda checked=False, action=text: self.on_placeholder_button_clicked(action)
            )
            button_layout.addWidget(button)

        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addLayout(button_layout)

        return row

    def add_hint_card(self, container, title, description):
        card = QFrame()
        card.setObjectName("hintCard")

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)
        card.setLayout(layout)

        title_label = QLabel(title)
        title_label.setObjectName("hintTitle")

        desc_label = QLabel(description)
        desc_label.setObjectName("hintDescription")
        desc_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(desc_label)

        self.add_to_container(container, card)

    def on_setting_changed(self, key, value):
        """
        预留接口：任意设置项变化。
        后续可以在这里标记 dirty 状态，或者写入临时配置。
        """
        print(f"TODO: 设置变化：{key} = {value}")

    def on_reset_defaults(self):
        """
        预留接口：恢复默认设置。
        后续接入 config_manager 后，在这里重置配置。
        """
        print("TODO: 恢复默认设置")


    def on_apply_settings(self):
        """
        应用设置但不关闭窗口。

        当前已接入：
            - 显示 / 隐藏桌面宠物
            - 启动时显示宠物
            - 宠物窗口置顶
            - 宠物透明度
        """
        if (
            self.pet_visible_switch is None
            or self.pet_startup_switch is None
            or self.pet_top_switch is None
            or self.pet_opacity_slider is None
        ):
            print("宠物设置控件尚未初始化。")
            return

        visible = self.pet_visible_switch.isChecked()
        show_on_startup = self.pet_startup_switch.isChecked()
        always_on_top = self.pet_top_switch.isChecked()
        opacity = self.pet_opacity_slider.value() / 100

        config_manager.update_pet_config(
            visible=visible,
            show_on_startup=show_on_startup,
            always_on_top=always_on_top,
            opacity=opacity,
        )

        if self.main_window is not None and hasattr(self.main_window, "apply_pet_settings_from_dialog"):
            self.main_window.apply_pet_settings_from_dialog()

        print(
            "已应用宠物设置："
            f"visible={visible}, "
            f"show_on_startup={show_on_startup}, "
            f"always_on_top={always_on_top}, "
            f"opacity={opacity}"
        )


    def on_save_and_close(self):
        """
        预留接口：保存设置并关闭窗口。
        """
        self.on_apply_settings()
        self.accept()

    def on_placeholder_button_clicked(self, action):
        """
        预留接口：设置页按钮点击事件。
        后续根据 action 分发到真实功能。
        """
        print(f"TODO: 设置按钮点击：{action}")

    # =========================
    # 样式
    # =========================

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #eef2ff;
                font-family: "Microsoft YaHei";
                color: #111827;
            }

            #navCard,
            #contentCard {
                background-color: rgba(255, 255, 255, 235);
                border: 1px solid #dbeafe;
                border-radius: 18px;
            }

            #settingsTitle {
                color: #111827;
                font-size: 22px;
                font-weight: 700;
                background-color: transparent;
            }

            #settingsSubtitle {
                color: #6b7280;
                font-size: 12px;
                background-color: transparent;
            }

            #settingsNav {
                background-color: transparent;
                border: none;
                outline: none;
                color: #374151;
                font-size: 14px;
            }

            #settingsNav::item {
                min-height: 36px;
                padding: 8px 10px;
                border-radius: 10px;
            }

            #settingsNav::item:hover {
                background-color: #eff6ff;
                color: #1d4ed8;
            }

            #settingsNav::item:selected {
                background-color: #2563eb;
                color: #ffffff;
                font-weight: 600;
            }

            #settingsScroll {
                background-color: transparent;
                border: none;
            }

            #settingsPage {
                background-color: transparent;
            }

            #pageTitle {
                color: #111827;
                font-size: 24px;
                font-weight: 700;
                background-color: transparent;
            }

            #pageSubtitle {
                color: #6b7280;
                font-size: 13px;
                background-color: transparent;
            }

            #settingGroup {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 14px;
            }

            #settingTitle {
                color: #111827;
                font-size: 14px;
                font-weight: 600;
                background-color: transparent;
            }

            #settingDescription {
                color: #6b7280;
                font-size: 12px;
                background-color: transparent;
            }

            #settingCheckButton {
                background-color: #ffffff;
                color: #ffffff;
                border: 2px solid #cbd5e1;
                border-radius: 10px;
                font-size: 26px;
                font-weight: 900;
                padding: 0px;
            }

            #settingCheckButton:hover {
                border-color: #93c5fd;
                background-color: #eff6ff;
            }

            #settingCheckButton:checked {
                background-color: #2563eb;
                border-color: #2563eb;
                color: #ffffff;
            }

            #settingCheckButton:checked:hover {
                background-color: #1d4ed8;
                border-color: #1d4ed8;
            }

            #settingCombo {
                background-color: #f9fafb;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 6px 8px;
                font-size: 13px;
            }

            #settingCombo:hover {
                border-color: #93c5fd;
            }

            #settingSlider {
                background-color: transparent;
            }

            #sliderValue {
                color: #374151;
                font-size: 13px;
                background-color: transparent;
            }

            #pathLabel {
                color: #374151;
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 8px;
                font-size: 12px;
            }

            #hintCard {
                background-color: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 14px;
            }

            #hintTitle {
                color: #1e40af;
                font-size: 13px;
                font-weight: 700;
                background-color: transparent;
            }

            #hintDescription {
                color: #1f2937;
                font-size: 12px;
                background-color: transparent;
            }

            #aboutTitle {
                color: #111827;
                font-size: 20px;
                font-weight: 700;
                background-color: transparent;
            }

            #aboutSlogan {
                color: #2563eb;
                font-size: 14px;
                font-weight: 700;
                background-color: transparent;
            }

            QPushButton {
                border: none;
                border-radius: 9px;
                padding: 7px 12px;
                font-size: 13px;
                font-weight: 600;
            }

            #primaryButton {
                background-color: #2563eb;
                color: #ffffff;
            }

            #primaryButton:hover {
                background-color: #1d4ed8;
            }

            #secondaryButton {
                background-color: #e5e7eb;
                color: #111827;
            }

            #secondaryButton:hover {
                background-color: #d1d5db;
            }

            #dangerButton {
                background-color: #fee2e2;
                color: #b91c1c;
            }

            #dangerButton:hover {
                background-color: #fecaca;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 6px 2px 6px 2px;
            }

            QScrollBar::handle:vertical {
                background: #c7d2fe;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical:hover {
                background: #93c5fd;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.exec()