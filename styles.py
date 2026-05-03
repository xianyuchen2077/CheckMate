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

ADD_TASK_DIALOG_STYLE = """
QDialog {
    background-color: #f5f7fb;
    color: #111827;
}

QWidget {
    background-color: transparent;
    color: #111827;
    font-family: "Microsoft YaHei";
}

QLabel {
    color: #111827;
    background-color: transparent;
    font-size: 14px;
}

QCheckBox {
    color: #111827;
    background-color: transparent;
    font-size: 14px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
}

QLineEdit, QTimeEdit, QTextEdit {
    background-color: #ffffff;
    color: #111827;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 8px;
    font-size: 14px;
    selection-background-color: #dbeafe;
    selection-color: #111827;
}

QLineEdit::placeholder {
    color: #9ca3af;
}

QTimeEdit::up-button,
QTimeEdit::down-button {
    background-color: #e5e7eb;
    border: none;
    width: 16px;
}

QTimeEdit::up-button:hover,
QTimeEdit::down-button:hover {
    background-color: #d1d5db;
}

QPushButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1d4ed8;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #1e40af;
    color: #ffffff;
}

QPushButton:disabled {
    background-color: #9ca3af;
    color: #f9fafb;
}
"""