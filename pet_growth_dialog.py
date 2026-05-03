from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QFrame,
    QSizePolicy,
)

def lock_dialog_layout(dialog):
    """
    固定弹窗布局，避免拖动或重绘时控件被压缩变形。
    """
    layout = dialog.layout()

    if layout is not None:
        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

class PetGrowthDialog(QDialog):
    def __init__(self, growth_result, parent=None):
        super().__init__(parent)

        self.growth_result = growth_result

        self.setWindowTitle("宠物成长")

        # 固定外层窗口尺寸，避免拖动时窗口内部重新压缩
        self.setFixedSize(440, 300)
        self.setMinimumSize(440, 300)
        self.setMaximumSize(440, 300)

        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.init_ui()
        self.apply_styles()

        lock_dialog_layout(self)

    def init_ui(self):
        """
        初始化宠物成长弹窗界面。

        布局调整说明：
        1. 外层窗口大小在 __init__() 里的 self.setFixedSize(...) 控制。
        2. 白色卡片大小由 card.setFixedSize(...) 控制。
        3. 每个 QLabel 的高度由 setFixedHeight / setMinimumHeight / setMaximumHeight 控制。
        4. 控件之间的默认间距由 card_layout.setSpacing(...) 控制。
        5. 如果想单独拉开某两个控件的距离，可以用 card_layout.addSpacing(...)。
        6. 字体大小主要在 apply_styles() 的 QSS 中修改。
        """
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(0)

        # 弹窗中间的白色卡片。
        # 如果内容放不下，优先调大这里和 __init__() 里的窗口高度。
        card = QFrame()
        card.setObjectName("growthCard")
        card.setFixedSize(404, 264)
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(24, 18, 24, 18)

        # 控制卡片内大部分控件之间的默认间距。
        # 数字越大，整体越松；数字越小，整体越紧。
        card_layout.setSpacing(8)

        card.setLayout(card_layout)

        title_text = self.get_title_text()
        icon_text = self.get_icon_text()

        # 顶部图标，例如 🎉 / ✨ / 🐟。
        # 图标大小在 apply_styles() 的 #iconLabel 里改 font-size。
        icon_label = QLabel(icon_text)
        icon_label.setObjectName("iconLabel")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedHeight(42)
        icon_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # 主标题，例如“宠物升级了！”
        # 标题字体在 apply_styles() 的 #titleLabel 里改。
        title_label = QLabel(title_text)
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFixedHeight(34)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # 成长提示文案，例如“获得 20 EXP！宠物升级了...”
        # 如果文字被挤压，调大 minimum / maximum height。
        message_label = QLabel(self.growth_result["message"])
        message_label.setObjectName("messageLabel")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        message_label.setMinimumHeight(48)
        message_label.setMaximumHeight(58)
        message_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # 详细信息，例如经验、等级变化、阶段变化。
        # 如果你在 get_detail_text() 里用了 "\n\n".join(lines)，这里高度要适当调大。
        detail_label = QLabel(self.get_detail_text())
        detail_label.setObjectName("detailLabel")
        detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        detail_label.setWordWrap(True)
        detail_label.setMinimumHeight(48)
        detail_label.setMaximumHeight(70)
        detail_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # 确认按钮。
        # 按钮高度在 setFixedHeight() 控制；
        # 按钮颜色、字体在 apply_styles() 的 #primaryButton / QPushButton 里改。
        ok_btn = QPushButton("知道啦")
        ok_btn.setObjectName("primaryButton")
        ok_btn.setFixedHeight(38)
        ok_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        ok_btn.clicked.connect(self.accept)

        card_layout.addWidget(icon_label)
        card_layout.addWidget(title_label)
        card_layout.addWidget(message_label)
        card_layout.addWidget(detail_label)

        # 单独把按钮往下推一点。
        # 想更靠下：改成 10 / 12 / 16。
        # 想更靠上：改成 0 / 2 / 4。
        card_layout.addSpacing(12)

        card_layout.addWidget(ok_btn)

        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

    def get_icon_text(self):
        if self.growth_result.get("evolved"):
            return "✨"

        if self.growth_result.get("leveled_up"):
            return "🎉"

        return "🐟"

    def get_title_text(self):
        if self.growth_result.get("evolved"):
            return "宠物进化了！"

        if self.growth_result.get("leveled_up"):
            return "宠物升级了！"

        return "宠物获得经验！"

    def get_detail_text(self):
        exp_gained = self.growth_result.get("exp_gained", 0)

        old_level = self.growth_result.get("old_level")
        new_level = self.growth_result.get("new_level")

        old_stage_name = self.growth_result.get("old_stage_name")
        new_stage_name = self.growth_result.get("new_stage_name")

        lines = [
            f"获得经验：+{exp_gained} EXP",
            f"等级变化：Lv.{old_level} → Lv.{new_level}",
        ]

        if self.growth_result.get("evolved"):
            lines.append(f"阶段变化：{old_stage_name} → {new_stage_name}")

        return "\n".join(lines)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #eef2ff;
                font-family: "Microsoft YaHei";
            }

            #growthCard {
                background-color: #ffffff;
                border: 1px solid #dbeafe;
                border-radius: 22px;
            }

            #iconLabel {
                font-size: 38px;
                background-color: transparent;
            }

            #titleLabel {
                color: #111827;
                font-size: 23px;
                font-weight: bold;
                background-color: transparent;
            }

            #messageLabel {
                color: #1f2937;
                font-size: 14px;
                font-weight: 600;
                background-color: transparent;
            }

            #detailLabel {
                color: #4b5563;
                font-size: 13px;
                background-color: transparent;
            }

            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 0px 12px;
                font-size: 14px;
                font-weight: 600;
            }

            #primaryButton {
                background-color: #2563eb;
                color: #ffffff;
            }

            #primaryButton:hover {
                background-color: #1d4ed8;
            }

            #primaryButton:pressed {
                background-color: #1e40af;
            }
        """)