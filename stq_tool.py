import sys
import struct
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel, QDialog, QHBoxLayout, QMessageBox, QSizePolicy, QAction, QSplitter, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QRect, QEvent

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

        # Faint background egg image setup (top right corner)
        self.background_label = QLabel(main_widget)
        egg_pixmap = QPixmap(self.get_resource_path("egg.png"))
        egg_pixmap = egg_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.background_label.setPixmap(egg_pixmap)
        self.background_label.setStyleSheet("opacity: 0.1;")  # Adjusted to make it faint but visible
        self.background_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.background_label.setGeometry(self.width() - 220, 20, 200, 200)
        self.background_label.lower()

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

        # Update the position of the background_label when the window is resized
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Resize:
            # Reposition the egg image to always be on the top right
            self.background_label.setGeometry(self.width() - 220, 20, 200, 200)
        return super().eventFilter(source, event)

    def create_data_grid(self):
        grid = QTableWidget(self)
        grid.setColumnCount(7)
        grid.setHorizontalHeaderLabels([
            "Title",
            "Size of File (samples)",
            "Number of Samples",
            "Number of Channels",
            "Sample Rate Hz",
            "Loop Start (samples)",
            "Loop End (samples)"
        ])
        grid.horizontalHeader().setFont(QFont("Arial", weight=QFont.Bold))
        grid.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # Enable column resizing
        grid.horizontalHeader().sectionDoubleClicked.connect(self.resize_column_to_contents)
        grid.horizontalHeader().setStyleSheet("color: black")
        grid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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
            with open(file_name, 'rb') as file:
                content = file.read()
                if content[:4] != b'STQR':
                    self.text_edit.setText("Error: The file is not a valid .stqr file.")
                else:
                    self.text_edit.setText(self.format_hex(content))
                    self.pattern_search_button.setEnabled(True)

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

            # Split the data based on "00"
            data_parts = windows_data.split("00")

            # Iterate over the parts and display them
            for part in data_parts:
                if part:  # Check if the part is not empty
                    # Convert hex to bytes and then decode as ANSI
                    try:
                        decoded_part = bytes.fromhex(part).decode('ansi')
                    except UnicodeDecodeError:
                        decoded_part = f"Error decoding part: {part}"
                    self.text_edit.append(decoded_part)
                    self.append_to_title_column(decoded_part)  # Add the decoded part to the "Title" column

    def append_to_title_column(self, text):
        # Find the "Title" column index
        title_column_index = 0  # The first column is "Title"
        
        # Start appending text to the first available row in the "Title" column
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
            self.pattern_search_button.setEnabled(True)  # Re-enable the search button

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

    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout(dialog)

        layout.addWidget(self.create_icon_label(self.get_resource_path("egg.png"), 100))
        layout.addLayout(self.create_link_layout(self.get_resource_path("github.png"),
                                                 "Github - RTHKKona", "https://github.com/RTHKKona", 64))
        layout.addLayout(self.create_link_layout(self.get_resource_path("ko-fi.png"),
                                                 "Ko-Fi - Handburger", "https://ko-fi.com/handburger", 64))
        close_button = QPushButton("Close", dialog)
        close_button.clicked.connect(dialog.close)
        close_button.setStyleSheet("border: 1px solid white; color: black;")
        layout.addWidget(close_button)

        dialog.exec_()

    def create_icon_label(self, icon_path, size):
        label = QLabel(self)
        label.setPixmap(QPixmap(icon_path).scaled(size, size, Qt.KeepAspectRatio))
        return label

    def create_link_layout(self, icon_path, text, url, icon_size):
        layout = QHBoxLayout()
        layout.addWidget(self.create_icon_label(icon_path, icon_size))
        link_label = QLabel(f'<a href="{url}">{text}</a>', self)
        link_label.setOpenExternalLinks(True)
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
