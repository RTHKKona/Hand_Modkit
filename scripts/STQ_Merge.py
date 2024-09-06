# Current version
VERSION = "0.5"

import sys
import os
import struct
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, 
    QMessageBox, QTextEdit, QAction,QTableWidget, QTableWidgetItem, QHeaderView, 
    QWidget, QSplitter, QScrollArea, QDialog, QDialogButtonBox, QLabel, QGroupBox
)
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt

class STQMergeTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Handburger's STQ Merge Tool v{VERSION}")
        self.setGeometry(100, 100, 1600, 900)
        self.setWindowIcon(QIcon(self.get_resource_path("egg.png")))

        # Initialize variables
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

        # Create a menu bar with help and usage actions
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Help")
        
        # About button
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
        
        # Usage button
        usage_action = QAction("Usage", self)
        usage_action.triggered.connect(self.show_usage_dialog)
        help_menu.addAction(usage_action)

        # Create a splitter for text editors and the data grid
        top_splitter = QSplitter(Qt.Vertical)

        # File name labels
        self.file_label_1 = QLabel("", self)
        self.file_label_1.setFont(QFont("Consolas", 10, QFont.Bold))
        self.file_label_2 = QLabel("", self)
        self.file_label_2.setFont(QFont("Consolas", 10, QFont.Bold))

        # Horizontal layout for file names
        file_name_layout = QHBoxLayout()
        file_name_layout.addWidget(self.file_label_1)
        file_name_layout.addWidget(self.file_label_2)

        # Text editors for left and right views
        self.text_edit_left = QTextEdit(self, readOnly=True, font=QFont("Consolas", 11))
        self.text_edit_right = QTextEdit(self, readOnly=True, font=QFont("Consolas", 11))
        text_splitter = QSplitter(Qt.Horizontal)
        text_splitter.addWidget(self.text_edit_left)
        text_splitter.addWidget(self.text_edit_right)
        text_splitter.setStretchFactor(0, 2)  # Increase the stretch factor for larger previews
        text_splitter.setStretchFactor(1, 2)

        # Add labels and text_splitter to the top part of top_splitter
        text_layout = QVBoxLayout()
        text_layout.addLayout(file_name_layout)
        text_layout.addWidget(text_splitter)
        text_widget = QWidget()
        text_widget.setLayout(text_layout)
        top_splitter.addWidget(text_widget)

        # Grid for displaying conflicts (first STQR file)
        self.grid_group_1 = QGroupBox("", self)
        grid_layout_1 = QVBoxLayout(self.grid_group_1)
        self.data_grid_1 = self.create_data_grid()
        grid_layout_1.addWidget(self.data_grid_1)

        # Grid for displaying conflicts (second STQR file)
        self.grid_group_2 = QGroupBox("", self)
        grid_layout_2 = QVBoxLayout(self.grid_group_2)
        self.data_grid_2 = self.create_data_grid()
        grid_layout_2.addWidget(self.data_grid_2)

        # Scroll area for grids
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.addWidget(self.grid_group_1)
        scroll_layout.addWidget(self.grid_group_2)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        # Add grids to the bottom part of top_splitter
        top_splitter.addWidget(scroll_area)
        top_splitter.setStretchFactor(0, 1)  # Adjust stretch factors to make previews larger
        top_splitter.setStretchFactor(1, 4)

        # Add the top_splitter to the main layout
        main_layout.addWidget(top_splitter)

        # Add buttons at the bottom
        self.import_first_btn = QPushButton("Import Template STQR", self)
        self.import_first_btn.clicked.connect(lambda: self.load_file(0))
        bottom_layout.addWidget(self.import_first_btn)

        self.import_second_btn = QPushButton("Import Addition STQR", self)
        self.import_second_btn.clicked.connect(lambda: self.load_file(1))
        bottom_layout.addWidget(self.import_second_btn)

        self.merge_btn = QPushButton("Merge", self)
        self.merge_btn.clicked.connect(self.analyze_and_merge)
        bottom_layout.addWidget(self.merge_btn)

        self.save_btn = QPushButton("Save", self)
        self.save_btn.setEnabled(False)  # Disable the save button by default
        self.save_btn.clicked.connect(self.save_merged_file)
        bottom_layout.addWidget(self.save_btn)

        self.clear_btn = QPushButton("Clear", self)
        self.clear_btn.clicked.connect(self.clear_data)
        bottom_layout.addWidget(self.clear_btn)

        self.theme_btn = QPushButton("Change Theme", self)
        self.theme_btn.clicked.connect(self.toggle_theme)
        bottom_layout.addWidget(self.theme_btn)

        main_layout.addLayout(bottom_layout)

    def show_about_dialog(self):
        """Display the About dialog with version information."""
        about_text = (
            f"STQ Merge Tool\n"
            f"Version {VERSION}\n\n"
            "This tool allows you to merge two STQR files, analyze hexadecimal data, resolve conflicts, and save the merged file."
        )
        QMessageBox.about(self, "About", about_text)
            
    def show_usage_dialog(self):
        """Display the Usage dialog with instructions on how to use the tool."""
        usage_text = (
            "A quick tutorial on usage:\n"
            "1) Press the Import Template STQR for your first stqr file that you want to merge.\n"
            "2) Press the Import Addition STQR for your second stqr file that you want to merge.\n"
            "3) Press the Merge button to check for conflicts.\n"
            "4) Review the conflict checker and decide on which one you want to save.\n"
            "5) Save your new merged STQR file."
        )
        QMessageBox.information(self, "Usage", usage_text)

    def get_resource_path(self, filename):
        """Get the path to a resource file in the assets directory."""
        assets_path = os.path.join('assets', filename)
        if not os.path.exists(assets_path):
            self.show_error_message("Error", f"Resource not found: {filename} in {assets_path}.")
            return None
        return assets_path

    def create_data_grid(self):
        #Create a data grid with predefined columns for conflict resolution.
        grid = QTableWidget(self)
        grid.setColumnCount(7)
        grid.setHorizontalHeaderLabels([
            "File Directory", "Size of File (bytes)", "Number of Samples",
            "Number of Channels", "Sample Rate Hz", "Loop Start (samples)",
            "Loop End (samples)"
        ])
        grid.horizontalHeader().setFont(QFont("Arial", weight=QFont.Bold))
        grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        grid.horizontalHeader().setStyleSheet("QHeaderView::section { color: black; }")  # Set header text color to black
        grid.setEditTriggers(QTableWidget.DoubleClicked)
        return grid

    def load_file(self, index):
        #Load an STQR file and update the corresponding view.
        file, _ = QFileDialog.getOpenFileName(self, "Open .stqr File", "", "STQ Files (*.stqr);;All Files (*)")
        if file:
            if self.loaded_files[index] is None or os.path.basename(file) == os.path.basename(self.loaded_files[index]):
                self.loaded_files[index] = file
                if index == 0:
                    self.file_label_1.setText(f"Template: {file}")
                    self.grid_group_1.setTitle(f"{file} - Template")
                else:
                    self.file_label_2.setText(f"Addition: {file}")
                    self.grid_group_2.setTitle(f"{file} - Addition")
                self.load_hex_data(index)
                if index == 1:
                    self.load_template(file)
                    
                if None not in self.loaded_files:
                    self.save_btn.setEnabled(True)  # Enable the save button when both files are loaded
            else:
                self.show_error_message("Error", "The filenames of both STQR files must match exactly.")

    def load_hex_data(self, index):
       #Load hexadecimal data from the STQR file and display it.
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
        except Exception as e:
            self.show_error_message("Error", str(e))

    def load_template(self, file):
       #Load the template STQR file into memory.
        try:
            with open(file, 'rb') as f:
                self.template_data = bytearray(f.read())
                self.merged_data = bytearray(self.template_data)  # Copy template to merged data
        except Exception as e:
            self.show_error_message("Template Load Error", str(e))

    def search_patterns(self):
        # Search for specific patterns in the loaded STQR files and populate the data grid.
        # Clear the grids and reset the state
        self.data_grid_1.clearContents()
        self.data_grid_1.setRowCount(0)
        self.data_grid_2.clearContents()
        self.data_grid_2.setRowCount(0)
        self.pattern_offsets.clear()
        self.file_directories.clear()

        # Process the first file
        content_1 = self.hex_data[0]
        self.populate_patterns(self.data_grid_1, content_1)

        # Process the second file
        content_2 = self.hex_data[1]
        self.populate_patterns(self.data_grid_2, content_2)

        # Extract file directory data (assuming it's the same for both files)
        start_pattern = "0000000000000000736F756E64"
        start_index = content_1.find(start_pattern)
        if start_index != -1:
            self.extract_directory_data(content_1[start_index + len(start_pattern):])

    def populate_patterns(self, grid, content):
        # Populate the data grid with patterns found in the STQR file.
        pattern1 = "XXXXXXXX XXXXXXXX 02000000 80BB0000 XXXXXXXX XXXXXXXX".replace(' ', '')
        for index in range(0, len(content) - len(pattern1), 2):
            match = content[index:index + len(pattern1)]
            if self.pattern_matches(match, pattern1):
                window_data = content[index:index + 72]  # 36 bytes * 2 hex characters per byte = 72
                self.populate_grid(grid, window_data)
                self.pattern_offsets.append((index // 2, window_data))  # Store offset and data

    def extract_directory_data(self, data):
        # Extract directory information from the hex data and populate the grids.
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

        # Populate the file directories into the grids
        for i, directory in enumerate(self.file_directories):
            self.data_grid_1.setItem(i, 0, QTableWidgetItem(directory))
            self.data_grid_2.setItem(i, 0, QTableWidgetItem(directory))

    def populate_grid(self, grid, hex_data):
        # Populate the grid with decoded values from the hex data.
        row_position = grid.rowCount()
        grid.insertRow(row_position)
        for i in range(0, len(hex_data), 8):
            try:
                # Extract 8 hex characters (4 bytes)
                hex_part = hex_data[i:i + 8]
                if len(hex_part) == 8:
                    # Convert to little-endian signed int32
                    value = struct.unpack('<i', bytes.fromhex(hex_part))[0]
                    item = QTableWidgetItem(str(value))
                    grid.setItem(row_position, i // 8 + 1, item)
                else:
                    grid.setItem(row_position, i // 8 + 1, QTableWidgetItem("Invalid Data"))
            except struct.error:
                grid.setItem(row_position, i // 8 + 1, QTableWidgetItem("Error"))

    def pattern_matches(self, match, pattern):
        # Check if a hex string matches a specific pattern.
        return all(c == 'X' or c == m for c, m in zip(pattern, match))

    def analyze_and_merge(self):
        # Analyze the loaded STQR files for conflicts and merge them.
        try:
            if len(self.loaded_files) < 2 or None in self.loaded_files:
                raise ValueError("Please load both .stqr files before merging.")

            self.conflict_locations.clear()

            row_count = self.data_grid_1.rowCount()
            conflicting_rows = []

            for row in range(row_count):
                has_conflict = False
                for col in range(1, self.data_grid_1.columnCount()):  # Skip the first column (File Directory)
                    item1 = self.data_grid_1.item(row, col)
                    item2 = self.data_grid_2.item(row, col)
                    if item1 and item2 and item1.text() != item2.text():
                        # Highlight discrepancies in yellow with black text
                        item1.setBackground(QColor(Qt.yellow))
                        item1.setForeground(QColor(Qt.black))
                        item2.setBackground(QColor(Qt.yellow))
                        item2.setForeground(QColor(Qt.black))

                        conflict_key = f"Row {row + 1} - Column {col + 1}"
                        chosen_value = self.prompt_conflict_resolution(conflict_key, item1.text(), item2.text())
                        self.conflict_locations[(row, col)] = chosen_value

                        # Apply the chosen value to the original hex data of the first STQR file
                        self.update_hex_data(row, col, chosen_value)
                        has_conflict = True

                if has_conflict:
                    conflicting_rows.append(row)

            # Remove non-conflicting rows
            self.filter_conflicting_rows(conflicting_rows)

            # After resolving conflicts, prompt to save the file
            self.save_merged_file()

        except Exception as e:
            self.show_error_message("Merge Error", str(e))

    def prompt_conflict_resolution(self, conflict_key, value1, value2):
        # Prompt the user to resolve conflicts between the two STQR files."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Resolve Conflict")
        dialog_layout = QVBoxLayout(dialog)
        dialog_layout.addWidget(QLabel(f"Conflict found at {conflict_key}."))
        dialog_layout.addWidget(QLabel(f"Template: {value1}"))
        dialog_layout.addWidget(QLabel(f"Addition: {value2}"))

        button_box = QDialogButtonBox(QDialogButtonBox.NoButton)
        stqr1_button = QPushButton("Use Template", dialog)
        stqr2_button = QPushButton("Use Addition", dialog)

        button_box.addButton(stqr1_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(stqr2_button, QDialogButtonBox.RejectRole)
        dialog_layout.addWidget(button_box)

        chosen_value = None

        def on_stqr1():
            nonlocal chosen_value
            chosen_value = value1
            dialog.accept()

        def on_stqr2():
            nonlocal chosen_value
            chosen_value = value2
            dialog.accept()

        stqr1_button.clicked.connect(on_stqr1)
        stqr2_button.clicked.connect(on_stqr2)

        dialog.exec_()

        return chosen_value

    def update_hex_data(self, row, col, value):
        # Update the original hex data with the resolved conflict value."""
        try:
            # Convert the chosen value back to little-endian signed int32 hex
            hex_value = struct.pack('<i', int(value)).hex().upper()

            # Calculate the exact position in the hex data
            start_index = (self.pattern_offsets[row][0] * 2) + ((col - 1) * 8)
            self.merged_data[start_index:start_index + 8] = bytes.fromhex(hex_value)
        except Exception as e:
            self.show_error_message("Update Error", str(e))

    def filter_conflicting_rows(self, conflicting_rows):
        # Remove non-conflicting rows from the data grid."""
        rows_to_keep = set(conflicting_rows)
        for row in range(self.data_grid_1.rowCount() - 1, -1, -1):
            if row not in rows_to_keep:
                self.data_grid_1.removeRow(row)
                self.data_grid_2.removeRow(row)

    def save_merged_file(self):
        # Save the merged STQR file to disk."""
        try:
            original_filename = os.path.basename(self.loaded_files[0])  # Use the first STQR file's name
            default_filename = f"merged_{os.path.splitext(original_filename)[0]}.stqr"
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Merged STQR File", default_filename, "STQ Files (*.stqr);;All Files (*)")
            if file_name:
                with open(file_name, 'wb') as output_file:
                    output_file.write(self.merged_data)  # Save the modified template
                QMessageBox.information(self, "Save Successful", f"File saved successfully to {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"An unexpected error occurred: {str(e)}")

    def clear_data(self):
        # Clear all data and reset the tool's state."""
        self.text_edit_left.clear()
        self.text_edit_right.clear()
        self.data_grid_1.setRowCount(0)
        self.data_grid_2.setRowCount(0)
        self.hex_data.clear()
        self.loaded_files = [None, None]
        self.template_data = None
        self.merged_data = None
        self.file_label_1.setText("")
        self.file_label_2.setText("")
        self.save_btn.setEnabled(False)  # Disable the save button after clearing

    def format_hex(self, hex_str):
        # Format hexadecimal string into a human-readable format for display."""
        return '\n'.join(
            ' '.join(hex_str[i:i + 8] for i in range(start, start + 36 * 2, 8))  # 36 bytes per row
            for start in range(0, len(hex_str), 36 * 2)
        )

    def toggle_theme(self):
        # Toggle between dark mode and light mode."""
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_initial_theme(self):
        # Apply the initial theme when the tool is launched."""
        self.apply_theme()

    def apply_theme(self):
        # Apply the current theme based on the dark_mode flag."""
        stylesheet = """
            QWidget { background-color: #2b2b2b; color: #ffebcd; }
            QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
            QLabel { color: #ffebcd; }
            QLineEdit { background-color: #4d4d4d; color: #ffebcd; border: 1px solid #ffebcd; }
            QPushButton { background-color: #4d4d4d; color: #ffebcd; }
        """ if self.dark_mode else ""
        self.setStyleSheet(stylesheet)

    def show_error_message(self, title, message):
        # Display an error message in a message box."""
        QMessageBox.critical(self, title, message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = STQMergeTool()
    window.show()
    sys.exit(app.exec_())
