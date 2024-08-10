import sys
import struct
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel, QDialog, QHBoxLayout, QMessageBox, QSizePolicy, QAction, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QRect

class STQReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.loaded_file_name = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Handburger's STQ Reader Tool")
        self.setGeometry(100, 100, 1200, 800)  # Adjusted size for better splitting and visibility
        self.setWindowIcon(QIcon(self.get_resource_path("egg.png")))

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Splitter for window resizing
        splitter = QSplitter(Qt.Vertical, main_widget)

        # Faint foreground egg image setup
        self.background_label = QLabel(main_widget)
        egg_pixmap = QPixmap(self.get_resource_path("egg.png"))
        egg_pixmap = egg_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.background_label.setPixmap(egg_pixmap)
        self.background_label.setGeometry(QRect(self.width() - 220, 10, 200, 200))  # Positioned at the top right
        self.background_label.setStyleSheet("opacity: 0.15;")  # Faint but visible
        self.background_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.background_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.background_label.hide()  # Initially hide the egg
        self.background_label.raise_()  # Ensure the label stays in the foreground

        # Text editor for raw hexadecimal data
        self.text_edit = QTextEdit(self, readOnly=True, font=QFont("Consolas", 10))
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.text_edit.setStyleSheet("background-color: rgba(255, 255, 255, 0.8);")

        # Table for grid data
        self.data_grid = self.create_data_grid()

        # Add widgets to splitter
        splitter.addWidget(self.text_edit)
        splitter.addWidget(self.data_grid)

        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(splitter)
        self.buttons = self.create_buttons()  # Keep a reference to the buttons for style changes
        main_layout.addLayout(self.buttons)

        self.setup_menu()
        self.apply_styles()  # Apply initial styles

    def create_data_grid(self):
        grid = QTableWidget(self)
        grid.setColumnCount(7)
        grid.setHorizontalHeaderLabels([
            "File Directory",  # Updated header
            "Size of File (bytes)",  # Updated header
            "Number of Samples",
            "Number of Channels",
            "Sample Rate Hz",
            "Loop Start (samples)",
            "Loop End (samples)"
        ])
        grid.horizontalHeader().setFont(QFont("Arial", weight=QFont.Bold))
        grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)  # Resize columns to contents initially
        grid.horizontalHeader().sectionDoubleClicked.connect(self.resize_column_to_contents)
        grid.horizontalHeader().setStyleSheet("color: black")
        grid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        grid.setEditTriggers(QTableWidget.DoubleClicked)  # Allow editing on double-click
        return grid

    def resize_column_to_contents(self, index):
        # Resize the column to fit its contents perfectly
        self.data_grid.resizeColumnToContents(index)
        
        # Ensure the column does not exceed the screen width
        available_width = self.data_grid.viewport().width()
        column_width = self.data_grid.columnWidth(index)
        
        if column_width > available_width:
            self.data_grid.setColumnWidth(index, available_width)

    def create_buttons(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 20, 0, 20)  # 20px margin above and below the button area
        buttons = [
            ("Load .stqr File", self.load_file),
            ("Search Patterns", self.search_patterns),
            ("Save Changes", self.save_changes),  # New button to save changes
            ("Clear", self.clear_data),
            ("Toggle Dark/Light Mode", self.toggle_theme),
            ("Increase Header Size", self.increase_header_size),
            ("Decrease Header Size", self.decrease_header_size)
        ]

        button_widgets = []

        for label, callback in buttons:
            button = QPushButton(label, self)
            button.clicked.connect(callback)
            button.setStyleSheet(
                "border: 1px solid black; color: black; padding-top: 10px; padding-bottom: 10px; text-align: center; font-weight: bold;"
            )  # Padding to create space above and below the text, and bold font
            layout.addWidget(button)
            button_widgets.append(button)

        self.pattern_search_button = layout.itemAt(1).widget()
        self.pattern_search_button.setEnabled(False)

        return layout

    def setup_menu(self):
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        menubar = self.menuBar()
        menubar.addMenu("Help").addAction(about_action)

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open .stqr File", "", "STQ Files (*.stqr);;All Files (*)")
        if file_name:
            self.loaded_file_name = file_name
            self.setWindowTitle(f"Handburger's STQ Reader Tool - Editing {os.path.basename(file_name)}")
            with open(file_name, 'rb') as file:
                content = file.read()
                if content[:4] != b'STQR':
                    self.text_edit.setText("Error: The file is not a valid .stqr file.")
                else:
                    self.text_edit.setText(self.format_hex(content))
                    self.pattern_search_button.setEnabled(True)

                    # Show egg.png with 20% probability
                    if random.random() < 0.2:
                        self.background_label.show()
                    else:
                        self.background_label.hide()

    def format_hex(self, content):
        hex_str = content.hex().upper()
        return '\n'.join(
            ' '.join(hex_str[i:i + 8] for i in range(start, start + 36 * 2, 8))
            for start in range(0, len(hex_str), 36 * 2)
        )

    def search_patterns(self):
        # Disable the search button after pressing
        self.pattern_search_button.setEnabled(False)
        
        content = self.text_edit.toPlainText().replace(' ', '').replace('\n', '')
        self.text_edit.clear()
        self.data_grid.clearContents()
        self.data_grid.setRowCount(0)

        # First pattern: "XXXXXXXX XXXXXXXX 02000000 80BB0000 XXXXXXXX XXXXXXXX"
        pattern1 = "XXXXXXXX XXXXXXXX 02000000 80BB0000 XXXXXXXX XXXXXXXX".replace(' ', '')
        for index in range(0, len(content) - len(pattern1), 2):
            match = content[index:index + len(pattern1)]
            if self.pattern_matches(match, pattern1):
                window_data = content[index:index + 48]
                self.text_edit.append(self.format_hex(bytes.fromhex(window_data)))

                # Add window data to grid
                self.populate_grid(window_data)

        self.text_edit.append("\n")  # Line break between pattern outputs

        # Second pattern: All data starting from "00000000 00000000 736F756E64"
        start_pattern = "0000000000000000736F756E64"
        start_index = content.find(start_pattern)
        if start_index != -1:
            windows_data = content[start_index + len(start_pattern):]  # Skip the start pattern itself

            digit_count = 0
            buffer = ""

            while windows_data:
                # Take 2 digits at a time
                part = windows_data[:2]
                windows_data = windows_data[2:]

                # Check if we encounter "00"
                if part == "00":
                    if digit_count >= 8:
                        try:
                            # Decode buffer as ANSI
                            decoded_part = bytes.fromhex(buffer).decode('ansi')
                            self.text_edit.append(decoded_part)
                            self.append_to_title_column(decoded_part)  # Add the decoded part to the "File Directory" column
                        except (ValueError, UnicodeDecodeError):
                            pass
                    # Reset count and buffer
                    digit_count = 0
                    buffer = ""
                else:
                    # Accumulate the hex digits and increase count
                    buffer += part
                    digit_count += 2

    def append_to_title_column(self, text):
        # Find the "File Directory" column index
        title_column_index = 0  # The first column is "File Directory"
        
        # Start appending text to the first available row in the "File Directory" column
        row_count = self.data_grid.rowCount()
        
        for row in range(row_count):
            item = self.data_grid.item(row, title_column_index)
            if item is None or item.text() == "":
                self.data_grid.setItem(row, title_column_index, QTableWidgetItem(text))
                break

    def pattern_matches(self, match, pattern):
        return all(c == 'X' or c == m for c, m in zip(pattern, match))

    def populate_grid(self, hex_data):
        row_position = self.data_grid.rowCount()
        self.data_grid.insertRow(row_position)

        # Populate grid with decoded integer values from hex_data in little-endian format
        for i in range(0, len(hex_data), 8):
            value = struct.unpack('<i', bytes.fromhex(hex_data[i:i + 8]))[0]
            self.data_grid.setItem(row_position, i // 8 + 1, QTableWidgetItem(str(value)))

    def clear_data(self):
        if QMessageBox.question(self, 'Clear Data', "Are you sure you want to clear all data?",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.text_edit.clear()
            self.data_grid.clearContents()
            self.data_grid.setRowCount(0)
            self.setWindowTitle("Handburger's STQ Reader Tool")  # Reset the title
            self.pattern_search_button.setEnabled(True)  # Re-enable the search button
            self.background_label.hide()  # Hide the egg if it was shown

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_styles()

    def apply_styles(self):
        if self.dark_mode:
            style = "background-color: black; color: white;"
            button_style = "border: 1px solid white; color: white; padding-top: 10px; padding-bottom: 10px; font-weight: bold;"
        else:
            style = "background-color: white; color: black;"
            button_style = "border: 1px solid black; color: black; padding-top: 10px; padding-bottom: 10px; font-weight: bold;"

        self.setStyleSheet(style)
        self.text_edit.setStyleSheet(style)
        for i in range(self.buttons.count()):
            self.buttons.itemAt(i).widget().setStyleSheet(button_style)

    def increase_header_size(self):
        header_font = self.data_grid.horizontalHeader().font()
        header_font.setPointSize(header_font.pointSize() + 1)
        self.data_grid.horizontalHeader().setFont(header_font)

    def decrease_header_size(self):
        header_font = self.data_grid.horizontalHeader().font()
        header_font.setPointSize(header_font.pointSize() - 1)
        self.data_grid.horizontalHeader().setFont(header_font)

    def save_changes(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save STQR File", "", "STQ Files (*.stqr);;All Files (*)")
        if file_name:
            with open(file_name, 'wb') as file:
                # Gather data from the grid to save to the file
                for row in range(self.data_grid.rowCount()):
                    row_data = []
                    for col in range(self.data_grid.columnCount()):
                        item = self.data_grid.item(row, col)
                        if item:
                            row_data.append(item.text())
                        else:
                            row_data.append("")
                    # Convert the row data back to binary format and write to the file
                    # This is just an example; adjust this as needed for your specific file format.
                    file.write(self.convert_row_to_binary(row_data))

    def convert_row_to_binary(self, row_data):
        # Example conversion of row data to binary format
        binary_data = b""
        for data in row_data:
            # Convert each string to binary; this needs to be adjusted to your specific format
            binary_data += data.encode('ascii') + b'\x00'
        return binary_data

    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout(dialog)

        about_label = QLabel(self.create_about_text(), self)
        about_label.setFont(QFont("Arial", 12))  # Increased font size
        layout.addWidget(self.create_icon_label(self.get_resource_path("egg.png"), 100))
        layout.addWidget(about_label)
        layout.addLayout(self.create_link_layout(self.get_resource_path("github.png"),
                                                 "Github - RTHKKona", "https://github.com/RTHKKona", 64))
        layout.addLayout(self.create_link_layout(self.get_resource_path("ko-fi.png"),
                                                 "Ko-Fi - Handburger", "https://ko-fi.com/handburger", 64))
        close_button = QPushButton("Close", dialog)
        close_button.clicked.connect(dialog.close)
        close_button.setStyleSheet("border: 1px solid white; color: black;")
        layout.addWidget(close_button)

        dialog.exec_()

    def create_about_text(self):
        return (
            "Handburger's STQ Reader Tool\n"
            "Version 1.0\n\n"
            "This tool is designed for analyzing and reading .stqr files, providing a comprehensive interface for examining hexadecimal data.\n"
        )

    def create_icon_label(self, icon_path, size):
        label = QLabel(self)
        label.setPixmap(QPixmap(icon_path).scaled(size, size, Qt.KeepAspectRatio))
        return label

    def create_link_layout(self, icon_path, text, url, icon_size):
        layout = QHBoxLayout()
        layout.addWidget(self.create_icon_label(icon_path, icon_size))
        link_label = QLabel(f'<a href="{url}">{text}</a>', self)
        link_label.setOpenExternalLinks(True)
        link_label.setFont(QFont("Arial", 12))  # Increase font size for hyperlinks
        link_label.setStyleSheet("color: white;")
        layout.addWidget(link_label)
        return layout

    def get_resource_path(self, filename):
        return os.path.join(os.getcwd(), filename)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    reader = STQReader()
    reader.show()
    sys.exit(app.exec_())
