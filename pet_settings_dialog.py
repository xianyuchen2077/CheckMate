from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)

import config_manager


def lock_dialog_layout(dialog):
    """
    固定弹窗布局，避免拖动或重绘时控件压缩变形。
    """
    layout = dialog.layout()

    if layout is not None:
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)


class PetSettingsDialog(QDialog):
    def __init__(self, pet_window, parent=None):
        super().__init__(parent)

        self.pet_window = pet_window
        self.pet_config = config_manager.get_pet_config()

        self.setWindowTitle("宠物设置")
        self.setFixedSize(430, 330)
        self.setMinimumSize(430, 330)
        self.setMaximumSize(430, 330)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.init_ui()
        self.apply_styles()
        self.load_values()

        lock_dialog_layout(self)

    def init_ui(self):
        """
        初始化宠物设置界面。

        布局调整：
        - 外层窗口大小在 __init__() 的 setFixedSize 修改。
        - 白色卡片大小在 card.setFixedSize 修改。
        - 控件间距在 layout.setSpacing 修改。
        - 字体颜色在 apply_styles() 里修改。
        """
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(0)

        card = QFrame()
        card.setObjectName("settingsCard")
        card.setFixedSize(394, 294)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(12)
        card.setLayout(card_layout)

        title_label = QLabel("宠物设置")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFixedHeight(34)

        opacity_title = QLabel("不透明度")
        opacity_title.setObjectName("sectionLabel")
        opacity_title.setFixedHeight(24)

        self.opacity_value_label = QLabel("100%")
        self.opacity_value_label.setObjectName("valueLabel")
        self.opacity_value_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        opacity_header_layout = QHBoxLayout()
        opacity_header_layout.addWidget(opacity_title)
        opacity_header_layout.addWidget(self.opacity_value_label)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setObjectName("opacitySlider")
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setFixedHeight(28)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)

        self.show_on_startup_checkbox = QCheckBox("启动时显示宠物")
        self.show_on_startup_checkbox.setObjectName("optionCheckBox")

        self.always_on_top_checkbox = QCheckBox("宠物窗口始终置顶")
        self.always_on_top_checkbox.setObjectName("optionCheckBox")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.save_position_btn = QPushButton("保存当前位置")
        self.reset_position_btn = QPushButton("回到右下角")
        self.reset_btn = QPushButton("恢复默认")
        self.close_btn = QPushButton("关闭")

        for button in [
            self.save_position_btn,
            self.reset_position_btn,
            self.reset_btn,
            self.close_btn,
        ]:
            button.setFixedHeight(34)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.save_position_btn.clicked.connect(self.save_current_position)
        self.reset_position_btn.clicked.connect(self.reset_position)
        self.reset_btn.clicked.connect(self.reset_defaults)
        self.close_btn.clicked.connect(self.accept)

        self.show_on_startup_checkbox.stateChanged.connect(self.on_show_on_startup_changed)
        self.always_on_top_checkbox.stateChanged.connect(self.on_always_on_top_changed)

        button_layout.addWidget(self.save_position_btn)
        button_layout.addWidget(self.reset_position_btn)

        bottom_button_layout = QHBoxLayout()
        bottom_button_layout.setSpacing(10)
        bottom_button_layout.addWidget(self.reset_btn)
        bottom_button_layout.addWidget(self.close_btn)

        card_layout.addWidget(title_label)
        card_layout.addLayout(opacity_header_layout)
        card_layout.addWidget(self.opacity_slider)
        card_layout.addWidget(self.show_on_startup_checkbox)
        card_layout.addWidget(self.always_on_top_checkbox)
        card_layout.addSpacing(4)
        card_layout.addLayout(button_layout)
        card_layout.addSpacing(4)
        card_layout.addLayout(bottom_button_layout)

        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #eef2ff;
                font-family: "Microsoft YaHei";
            }

            #settingsCard {
                background-color: #ffffff;
                border: 1px solid #dbeafe;
                border-radius: 22px;
            }

            #titleLabel {
                color: #111827;
                font-size: 22px;
                font-weight: bold;
                background-color: transparent;
            }

            #sectionLabel {
                color: #374151;
                font-size: 14px;
                font-weight: 700;
                background-color: transparent;
            }

            #valueLabel {
                color: #2563eb;
                font-size: 14px;
                font-weight: 700;
                background-color: transparent;
            }

            #optionCheckBox {
                color: #111827;
                font-size: 14px;
                font-weight: 600;
                background-color: transparent;
            }

            QSlider::groove:horizontal {
                height: 8px;
                background-color: #e5e7eb;
                border-radius: 4px;
            }

            QSlider::handle:horizontal {
                width: 18px;
                height: 18px;
                margin: -5px 0;
                border-radius: 9px;
                background-color: #2563eb;
            }

            QSlider::sub-page:horizontal {
                background-color: #22c55e;
                border-radius: 4px;
            }

            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 9px;
                padding: 0px 12px;
                font-size: 13px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)

    def load_values(self):
        """
        从配置文件读取当前设置，并同步到 UI。
        """
        opacity = float(self.pet_config.get("opacity", 1.0))
        opacity_percent = int(opacity * 100)

        self.opacity_slider.setValue(opacity_percent)
        self.opacity_value_label.setText(f"{opacity_percent}%")

        self.show_on_startup_checkbox.setChecked(
            bool(self.pet_config.get("show_on_startup", True))
        )

        self.always_on_top_checkbox.setChecked(
            bool(self.pet_config.get("always_on_top", True))
        )

    def on_opacity_changed(self, value):
        """
        拖动滑块时实时修改宠物不透明度，并保存。
        """
        opacity = value / 100
        self.opacity_value_label.setText(f"{value}%")

        self.pet_window.setWindowOpacity(opacity)
        config_manager.update_pet_config(opacity=opacity)

    def on_show_on_startup_changed(self):
        show_on_startup = self.show_on_startup_checkbox.isChecked()
        config_manager.update_pet_config(show_on_startup=show_on_startup)

    def on_always_on_top_changed(self):
        always_on_top = self.always_on_top_checkbox.isChecked()
        config_manager.update_pet_config(always_on_top=always_on_top)

        self.pet_window.set_always_on_top(always_on_top)

    def save_current_position(self):
        """
        保存当前宠物位置。
        """
        pos = self.pet_window.pos()

        config_manager.update_pet_config(
            x=pos.x(),
            y=pos.y()
        )

        self.pet_window.pet_text.setText("当前位置已保存")

    def reset_position(self):
        """
        宠物回到右下角，并保存新位置。
        """
        self.pet_window.move_to_bottom_right()

        pos = self.pet_window.pos()

        config_manager.update_pet_config(
            x=pos.x(),
            y=pos.y()
        )

        self.pet_window.pet_text.setText("已经回到右下角")

    def reset_defaults(self):
        """
        恢复宠物设置默认值。
        """
        # 避免 setValue / setChecked 触发多次信号，导致窗口 flags 被重复刷新
        self.opacity_slider.blockSignals(True)
        self.show_on_startup_checkbox.blockSignals(True)
        self.always_on_top_checkbox.blockSignals(True)

        config_manager.update_pet_config(
            opacity=1.0,
            show_on_startup=True,
            always_on_top=True,
            x=None,
            y=None
        )

        self.opacity_slider.setValue(100)
        self.opacity_value_label.setText("100%")
        self.show_on_startup_checkbox.setChecked(True)
        self.always_on_top_checkbox.setChecked(True)

        self.opacity_slider.blockSignals(False)
        self.show_on_startup_checkbox.blockSignals(False)
        self.always_on_top_checkbox.blockSignals(False)

        self.pet_window.setWindowOpacity(1.0)
        self.pet_window.set_always_on_top(True)
        self.pet_window.move_to_bottom_right()

        # 恢复默认后，重新刷新宠物成长信息和默认状态图片
        self.pet_window.refresh_growth_info()
        self.pet_window.set_idle()

        self.pet_window.pet_text.setText("宠物设置已恢复默认")