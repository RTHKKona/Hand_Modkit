# Hex Converter Encoder/Decoder module
# Version management
VERSION = "1.0.5"

import sys
import struct
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QWidget, 
    QApplication, QComboBox, QRadioButton, QButtonGroup, QFrame, QAction, QMenuBar, QMessageBox
)
from PyQt5.QtGui import QTextCursor


class HexConverterEncoder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Dark Mode Initialized
        self.init_ui()

    def init_ui(self):
        self.apply_stylesheet()  # Apply initial theme
        central_widget = QWidget(self)
        main_layout = QHBoxLayout(central_widget)

        # Left Column - Input
        left_frame = QFrame(self)
        left_frame.setFrameShape(QFrame.Box)
        left_layout = QVBoxLayout(left_frame)

        self.hex_input_label = QLabel("Hexadecimal Input", self)
        self.hex_input = QTextEdit(self)
        self.hex_input.setPlaceholderText("Enter hexadecimal value in 4-byte format (e.g., f09f8fb3 efb88fe2).")
        self.hex_input.textChanged.connect(self.format_hex_input)  # Auto format input
        left_layout.addWidget(self.hex_input_label)
        left_layout.addWidget(self.hex_input)

        # Center Column - Settings
        center_frame = QFrame(self)
        center_frame.setFrameShape(QFrame.Box)
        center_layout = QVBoxLayout(center_frame)

        self.settings_label = QLabel("Conversion Settings", self)
        center_layout.addWidget(self.settings_label)

        self.conversion_type = QComboBox(self)
        self.conversion_type.addItems([
            "Hex to Signed Int32",
            "Hex to Windows (ANSI)",
            "Signed Int32 to Hex",
            "Windows (ANSI) to Hex"
        ])
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

        # Buttons
        convert_button = QPushButton("Convert", self)
        convert_button.clicked.connect(self.convert)
        center_layout.addWidget(convert_button)

        theme_button = QPushButton("Toggle Theme", self)
        theme_button.clicked.connect(self.toggle_dark_mode)
        center_layout.addWidget(theme_button)

        clipboard_button = QPushButton("Copy to Clipboard", self)
        clipboard_button.clicked.connect(self.copy_to_clipboard)
        center_layout.addWidget(clipboard_button)

        paste_button = QPushButton("Paste from Clipboard", self)
        paste_button.clicked.connect(self.paste_from_clipboard)
        center_layout.addWidget(paste_button)

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

    def apply_stylesheet(self):
        dark_style = """
            QMainWindow { 
                background-color: #2b2b2b; 
                color: #ffebcd; 
                font-family: Consolas; 
                font-size: 11pt; 
                }
                
            QTextEdit, QPushButton, QComboBox { 
                background-color: #4d4d4d; 
                color: #ffebcd; 
                font-family: Consolas; 
                font-size: 11pt; 
                font-weight: bold;
                }
            QPushButton {
                border: 2px solid #ffebcd;
                border-style: outset;
                margin:  5px;
                padding: 3px;
            }
            QPushButton::hover {
                background-color: #ffebcd;
                color: #000000;
                border-style: inset;
                }
            QLabel, QRadioButton {
                color: #ffebcd;
                font-family: Consolas;
                font-size: 11pt;
                }
        """
        light_style = """
            QMainWindow {
                background-color: #ffffff;
                color: #000000;
                font-family: Consolas;
                font-size: 11pt;
                }
            QTextEdit, QPushButton, QComboBox {
                background-color: #d9d9d9;
                color: #000000;
                font-family: Consolas; 
                font-weight: bold;
                font-size: 11pt;
                }
            QPushButton {
                border:  2px solid #cacaca;
                border-style: outset;
                margin:  5px;
                padding:  3px;

            }
            QPushButton::hover,QPushButton::pressed, QRadioButton::hover{
                background-color: #cacaca;
                border-style: inset;
            }
            QLabel, QRadioButton {
                color: #000000;
                font-family: Consolas;
                font-size: 11pt;
                }
        """
        self.setStyleSheet(dark_style if self.dark_mode else light_style)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_stylesheet()

    def format_hex_input(self):
        # Auto-format hex input in 4-byte groups
        text = self.hex_input.toPlainText().replace(" ", "").upper()
        formatted_text = " ".join(text[i:i+8] for i in range(0, len(text), 8))
        self.hex_input.blockSignals(True)  # Prevent recursive signal
        self.hex_input.setPlainText(formatted_text)
        self.hex_input.moveCursor(QTextCursor.End)
        self.hex_input.blockSignals(False)  # Re-enable signal

    def show_about_dialog(self):
        about_text = f"Hex Converter Encoder\nVersion {VERSION}\nConverts and encodes data to/from hexadecimal format."
        QMessageBox.about(self, "About", about_text)

    def update_labels(self):
        # Update labels based on conversion type
        conversion = self.conversion_type.currentText()
        if conversion in ["Hex to Signed Int32", "Signed Int32 to Hex"]:
            self.byte_order_label.show()
            for button in self.byte_order_group.buttons():
                button.show()
        else:
            self.byte_order_label.hide()
            for button in self.byte_order_group.buttons():
                button.hide()

        if conversion in ["Hex to Signed Int32", "Hex to Windows (ANSI)"]:
            self.hex_input_label.setText("Hexadecimal Input")
        elif conversion == "Signed Int32 to Hex":
            self.hex_input_label.setText("Signed Int32 Input")
        else:
            self.hex_input_label.setText("ANSI String Input")

        if conversion == "Signed Int32 to Hex":
            self.hex_input.setPlaceholderText("Enter signed int32 value (e.g., -123456789)")
        elif conversion == "Windows (ANSI) to Hex":
            self.hex_input.setPlaceholderText("Enter ANSI string (e.g., Hello World)")
        else:
            self.hex_input.setPlaceholderText("Enter hexadecimal value (e.g., f09f8fb3 efb88fe2).")

    def convert(self):
        try:
            input_value = self.hex_input.toPlainText().strip()
            conversion = self.conversion_type.currentText()
            byte_order = '<' if self.byte_order_group.buttons()[0].isChecked() else '>'

            if conversion == "Hex to Signed Int32":
                if len(input_value) != 8:
                    raise ValueError("Hex input must be 8 characters long.")
                packed = bytes.fromhex(input_value)
                result = struct.unpack(f'{byte_order}i', packed)[0]
                self.result_output.setText(str(result))

            elif conversion == "Hex to Windows (ANSI)":
                result = bytes.fromhex(input_value).decode('cp1252')
                self.result_output.setText(result)

            elif conversion == "Signed Int32 to Hex":
                int_value = int(input_value)
                packed = struct.pack(f'{byte_order}i', int_value)
                self.result_output.setText(packed.hex().upper())

            elif conversion == "Windows (ANSI) to Hex":
                result = input_value.encode('cp1252').hex().upper()
                self.result_output.setText(result)

        except (ValueError, struct.error, UnicodeDecodeError) as e:
            self.result_output.setText(f"Error: {str(e)}")

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.result_output.toPlainText())

    def paste_from_clipboard(self):
        clipboard = QApplication.clipboard()
        self.hex_input.setText(clipboard.text())

    def clear_fields(self):
        self.hex_input.clear()
        self.result_output.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    converter = HexConverterEncoder()
    converter.show()
    sys.exit(app.exec_())
