def get_main_window_style(background_path=None):
    background_style = ""

    if background_path:
        background_style = f"""
        #mainBackground {{
            border-image: url("{background_path}") 0 0 0 0 stretch stretch;
        }}
        """

    return f"""
        QMainWindow {{
            background-color: #f5f7fb;
        }}

        {background_style}

        QWidget {{
            color: #111827;
            background-color: transparent;
            font-family: "Microsoft YaHei";
        }}

        QLabel {{
            color: #111827;
            background-color: transparent;
            font-size: 14px;
        }}

        #titleLabel {{
            font-size: 32px;
            font-weight: bold;
            color: #111827;
        }}

        #subtitleLabel {{
            font-size: 15px;
            color: #4b5563;
            margin-bottom: 10px;
        }}

        #sectionTitle {{
            font-size: 20px;
            font-weight: bold;
            color: #111827;
            margin-bottom: 6px;
        }}

        #card {{
            background-color: rgba(255, 255, 255, 230);
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 14px;
        }}

        QListWidget {{
            background-color: rgba(255, 255, 255, 235);
            color: #111827;
            border: 1px solid #d1d5db;
            border-radius: 12px;
            padding: 8px;
            font-size: 15px;
            outline: none;
        }}

        QListWidget::item {{
            background-color: transparent;
            color: #111827;
            padding: 10px;
            border-radius: 8px;
        }}

        QListWidget::item:hover {{
            background-color: #f3f4f6;
            color: #111827;
        }}

        QListWidget::item:selected {{
            background-color: #dbeafe;
            color: #111827;
        }}

        QPushButton {{
            background-color: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 10px 16px;
            font-size: 14px;
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: #1d4ed8;
            color: #ffffff;
        }}

        QPushButton:pressed {{
            background-color: #1e40af;
            color: #ffffff;
        }}

        QPushButton:disabled {{
            background-color: #9ca3af;
            color: #f9fafb;
        }}

        QMessageBox {{
            background-color: #ffffff;
            color: #111827;
        }}

        QMessageBox QLabel {{
            color: #111827;
            background-color: transparent;
        }}

        QMessageBox QPushButton {{
            background-color: #2563eb;
            color: #ffffff;
            border-radius: 8px;
            padding: 6px 12px;
        }}

        #tipLabel {{
            color: #374151;
            background-color: transparent;
            font-size: 14px;
            line-height: 1.6;
        }}
    """

def get_add_task_dialog_style(background_path=None):
    """
    获取添加 / 编辑任务弹窗样式。

    background_path:
        背景图片路径。
        如果为 None，则使用浅灰色背景。
    """
    if background_path:
        background_style = f"""
            #addTaskBackground {{
                border-image: url("{background_path}") 0 0 0 0 stretch stretch;
            }}
        """
    else:
        background_style = """
            #addTaskBackground {
                background-color: #f3f4f6;
            }
        """

    return f"""
        QDialog {{
            background-color: #f3f4f6;
            font-family: "Microsoft YaHei";
        }}

        {background_style}

        /*
            ===== 文字颜色修改区 =====

            表单左侧文字颜色：
                修改 QFormLayout 里的 QLabel color

            输入框文字颜色：
                修改 QLineEdit, QTextEdit, QTimeEdit 的 color

            输入框占位提示颜色：
                修改 placeholder-text-color

            勾选框文字颜色：
                修改 QCheckBox color

            按钮文字颜色：
                修改 QPushButton color
        */

        QLabel {{
            color: #ffffff;
            background-color: transparent;
            font-size: 14px;
            font-weight: 600;
        }}

        QCheckBox {{
            color: #ffffff;
            background-color: transparent;
            font-size: 14px;
            font-weight: 600;
        }}

        QLineEdit,
        QTextEdit,
        QTimeEdit {{
            background-color: rgba(255, 255, 255, 235);
            color: #111827;
            border: 1px solid #d1d5db;
            border-radius: 10px;
            padding: 8px;
            font-size: 14px;
            selection-background-color: #bfdbfe;
        }}

        QLineEdit:disabled,
        QTextEdit:disabled,
        QTimeEdit:disabled {{
            background-color: rgba(229, 231, 235, 220);
            color: #6b7280;
        }}

        QLineEdit {{
            placeholder-text-color: #9ca3af;
        }}

        QTextEdit {{
            placeholder-text-color: #9ca3af;
        }}

        QPushButton {{
            background-color: #2563eb;
            color: #ffffff;
            border: none;
            border-radius: 9px;
            padding: 8px 14px;
            font-size: 14px;
            font-weight: 600;
        }}

        QPushButton:hover {{
            background-color: #1d4ed8;
            color: #ffffff;
        }}

        QPushButton:pressed {{
            background-color: #1e40af;
            color: #ffffff;
        }}

        QDialogButtonBox QPushButton {{
            min-width: 72px;
            min-height: 30px;
        }}
    """