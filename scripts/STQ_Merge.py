import sys
import os
import re
import struct
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox, QTextEdit, QAction,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMenuBar, QWidget, QSplitter, QDialog, QDialogButtonBox
)
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt

class STQMergeTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Handburger's STQ Merge Tool")
        self.setGeometry(100, 100, 1600, 900)
        self.setWindowIcon(QIcon(self.get_resource_path("egg.png")))

        self.loaded_files = [None, None]
        self.hex_data = []
        self.conflict_locations = {}
        self.template_data = None  # Store template data
        self.merged_data = None  # Store merged data
        self.pattern_offsets = []  # Store pattern offsets
        self.file_directories = []  # Store file directory information
        self.dark_mode = True  # Start in dark mode by default

        self.initUI()
        self.apply_initial_theme()

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        bottom_layout = QHBoxLayout()

        # Create a menu bar
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Help")
        help_action = QAction("About", self)
        help_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(help_action)

        # Create a splitter for text editors and the data grid
        top_splitter = QSplitter(Qt.Vertical)
        
        # Text editors for left and right views
        self.text_edit_left = QTextEdit(self, readOnly=True, font=QFont("Consolas", 10))
        self.text_edit_right = QTextEdit(self, readOnly=True, font=QFont("Consolas", 10))
        text_splitter = QSplitter(Qt.Horizontal)
        text_splitter.addWidget(self.text_edit_left)
        text_splitter.addWidget(self.text_edit_right)
        text_splitter.setStretchFactor(0, 1)
        text_splitter.setStretchFactor(1, 1)
        
        # Add text_splitter to the top part of top_splitter
        top_splitter.addWidget(text_splitter)

        # Grid for displaying conflicts
        self.data_grid = self.create_data_grid()

        # Add data_grid to the bottom part of top_splitter
        top_splitter.addWidget(self.data_grid)
        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 1)

        # Add the top_splitter to the main layout
        main_layout.addWidget(top_splitter)

        # Add buttons at the bottom
        self.import_first_btn = QPushButton("Import First STQR", self)
        self.import_first_btn.clicked.connect(lambda: self.load_file(0))
        bottom_layout.addWidget(self.import_first_btn)

        self.import_second_btn = QPushButton("Import Second STQR", self)
        self.import_second_btn.clicked.connect(lambda: self.load_file(1))
        bottom_layout.addWidget(self.import_second_btn)

        self.merge_btn = QPushButton("Merge", self)
        self.merge_btn.clicked.connect(self.compare_files)
        bottom_layout.addWidget(self.merge_btn)

        self.save_btn = QPushButton("Save", self)
        self.save_btn.clicked.connect(self.save_merged_file)
        bottom_layout.addWidget(self.save_btn)

        self.clear_btn = QPushButton("Clear", self)
        self.clear_btn.clicked.connect(self.clear_data)
        bottom_layout.addWidget(self.clear_btn)

        self.theme_btn = QPushButton("Change Theme", self)
        self.theme_btn.clicked.connect(self.toggle_theme)
        bottom_layout.addWidget(self.theme_btn)

        main_layout.addLayout(bottom_layout)

    def get_resource_path(self, filename):
        assets_path = os.path.join('assets', filename)
        if not os.path.exists(assets_path):
            self.show_error_message("Error", f"Resource not found: {filename} in {assets_path}.")
            return None
        return assets_path

    def create_data_grid(self):
        grid = QTableWidget(self)
        grid.setColumnCount(7)
        grid.setHorizontalHeaderLabels([
            "File Directory", "Size of File (bytes)", "Number of Samples",
            "Number of Channels", "Sample Rate Hz", "Loop Start (samples)",
            "Loop End (samples)"
        ])
        grid.horizontalHeader().setFont(QFont("Arial", weight=QFont.Bold))
        grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        grid.horizontalHeader().setStyleSheet("QHeaderView::section { color: black; }")
        grid.setEditTriggers(QTableWidget.DoubleClicked)
        return grid

    def load_file(self, index):
        file, _ = QFileDialog.getOpenFileName(self, "Open .stqr File", "", "STQ Files (*.stqr);;All Files (*)")
        if file:
            if self.loaded_files[index] is None or os.path.basename(file) == os.path.basename(self.loaded_files[index]):
                self.loaded_files[index] = file
                self.load_hex_data(index)
                if index == 1:
                    self.load_template(file)
            else:
                self.show_error_message("Error", "The filenames of both STQR files must match exactly.")

    def load_hex_data(self, index):
        try:
            with open(self.loaded_files[index], 'rb') as f:
                content = f.read()
                if content[:4] != b'STQR':
                    raise ValueError(f"File {self.loaded_files[index]} is not a valid .stqr file.")
                hex_data = content.hex().upper().replace(" ", "")

                if index == 0:
                    self.hex_data.insert(0, hex_data)
                    self.text_edit_left.setText(self.format_hex(hex_data))
                elif index == 1:
                    self.hex_data.insert(1, hex_data)
                    self.text_edit_right.setText(self.format_hex(hex_data))
                    self.search_patterns()  # Populate the grid and file directories
                print(f"Successfully loaded file {self.loaded_files[index]} as hex data.")
        except Exception as e:
            self.show_error_message("Error", str(e))
            print(f"Error loading file {self.loaded_files[index]}: {e}")

    def load_template(self, file):
        try:
            with open(file, 'rb') as f:
                self.template_data = bytearray(f.read())
                self.merged_data = bytearray(self.template_data)  # Copy template to merged data
        except Exception as e:
            self.show_error_message("Template Load Error", str(e))
            print(f"Error loading template from {file}: {e}")

    def search_patterns(self):
        content = self.hex_data[1]  # Process the second file (template)
        self.data_grid.clearContents()
        self.data_grid.setRowCount(0)
        self.pattern_offsets.clear()
        self.file_directories.clear()

        # Find and process patterns
        pattern1 = "XXXXXXXX XXXXXXXX 02000000 80BB0000 XXXXXXXX XXXXXXXX".replace(' ', '')
        for index in range(0, len(content) - len(pattern1), 2):
            match = content[index:index + len(pattern1)]
            if self.pattern_matches(match, pattern1):
                window_data = content[index:index + 48]
                self.populate_grid(window_data)
                self.pattern_offsets.append(index // 2)

        # Extract file directory information
        start_pattern = "0000000000000000736F756E64"
        start_index = content.find(start_pattern)
        if start_index != -1:
            self.extract_directory_data(content[start_index + len(start_pattern):])

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
                        self.file_directories.append(decoded_part)
                    except (ValueError, UnicodeDecodeError):
                        pass
                digit_count = 0
                buffer = ""
            else:
                buffer += part
                digit_count += 2

        # Populate the grid with file directory data
        for i, directory in enumerate(self.file_directories):
            self.data_grid.setItem(i, 0, QTableWidgetItem(directory))

    def populate_grid(self, hex_data):
        row_position = self.data_grid.rowCount()
        self.data_grid.insertRow(row_position)
        for i in range(0, len(hex_data), 8):
            value = struct.unpack('<i', bytes.fromhex(hex_data[i:i + 8]))[0]
            self.data_grid.setItem(row_position, i // 8 + 1, QTableWidgetItem(str(value)))

    def pattern_matches(self, match, pattern):
        return all(c == 'X' or c == m for c, m in zip(pattern, match))

    def compare_files(self):
        try:
            if len(self.loaded_files) < 2 or None in self.loaded_files:
                raise ValueError("Please load both .stqr files before merging.")

            self.data_grid.setRowCount(0)
            self.conflict_locations.clear()

            left_patterns = list(self.pattern_offsets)
            right_patterns = list(self.pattern_offsets)

            pattern_count = min(len(left_patterns), len(right_patterns))
            if pattern_count == 0:
                raise ValueError("No matching patterns found in the provided STQR files.")

            for i in range(pattern_count):
                left_match = left_patterns[i]
                right_match = right_patterns[i]

                if left_match != right_match:
                    row_position = self.data_grid.rowCount()
                    self.data_grid.insertRow(row_position)

                    for j in range(7):
                        left_hex = left_match[j*8:(j+1)*8]
                        right_hex = right_match[j*8:(j+1)*8]

                        if len(left_hex) == 8 and len(right_hex) == 8:
                            left_val = struct.unpack('<i', bytes.fromhex(left_hex))[0]
                            right_val = struct.unpack('<i', bytes.fromhex(right_hex))[0]

                            if left_val != right_val:
                                conflict_key = f"Pattern {i + 1} - Position {j + 1}"
                                chosen_value = self.prompt_conflict_resolution(conflict_key, str(left_val), str(right_val))
                                self.conflict_locations[conflict_key] = (i, j, chosen_value)
                                item_left = QTableWidgetItem(chosen_value)
                                item_left.setBackground(QColor(Qt.yellow))
                                item_left.setForeground(QColor(Qt.black))
                                self.update_merged_data(i, j, chosen_value)
                            else:
                                item_left = QTableWidgetItem(str(left_val))

                            self.data_grid.setItem(row_position, j + 1, item_left)

            print(f"Pattern comparison complete. Conflicts found: {len(self.conflict_locations)}")

        except Exception as e:
            self.show_error_message("Merge Error", str(e))
            print(f"Error during file comparison: {e}")

    def update_merged_data(self, pattern_index, position_index, int_value):
        try:
            hex_value = struct.pack('<i', int(int_value)).hex().upper()
            pattern_match = list(self.pattern_offsets)[pattern_index]
            start_index = pattern_match.start() + (position_index * 8)
            self.merged_data[start_index:start_index + 8] = bytes.fromhex(hex_value)
        except Exception as e:
            self.show_error_message("Update Error", str(e))
            print(f"Error updating merged data: {e}")

    def save_merged_file(self):
        try:
            original_filename = os.path.basename(self.loaded_files[1])  # Use the second STQR file as the template
            default_filename = f"merged_{original_filename}"
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Merged STQR File", default_filename, "STQ Files (*.stqr);;All Files (*)")
            if file_name:
                with open(file_name, 'wb') as output_file:
                    output_file.write(self.merged_data)  # Save the modified template
                QMessageBox.information(self, "Save Successful", f"File saved successfully to {file_name}")
                print(f"Successfully saved merged file to {file_name}.")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"An unexpected error occurred: {str(e)}")
            print(f"Error saving file: {e}")

    def clear_data(self):
        self.text_edit_left.clear()
        self.text_edit_right.clear()
        self.data_grid.setRowCount(0)
        self.hex_data.clear()
        self.loaded_files = [None, None]
        self.template_data = None
        self.merged_data = None

    def format_hex(self, hex_str):
        return '\n'.join(
            ' '.join(hex_str[i:i + 8] for i in range(start, start + 32 * 2, 8))
            for start in range(0, len(hex_str), 32 * 2)
        )

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_initial_theme(self):
        self.apply_theme()

    def apply_theme(self):
        stylesheet = """
            QWidget { background-color: #2b2b2b; color: #ffebcd; }
            QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
            QLabel { color: #ffebcd; }
            QLineEdit { background-color: #4d4d4d; color: #ffebcd; border: 1px solid #ffebcd; }
            QPushButton { background-color: #4d4d4d; color: #ffebcd; }
        """ if self.dark_mode else ""
        self.setStyleSheet(stylesheet)

    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)

    def show_about_dialog(self):
        about_text = (
            "STQ Merge Tool\n"
            "Version 0.1\n\n"
            "This tool allows you to merge two STQR files, resolve conflicts, and save the merged file."
        )
        QMessageBox.about(self, "About", about_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = STQMergeTool()
    window.show()
    sys.exit(app.exec_())
