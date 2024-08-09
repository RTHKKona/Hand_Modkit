import sys
import struct
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QAction, QLabel, QDialog, QHBoxLayout, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QColor
from PyQt5.QtCore import Qt, QRect

class STQReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.dark_mode = False
        self.loaded_file_name = ""

    def setup_ui(self):
        self.setWindowTitle("STQ Reader Tool")
        self.setGeometry(100, 100, 900, 600)
        self.setWindowIcon(QIcon("C:/Users/necro/Downloads/MHGU_Modding/Audio/MHGU-STQReader/egg.png"))

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Background egg image setup
        self.background_label = QLabel(main_widget)
        egg_pixmap = QPixmap("C:/Users/necro/Downloads/MHGU_Modding/Audio/MHGU-STQReader/egg.png")
        self.background_label.setPixmap(egg_pixmap.scaled(300, 300, Qt.KeepAspectRatio))
        self.background_label.setAlignment(Qt.AlignCenter)
        self.background_label.setGeometry(QRect((self.width() - 300) // 2, (self.height() - 300) // 2, 300, 300))
        self.background_label.setVisible(True)

        self.text_edit = self.create_text_edit(read_only=True)
        self.raw_stq_data = self.create_text_edit(read_only=True)
        self.data_grid = self.create_data_grid()

        main_layout.addWidget(self.text_edit)
        main_layout.addWidget(self.raw_stq_data)
        main_layout.addWidget(self.data_grid)

        control_layout = self.create_control_buttons()
        main_layout.addLayout(control_layout)

        self.setup_menu()

    def create_text_edit(self, read_only=False):
        text_edit = QTextEdit(self)
        text_edit.setFont(QFont("Consolas", 10))
        text_edit.setReadOnly(read_only)
        return text_edit

    def create_data_grid(self):
        grid = QTableWidget(self)
        grid.setColumnCount(8)
        grid.setHorizontalHeaderLabels([
            "Size of File (samples)",
            "Number of Samples",
            "Number of Channels",
            "Sample Rate Hz",
            "Loop Start (samples)",
            "Loop End (samples)",
            "LINK",
            "File Name"
        ])
        grid.horizontalHeader().setFont(QFont("Arial", weight=QFont.Bold))
        return grid

    def create_control_buttons(self):
        layout = QHBoxLayout()

        buttons = [
            ("Load .stqr File", self.load_file),
            ("Hex to Dec Converter", self.hex_dec_converter),
            ("Search Pattern", self.search_pattern),
            ("Export RawSTQData", self.export_raw_stq_data),
            ("Clear", self.clear_data),
            ("Toggle Dark/Light Mode", self.toggle_theme)
        ]

        for label, callback in buttons:
            button = QPushButton(label, self)
            button.clicked.connect(callback)
            layout.addWidget(button)

        self.pattern_search_button = layout.itemAt(2).widget()
        self.pattern_search_button.setEnabled(False)

        return layout

    def setup_menu(self):
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        menubar = self.menuBar()
        about_menu = menubar.addMenu("Help")
        about_menu.addAction(about_action)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.setStyleSheet("background-color: black; color: white;" if self.dark_mode else "")
        self.text_edit.setStyleSheet("background-color: black; color: white;" if self.dark_mode else "")
        self.raw_stq_data.setStyleSheet("background-color: black; color: white;" if self.dark_mode else "")
        self.set_button_styles()

    def set_button_styles(self):
        button_style = ("QPushButton {"
                        "border: 1px solid %s; "
                        "color: %s; "
                        "background-color: %s; "
                        "font-size: 14px;"
                        "font-family: Arial, sans-serif;"
                        "padding: 5px 10px;}")

        border_color, text_color, bg_color = (
            ("#FFE4B5", "white", "black") if self.dark_mode else
            ("lightgray", "black", "white")
        )

        self.setStyleSheet(button_style % (border_color, text_color, bg_color))

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open .stqr File", "", "STQ Files (*.stqr);;All Files (*)")
        if file_name:
            self.loaded_file_name = file_name
            with open(file_name, 'rb') as file:
                content = file.read()

                if content[:4] != b'STQR':
                    self.text_edit.setText("Error: The file is not a valid .stqr file.")
                    return

                self.text_edit.setText(self.format_hex(content))
                self.pattern_search_button.setEnabled(True)

    def format_hex(self, content):
        hex_str = content.hex().upper()
        bytes_per_row = 36
        return '\n'.join(
            ' '.join(hex_str[i:i + 8] for i in range(start, start + bytes_per_row * 2, 8))
            for start in range(0, len(hex_str), bytes_per_row * 2)
        )

    def hex_dec_converter(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Hexadecimal to Decimal Converter")
        dialog.setGeometry(200, 200, 300, 100)
        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Input 8-character Hexadecimal (Little Endian):", dialog))
        hex_input = QTextEdit(dialog)
        hex_input.setFixedHeight(30)
        layout.addWidget(hex_input)

        dec_output = QLabel("", dialog)
        layout.addWidget(dec_output)

        convert_button = QPushButton("Convert", dialog)
        convert_button.clicked.connect(lambda: self.convert_hex_to_dec(hex_input, dec_output))
        layout.addWidget(convert_button)

        dialog.exec_()

    def convert_hex_to_dec(self, hex_input, dec_output):
        hex_value = hex_input.toPlainText().strip()
        if len(hex_value) == 8:
            try:
                little_endian_bytes = bytes.fromhex(hex_value)
                decimal_value = struct.unpack('<i', little_endian_bytes)[0]
                dec_output.setText(f"Decimal: {decimal_value}")
            except ValueError:
                dec_output.setText("Invalid hexadecimal input")
        else:
            dec_output.setText("Hex value must be 8 characters")

    def search_pattern(self):
        content = self.text_edit.toPlainText().replace(' ', '').replace('\n', '')
        pattern = "XXXXXXXX XXXXXXXX 02000000 80BB0000 XXXXXXXX XXXXXXXX"
        pattern_length = len(pattern.replace(' ', ''))

        raw_data_list = []
        for index in range(0, len(content) - pattern_length, 2):
            match = content[index:index + pattern_length]
            if self.pattern_matches(match):
                end_hex = content[index + pattern_length:index + pattern_length + 48]
                if len(end_hex) == 48:
                    raw_data_list.append(match + end_hex)
        
        self.raw_stq_data.setText('\n'.join(raw_data_list))
        self.populate_grid(raw_data_list, content)
        self.pattern_search_button.setEnabled(False)

    def pattern_matches(self, match):
        pattern = "XXXXXXXX XXXXXXXX 02000000 80BB0000 XXXXXXXX XXXXXXXX"
        return all(c == 'X' or c == m for c, m in zip(pattern.replace(' ', ''), match))

    def populate_grid(self, raw_data_list, full_content):
        self.data_grid.setRowCount(len(raw_data_list))

        for row_idx, data in enumerate(raw_data_list):
            parts = [self.convert_hex_to_int(data[i:i+8]) for i in range(0, len(data), 8)]
            for col_idx, part in enumerate(parts):
                self.data_grid.setItem(row_idx, col_idx, QTableWidgetItem(str(part)))

            # Extracting text after "736F756E64"
            if "736F756E64" in full_content:
                text_start = full_content.index("736F756E64") + len("736F756E64")
                text_data = self.hex_to_text(full_content[text_start:])
                link, file_name = self.split_text_data(text_data)
                self.data_grid.setItem(row_idx, 6, QTableWidgetItem(link))
                self.data_grid.setItem(row_idx, 7, QTableWidgetItem(file_name))

    def convert_hex_to_int(self, hex_str):
        little_endian_bytes = bytes.fromhex(hex_str)
        return struct.unpack('<i', little_endian_bytes)[0]

    def hex_to_text(self, hex_data):
        # Convert hex to ASCII text
        bytes_data = bytes.fromhex(hex_data)
        try:
            return bytes_data.decode('ascii')
        except UnicodeDecodeError:
            return bytes_data.decode('latin-1')

    def split_text_data(self, text_data):
        parts = text_data.split('.')
        link = parts[0] + "\\" if parts else ""
        file_name = parts[1] if len(parts) > 1 else ""
        return link, file_name

    def clear_data(self):
        if QMessageBox.question(self, 'Clear Data', "Are you sure you want to clear all data?",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.text_edit.clear()
            self.raw_stq_data.clear()
            self.data_grid.clearContents()
            self.data_grid.setRowCount(0)
            self.pattern_search_button.setEnabled(False)

    def export_raw_stq_data(self):
        if not self.loaded_file_name:
            file_name = "RawSTQData.txt"
        else:
            base_name = self.loaded_file_name.split('/')[-1].rsplit('.', 1)[0]
            file_name = f"{base_name}.txt"

        file_name, _ = QFileDialog.getSaveFileName(self, "Save RawSTQData", file_name, "Text Files (*.txt);;All Files (*)")
        if file_name:
            formatted_data = self.format_raw_stq_data(self.raw_stq_data.toPlainText())
            with open(file_name, 'w') as file:
                file.write(formatted_data)

    def format_raw_stq_data(self, data):
        parts = data.split('\n')
        formatted_parts = ['|'.join(part[i:i+8] for i in range(0, len(part), 8)) for part in parts]
        return '\n'.join(formatted_parts)

    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout(dialog)

        layout.addWidget(self.create_icon_label("C:/Users/necro/Downloads/MHGU_Modding/Audio/MHGU-STQReader/egg.png", 100))
        layout.addLayout(self.create_link_layout("C:/Users/necro/Downloads/MHGU_Modding/Audio/MHGU-STQReader/github.png",
                                                 "Github - RTHKKona", "https://github.com/RTHKKona", 64))
        layout.addLayout(self.create_link_layout("C:/Users/necro/Downloads/MHGU_Modding/Audio/MHGU-STQReader/ko-fi.png",
                                                 "Ko-Fi - Handburger", "https://ko-fi.com/handburger", 64))
        close_button = QPushButton("Close", dialog)
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.exec_()

    def create_icon_label(self, icon_path, size):
        label = QLabel(self)
        pixmap = QPixmap(icon_path)
        label.setPixmap(pixmap.scaled(size, size, Qt.KeepAspectRatio))
        return label

    def create_link_layout(self, icon_path, text, url, icon_size):
        layout = QHBoxLayout()
        layout.addWidget(self.create_icon_label(icon_path, icon_size))
        link_label = QLabel(f'<a href="{url}">{text}</a>', self)
        link_label.setOpenExternalLinks(True)
        layout.addWidget(link_label)
        return layout

if __name__ == "__main__":
    app = QApplication(sys.argv)
    reader = STQReader()
    reader.show()
    sys.exit(app.exec_())
