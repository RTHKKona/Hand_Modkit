import sys
import struct
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QWidget, 
    QApplication, QComboBox, QRadioButton, QButtonGroup, QFrame, QAction, QMenuBar,QMessageBox
)
from PyQt5.QtGui import QColor, QFont, QTextCursor
from PyQt5.QtCore import Qt

class HexConverterEncoder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.toggle_dark_mode()  # Start in dark mode by default

    def init_ui(self):
        # Increase default font size
        font = QFont()
        font.setPointSize(font.pointSize() + 1)
        self.setFont(font)

        # Main widget and layout
        central_widget = QWidget(self)
        main_layout = QHBoxLayout(central_widget)

        # Left Column - Input
        left_frame = QFrame(self)
        left_frame.setFrameShape(QFrame.Box)
        left_layout = QVBoxLayout(left_frame)
        
        self.hex_input_label = QLabel("Hexadecimal Input", self)
        self.hex_input = QTextEdit(self)
        self.hex_input.setPlaceholderText("Enter hexadecimal value (e.g., f0 9f 8f b3 ef b8 8f e2 80 8d)")
        self.hex_input.textChanged.connect(self.format_hex_input)  # Auto format input
        left_layout.addWidget(self.hex_input_label)
        left_layout.addWidget(self.hex_input)

        # Center Column - Options and Settings
        center_frame = QFrame(self)
        center_frame.setFrameShape(QFrame.Box)
        center_layout = QVBoxLayout(center_frame)
        
        self.settings_label = QLabel("Conversion Settings", self)
        center_layout.addWidget(self.settings_label)

        self.conversion_type = QComboBox(self)
        self.conversion_type.addItems(["Hex to Little Endian Signed Int32", "Hex to Windows (ANSI)"])
        self.conversion_type.currentIndexChanged.connect(self.update_labels)
        center_layout.addWidget(self.conversion_type)

        self.byte_order_label = QLabel("Byte Order", self)
        center_layout.addWidget(self.byte_order_label)

        self.byte_order_group = QButtonGroup(self)
        little_endian_radio = QRadioButton("Little-endian", self)
        big_endian_radio = QRadioButton("Big-endian", self)
        little_endian_radio.setChecked(True)

        self.byte_order_group.addButton(little_endian_radio)
        self.byte_order_group.addButton(big_endian_radio)

        center_layout.addWidget(little_endian_radio)
        center_layout.addWidget(big_endian_radio)

        convert_button = QPushButton("Convert", self)
        convert_button.clicked.connect(self.convert)
        center_layout.addWidget(convert_button)

        dark_mode_button = QPushButton("Toggle Dark Mode", self)
        dark_mode_button.clicked.connect(self.toggle_dark_mode)
        center_layout.addWidget(dark_mode_button)

        clipboard_button = QPushButton("Copy to Clipboard", self)
        clipboard_button.clicked.connect(self.copy_to_clipboard)
        center_layout.addWidget(clipboard_button)

        clear_button = QPushButton("Clear", self)
        clear_button.clicked.connect(self.clear_fields)
        center_layout.addWidget(clear_button)

        # Right Column - Output
        right_frame = QFrame(self)
        right_frame.setFrameShape(QFrame.Box)
        right_layout = QVBoxLayout(right_frame)
        
        self.result_label = QLabel("Converted Result", self)
        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(True)
        right_layout.addWidget(self.result_label)
        right_layout.addWidget(self.result_output)

        # Add columns to the main layout
        main_layout.addWidget(left_frame)
        main_layout.addWidget(center_frame)
        main_layout.addWidget(right_frame)

        self.setCentralWidget(central_widget)
        self.setWindowTitle("Hex Converter & Encoder")
        self.resize(800, 400)  # Initial size
        
        # Create a menu bar
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        help_menu = menubar.addMenu("Help")
        help_action = QAction("About", self)
        help_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(help_action)

    def format_hex_input(self):
        """
        Auto-format the hex input by grouping into 4 bytes (8 characters).
        """
        text = self.hex_input.toPlainText().replace(" ", "").upper()
        formatted_text = " ".join(text[i:i+8] for i in range(0, len(text), 8))
        self.hex_input.blockSignals(True)  # Prevent recursive signal
        self.hex_input.setPlainText(formatted_text)
        self.hex_input.moveCursor(QTextCursor.End)
        self.hex_input.blockSignals(False)  # Re-enable signal

    def show_about_dialog(self):
        about_text = (
            "Hex Converter Encoder\n"
            "Version 1.0\n\n"
            "Converts and encodes data to and from hexadecimal format."
        )
        QMessageBox.about(self, "About", about_text)
    
    def update_labels(self):
        # Update labels based on the selected conversion type
        conversion = self.conversion_type.currentText()
        if conversion == "Hex to Little Endian Signed Int32":
            self.hex_input_label.setText("Hexadecimal Input")
            self.result_label.setText("Converted Integer")
            self.byte_order_label.show()
            for button in self.byte_order_group.buttons():
                button.show()
        elif conversion == "Hex to Windows (ANSI)":
            self.hex_input_label.setText("Hexadecimal Input")
            self.result_label.setText("Converted ANSI String")
            self.byte_order_label.hide()
            for button in self.byte_order_group.buttons():
                button.hide()

    def convert(self):
        try:
            hex_value = self.hex_input.toPlainText().strip()

            # Normalize input: remove spaces
            hex_value = hex_value.replace(" ", "").upper()

            conversion = self.conversion_type.currentText()
            byte_order = '<' if self.byte_order_group.buttons()[0].isChecked() else '>'

            if conversion == "Hex to Little Endian Signed Int32":
                # Ensure the string is 8 characters long
                if len(hex_value) != 8:
                    raise ValueError("Hexadecimal input must be 8 characters long after normalization.")
                # Convert to little-endian or big-endian signed 32-bit integer
                packed = bytes.fromhex(hex_value)
                little_endian_int = struct.unpack(f'{byte_order}i', packed)[0]
                self.result_output.setText(f"{little_endian_int}")

            elif conversion == "Hex to Windows (ANSI)":
                # Convert hex to ANSI string
                ansi_string = bytes.fromhex(hex_value).decode('cp1252')
                self.result_output.setText(ansi_string)

        except (ValueError, struct.error, UnicodeDecodeError) as e:
            self.result_output.setText(f"Error: {str(e)}")

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.result_output.toPlainText())

    def clear_fields(self):
        self.hex_input.clear()
        self.result_output.clear()

    def toggle_dark_mode(self):
        dark_mode = self.palette().color(self.backgroundRole()) == QColor(Qt.black)
        if dark_mode:
            # Switch to light mode
            self.setStyleSheet("")
        else:
            # Switch to dark mode
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; color: #ffebcd; }
                QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
                QLabel { color: #ffebcd; }
                QPushButton { background-color: #4d4d4d; color: #ffebcd; }
                QComboBox { background-color: #4d4d4d; color: #ffebcd; }
                QRadioButton { color: #ffebcd; }
            """)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    converter = HexConverterEncoder()
    converter.show()
    sys.exit(app.exec_())
