import os
import sys
import tempfile
import shutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QTableWidget, 
    QTableWidgetItem, QHeaderView, QFileDialog, QWidget, QGridLayout, QLabel, QMessageBox,
)
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent, QIcon
from PyQt5.QtCore import Qt, QMimeData
import re

class STQMergeTool(QMainWindow):
    PATTERN_REGEX = re.compile(r"([A-F0-9]{16})(0200000080BB0000)([A-F0-9]{16})")
    DIRECTORY_PATTERN = re.compile(r"([A-F0-9]{16})(736F756E64)")

    def __init__(self):
        super().__init__()
        self.setWindowTitle("STQR Merge Tool")
        self.setGeometry(100, 100, 1600, 900)
        self.setWindowIcon(QIcon(self.get_resource_path("egg.png")))

        self.temp_dir = tempfile.mkdtemp()
        self.loaded_files = []
        self.renamed_files = []
        self.hex_data = []
        self.conflict_positions = []
        self.tally_count = 1

        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)

        # Input box
        self.input_label = QLabel("Drag and Drop STQR Files Here", self)
        self.input_label.setAlignment(Qt.AlignCenter)
        self.input_label.setFont(QFont("Arial", 16))
        self.input_label.setAcceptDrops(True)
        self.input_label.dragEnterEvent = self.dragEnterEvent
        self.input_label.dropEvent = self.dropEvent
        self.main_layout.addWidget(self.input_label)

        # Grid for hexadecimal data
        self.data_grid = self.create_data_grid()
        self.main_layout.addWidget(self.data_grid)

        # Add buttons
        self.buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save", self)
        self.save_btn.clicked.connect(self.save_merged_file)
        self.buttons_layout.addWidget(self.save_btn)

        self.main_layout.addLayout(self.buttons_layout)
        self.setCentralWidget(self.main_widget)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.endswith('.stqr'):
                self.loaded_files.append(file_path)
                self.rename_and_process_file(file_path)

    def rename_and_process_file(self, file_path):
        filename = os.path.basename(file_path)
        new_name = self.generate_fast_food_name(len(self.renamed_files))
        new_path = os.path.join(self.temp_dir, new_name + ".stqr")
        shutil.copy(file_path, new_path)
        self.renamed_files.append(new_path)
        self.process_hex_data(new_path)

    def generate_fast_food_name(self, index):
        fast_food_names = ['cheese', 'fries', 'burger', 'nugget', 'soda']
        return fast_food_names[index % len(fast_food_names)]

    def process_hex_data(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                content = f.read().hex().upper()
                self.scan_and_populate_grid(content)
        except Exception as e:
            self.show_error_message("Error", f"Failed to process file: {e}")

    def scan_and_populate_grid(self, content):
        matches = self.PATTERN_REGEX.finditer(content)
        for match in matches:
            left = match.group(1)
            right = match.group(3)
            pattern_row = f"{left} {right} 02000000 80BB0000 {left} {right}"

            if self.is_conflict(pattern_row):
                self.populate_grid_with_conflict(self.tally_count, pattern_row)
                self.tally_count += 1

        # Scan for directory data
        start_pattern = "0000000000000000736F756E64"
        start_index = content.find(start_pattern)
        if start_index != -1:
            self.extract_directory_data(content[start_index + len(start_pattern):])

    def is_conflict(self, row_data):
        return any(row_data != other_row for other_row in self.hex_data)

    def populate_grid_with_conflict(self, tally, conflict_data):
        row_position = self.data_grid.rowCount()
        self.data_grid.insertRow(row_position)

        tally_item = QTableWidgetItem(str(tally))
        self.data_grid.setItem(row_position, 0, tally_item)

        for col, hex_part in enumerate(conflict_data.split()):
            hex_item = QTableWidgetItem(hex_part)
            self.data_grid.setItem(row_position, col + 1, hex_item)

    def extract_directory_data(self, data):
        digit_count = 0
        buffer = ""
        while data:
            part = data[:2]
            data = data[2:]
            if part == "00":
                if digit_count >= 8:
                    try:
                        decoded_part = bytes.fromhex(buffer).decode('ansi')
                        self.append_to_title_column(decoded_part)
                    except (ValueError, UnicodeDecodeError):
                        pass
                digit_count = 0
                buffer = ""
            else:
                buffer += part
                digit_count += 2

    def append_to_title_column(self, text):
        title_column_index = 0
        row_count = self.data_grid.rowCount()
        for row in range(row_count):
            item = self.data_grid.item(row, title_column_index)
            if item is None or item.text() == "":
                # Append "sound" to the first title populated
                if row == 0:
                    text = "sound" + text
                self.data_grid.setItem(row, title_column_index, QTableWidgetItem(text))
                break

    def save_merged_file(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Merged STQR File", "merged_output.stqr", "STQ Files (*.stqr);;All Files (*)")
            if file_name:
                with open(file_name, 'wb') as f:
                    for row in range(self.data_grid.rowCount()):
                        row_data = []
                        for col in range(1, self.data_grid.columnCount()):
                            item = self.data_grid.item(row, col)
                            if item:
                                row_data.append(item.text())
                        if row_data:
                            f.write(bytes.fromhex("".join(row_data)))
                self.show_message("Save Successful", f"File saved successfully to {file_name}")
        except Exception as e:
            self.show_error_message("Save Failed", f"An unexpected error occurred: {e}")

    def create_data_grid(self):
        grid = QTableWidget(self)
        grid.setColumnCount(9)
        grid.setHorizontalHeaderLabels(["Pattern Position"] + [f"{i*4}-{(i+1)*4-1} (hex)" for i in range(8)])
        grid.horizontalHeader().setFont(QFont("Arial", weight=QFont.Bold))
        grid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        grid.setEditTriggers(QTableWidget.DoubleClicked)
        return grid

    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def get_resource_path(self, filename):
        return os.path.join(os.path.dirname(__file__), 'assets', filename)

    def closeEvent(self, event):
        shutil.rmtree(self.temp_dir)
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = STQMergeTool()
    window.show()
    sys.exit(app.exec_())
