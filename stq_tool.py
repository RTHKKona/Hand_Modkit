import sys
import struct
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QAction, QLabel, QDialog, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QTextCursor, QColor, QPalette, QBrush
from PyQt5.QtCore import Qt

class STQReader(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the window title and dimensions
        self.setWindowTitle("STQ Reader Tool")
        self.setGeometry(100, 100, 900, 600)
        self.setWindowIcon(QIcon("C:/Users/necro/Downloads/MHGU_Modding/Audio/MHGU-STQReader/egg.png"))

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 10, 10, 10)  # Small left offset

        # Text display area
        self.text_edit = QTextEdit(self)
        self.text_edit.setFont(QFont("Consolas", 10))  # Monospaced font for alignment
        self.text_edit.setReadOnly(True)
        self.text_edit.setWordWrapMode(False)
        main_layout.addWidget(self.text_edit)

        # Separate text box for RawSTQData
        self.raw_stq_data = QTextEdit(self)
        self.raw_stq_data.setFont(QFont("Consolas", 10))
        self.raw_stq_data.setReadOnly(True)
        main_layout.addWidget(self.raw_stq_data)

        # Overlay QLabel for the image
        self.egg_label = QLabel(self.text_edit)
        self.egg_pixmap = QPixmap("C:/Users/necro/Downloads/MHGU_Modding/Audio/MHGU-STQReader/egg.png")
        self.egg_label.setPixmap(self.egg_pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        self.egg_label.setAlignment(Qt.AlignCenter)
        self.egg_label.setGeometry(self.rect().center().x() - 100, self.rect().center().y() - 100, 200, 200)
        self.egg_label.setVisible(False)

        # Load file button
        load_button = QPushButton("Load .stqr File", self)
        load_button.clicked.connect(self.load_file)
        main_layout.addWidget(load_button)

        # Control buttons for text size
        control_layout = QHBoxLayout()
        increase_button = QPushButton("Ctrl +", self)
        increase_button.clicked.connect(self.increase_text_size)
        control_layout.addWidget(increase_button)

        decrease_button = QPushButton("Ctrl -", self)
        decrease_button.clicked.connect(self.decrease_text_size)
        control_layout.addWidget(decrease_button)

        main_layout.addLayout(control_layout)

        # Hexadecimal to decimal conversion tool
        hex_dec_button = QPushButton("Hex to Dec Converter", self)
        hex_dec_button.clicked.connect(self.hex_dec_converter)
        main_layout.addWidget(hex_dec_button)

        # Pattern search button
        self.pattern_search_button = QPushButton("Search Pattern", self)
        self.pattern_search_button.clicked.connect(self.search_pattern)
        self.pattern_search_button.setEnabled(False)  # Initially disabled
        main_layout.addWidget(self.pattern_search_button)

        # Clear button with confirmation prompt
        clear_button = QPushButton("Clear", self)
        clear_button.clicked.connect(self.clear_data)
        main_layout.addWidget(clear_button)

        # Theme toggle
        theme_toggle_button = QPushButton("Toggle Dark/Light Mode", self)
        theme_toggle_button.clicked.connect(self.toggle_theme)
        self.dark_mode = False
        main_layout.addWidget(theme_toggle_button)

        # Set the static button styles
        self.set_button_styles()

        # About tab
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        menubar = self.menuBar()
        about_menu = menubar.addMenu("Help")
        about_menu.addAction(about_action)

        # Finally, Chinese hamster line
        hamster_label = QLabel("Finally, Chinese hamster.", self)
        hamster_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        main_layout.addWidget(hamster_label)

        # Show placeholder image initially
        self.show_placeholder_image()

    def set_button_styles(self):
        button_style = ("QPushButton {"
                        "border: 1px solid %s; "
                        "color: %s; "
                        "background-color: %s; "
                        "font-size: 14px;"
                        "font-family: Arial, sans-serif;"
                        "padding: 5px 10px;}")

        if self.dark_mode:
            border_color = "#FFE4B5"  # Manilla
            text_color = "white"
            bg_color = "black"
        else:
            border_color = "lightgray"
            text_color = "black"
            bg_color = "white"

        self.setStyleSheet(button_style % (border_color, text_color, bg_color))

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode

        if self.dark_mode:
            self.setStyleSheet("background-color: black; color: white;")
            self.text_edit.setStyleSheet("background-color: black; color: white;")
            self.raw_stq_data.setStyleSheet("background-color: black; color: white;")
            palette = QPalette()
            palette.setBrush(QPalette.Button, QBrush(QColor("#FFE4B5")))  # Manilla (light beige)
            self.setPalette(palette)
        else:
            self.setStyleSheet("")
            self.text_edit.setStyleSheet("background-color: white; color: black;")
            self.raw_stq_data.setStyleSheet("background-color: white; color: black;")
            palette = QPalette()
            palette.setBrush(QPalette.Button, QBrush(QColor("lightgray")))
            self.setPalette(palette)

        # Update button styles to reflect the new theme, but keep font and size static
        self.set_button_styles()

    def show_placeholder_image(self):
        self.egg_label.setVisible(True)

    def hide_placeholder_image(self):
        self.egg_label.setVisible(False)

    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open .stqr File", "", "STQ Files (*.stqr);;All Files (*)", options=options)
        if file_name:
            with open(file_name, 'rb') as file:
                content = file.read()

                # Verify if the header is "STQR"
                if content[:4] != b'STQR':
                    self.text_edit.setText("Error: The file is not a valid .stqr file.")
                    self.show_placeholder_image()
                    return

                self.hide_placeholder_image()  # Hide the image when file is loaded
                formatted_text = self.format_hex(content)
                self.text_edit.setText(formatted_text)
                self.text_edit.moveCursor(QTextCursor.Start)
                self.pattern_search_button.setEnabled(True)  # Enable search pattern button

    def format_hex(self, content):
        hex_str = content.hex().upper()  # Convert to uppercase hex
        formatted_lines = []
        bytes_per_row = 36  # Each row will contain 36 bytes

        for i in range(0, len(hex_str), bytes_per_row * 2):
            row = hex_str[i:i + bytes_per_row * 2]

            # Create groups of 8 bytes (16 hex characters)
            hex_groups = ' '.join(row[j:j + 8] for j in range(0, len(row), 8))

            # Ensure that the hex groups are aligned properly
            formatted_lines.append(hex_groups)

        return '\n'.join(formatted_lines)

    def increase_text_size(self):
        current_font = self.text_edit.font()
        size = current_font.pointSize() + 2
        current_font.setPointSize(size)
        self.text_edit.setFont(current_font)
        self.raw_stq_data.setFont(current_font)

    def decrease_text_size(self):
        current_font = self.text_edit.font()
        size = current_font.pointSize() - 2
        current_font.setPointSize(size)
        self.text_edit.setFont(current_font)
        self.raw_stq_data.setFont(current_font)

    def hex_dec_converter(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Hexadecimal to Decimal Converter")
        dialog.setGeometry(200, 200, 300, 100)
        layout = QVBoxLayout(dialog)

        label = QLabel("Input 8-character Hexadecimal (Little Endian):", dialog)
        layout.addWidget(label)

        self.hex_input = QTextEdit(dialog)
        self.hex_input.setFixedHeight(30)
        layout.addWidget(self.hex_input)

        convert_button = QPushButton("Convert", dialog)
        convert_button.clicked.connect(self.convert_hex_to_dec)
        layout.addWidget(convert_button)

        self.dec_output = QLabel("", dialog)
        layout.addWidget(self.dec_output)

        dialog.exec_()

    def convert_hex_to_dec(self):
        hex_value = self.hex_input.toPlainText().strip()
        if len(hex_value) == 8:
            try:
                little_endian_bytes = bytes.fromhex(hex_value)
                decimal_value = struct.unpack('<i', little_endian_bytes)[0]
                self.dec_output.setText(f"Decimal: {decimal_value}")
            except ValueError:
                self.dec_output.setText("Invalid hexadecimal input")
        else:
            self.dec_output.setText("Hex value must be 8 characters")

    def search_pattern(self):
        content = self.text_edit.toPlainText().replace(' ', '').replace('\n', '')  # Clean up any spaces or newlines
        pattern = "XXXXXXXX XXXXXXXX 02000000 80BB0000 XXXXXXXX XXXXXXXX"  # Your pattern here
        matches = []
        raw_data = ""
        pattern_length = len(pattern.replace(' ', ''))  # The length of the pattern without spaces
        
        # Loop through the content to find the pattern
        index = 0
        while index <= len(content) - pattern_length:
            match = content[index:index + pattern_length]
            if self.pattern_matches(match):
                # Extract the portion that corresponds to the [24 digits] after the pattern
                end_hex = content[index + pattern_length:index + pattern_length + 48]  # 24 digits = 48 hex characters
                if len(end_hex) == 48:
                    # Append the matched raw data
                    raw_data += match + end_hex + '\n'
                    # Split the extracted value by "."
                    split_values = end_hex.split('.')
                    matches.append(split_values)
                index += pattern_length + 48  # Move past this match
            else:
                index += 2  # Move forward and continue searching

        # Display the matched raw data split into 8-digit segments
        raw_data_segments = ' '.join(raw_data[i:i+8] for i in range(0, len(raw_data), 8))
        self.raw_stq_data.setText(raw_data_segments.strip())

        # Display the results
        self.display_matches(matches)

        # Disable the search button to prevent multiple presses
        self.pattern_search_button.setEnabled(False)

    def pattern_matches(self, match):
        # Replace X's with appropriate checks (assuming we treat X as wildcard)
        pattern = "XXXXXXXX XXXXXXXX 02000000 80BB0000 XXXXXXXX XXXXXXXX"
        for i, char in enumerate(pattern.replace(' ', '')):
            if char != 'X' and match[i] != char:
                return False
        return True

    def display_matches(self, matches):
        result_text = ""
        for match in matches:
            result_text += "{" + "}, {".join(match) + "}\n"
        self.text_edit.setText(result_text)

    def clear_data(self):
        # Confirmation prompt
        reply = QMessageBox.question(self, 'Clear Data', "Are you sure you want to clear all data?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.text_edit.clear()
            self.raw_stq_data.clear()
            self.pattern_search_button.setEnabled(False)

    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout(dialog)

        egg_label = QLabel(dialog)
        egg_pixmap = QPixmap("C:/Users/necro/Downloads/MHGU_Modding/Audio/MHGU-STQReader/egg.png")
        egg_label.setPixmap(egg_pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        layout.addWidget(egg_label)

        # Github link with icon
        github_layout = QHBoxLayout()
        github_icon = QLabel(dialog)
        github_pixmap = QPixmap("C:/Users/necro/Downloads/MHGU_Modding/Audio/MHGU-STQReader/github.png")
        github_icon.setPixmap(github_pixmap.scaled(16, 16, Qt.KeepAspectRatio))
        github_layout.addWidget(github_icon)

        github_link = QLabel('<a href="https://github.com/RTHKKona">Github - RTHKKona</a>', dialog)
        github_link.setOpenExternalLinks(True)
        github_layout.addWidget(github_link)
        layout.addLayout(github_layout)

        # Ko-Fi link with icon
        kofi_layout = QHBoxLayout()
        kofi_icon = QLabel(dialog)
        kofi_pixmap = QPixmap("C:/Users/necro/Downloads/MHGU_Modding/Audio/MHGU-STQReader/ko-fi.png")
        kofi_icon.setPixmap(kofi_pixmap.scaled(16, 16, Qt.KeepAspectRatio))
        kofi_layout.addWidget(kofi_icon)

        kofi_link = QLabel('<a href="https://ko-fi.com/handburger">Ko-Fi - Handburger</a>', dialog)
        kofi_link.setOpenExternalLinks(True)
        kofi_layout.addWidget(kofi_link)
        layout.addLayout(kofi_layout)

        close_button = QPushButton("Close", dialog)
        close_button.clicked.connect(dialog.close)
        layout.addWidget(close_button)

        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    reader = STQReader()
    reader.show()
    sys.exit(app.exec_())
