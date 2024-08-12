import sys
import struct
import os
import random
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QLabel,
    QDialog, QSplitter, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QAction, QSizePolicy
)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QRect

class STQReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = False
        self.loaded_file_name = ""
        self.original_content = b""
        self.pattern_offsets = []
        self.undo_stack = []  # Initialize the undo stack
        self.redo_stack = []  # Initialize the redo stack
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Handburger's STQ Reader Tool")
        self.setGeometry(100, 100, 1600, 800)  # Extended width to accommodate the new text panel
        self.setWindowIcon(QIcon(self.get_resource_path("egg.png")))

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        splitter = QSplitter(Qt.Vertical, main_widget)

        self.background_label = QLabel(main_widget)
        egg_pixmap = QPixmap(self.get_resource_path("egg.png")).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.background_label.setPixmap(egg_pixmap)
        self.background_label.setGeometry(QRect(self.width() - 220, 10, 200, 200))
        self.background_label.setStyleSheet("opacity: 0.15;")
        self.background_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        self.background_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.background_label.hide()
        self.background_label.raise_()

        self.text_edit = QTextEdit(self, readOnly=True, font=QFont("Consolas", 10))
        self.text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.text_edit.setStyleSheet("background-color: rgba(255, 255, 255, 0.8);")

        self.text_panel = QTextEdit(self, readOnly=True, font=QFont("Consolas", 10))
        self.text_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.text_panel.setStyleSheet("background-color: rgba(255, 255, 255, 0.8);")
        self.text_panel.hide()  # Initially hidden

        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.addWidget(self.text_edit)
        top_splitter.addWidget(self.text_panel)
        splitter.addWidget(top_splitter)

        self.data_grid = self.create_data_grid()
        splitter.addWidget(self.data_grid)

        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(splitter)
        self.buttons = self.create_buttons()
        main_layout.addLayout(self.buttons)

        self.setup_menu()
        self.apply_styles()

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
        grid.setEditTriggers(QTableWidget.DoubleClicked)
        return grid

    def create_buttons(self):
        layout = QHBoxLayout()
        buttons = [
            ("Load .stqr File", self.load_file),
            ("Search Patterns", self.search_patterns),
            ("Save Changes", self.save_changes),
            ("Clear", self.clear_data),
            ("Undo", self.undo),
            ("Redo", self.redo),  # New Redo button
            ("Toggle Dark/Light Mode", self.toggle_theme),
            ("Increase Header Size", self.increase_header_size),
            ("Decrease Header Size", self.decrease_header_size)
        ]
        for label, callback in buttons:
            button = QPushButton(label, self)
            button.clicked.connect(callback)
            layout.addWidget(button)
        self.pattern_search_button = layout.itemAt(1).widget()
        self.pattern_search_button.setEnabled(False)
        return layout


    def setup_menu(self):
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        menubar = self.menuBar()
        menubar.setStyleSheet("background-color: grey;")
        menubar.addMenu("Help").addAction(about_action)

    def load_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open .stqr File", "", "STQ Files (*.stqr);;All Files (*)")
        if file_name:
            self.loaded_file_name = file_name
            self.setWindowTitle(f"Handburger's STQ Reader Tool - Editing {os.path.basename(file_name)}")
            with open(file_name, 'rb') as file:
                self.original_content = file.read()
                if self.original_content[:4] != b'STQR':
                    self.text_edit.setText("Error: The file is not a valid .stqr file.")
                else:
                    self.text_edit.setText(self.format_hex(self.original_content))
                    self.pattern_search_button.setEnabled(True)
                    if random.random() < 0.2298:  # Increased chance of showing egg.png
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
        self.pattern_search_button.setEnabled(False)
        content = self.original_content.hex().upper().replace(' ', '').replace('\n', '')
        self.data_grid.clearContents()
        self.data_grid.setRowCount(0)
        self.pattern_offsets.clear()  # Ensure pattern offsets are reset

        self.text_panel.show()  # Show the new text panel
        self.text_panel.clear()  # Clear any previous content

        pattern1 = "XXXXXXXX XXXXXXXX 02000000 80BB0000 XXXXXXXX XXXXXXXX".replace(' ', '')
        for index in range(0, len(content) - len(pattern1), 2):
            match = content[index:index + len(pattern1)]
            if self.pattern_matches(match, pattern1):
                window_data = content[index:index + 48]
                formatted_hex = self.format_hex(bytes.fromhex(window_data))
                self.text_panel.append(f"Found pattern at index {index // 2}:\n{formatted_hex}\n")
                self.populate_grid(window_data)
                self.pattern_offsets.append(index // 2)  # Store the offset

        self.text_panel.append("\n")

        start_pattern = "0000000000000000736F756E64"
        start_index = content.find(start_pattern)
        if start_index != -1:
            windows_data = content[start_index + len(start_pattern):]

            digit_count = 0
            buffer = ""

            while windows_data:
                part = windows_data[:2]
                windows_data = windows_data[2:]

                if part == "00":
                    if digit_count >= 8:
                        try:
                            decoded_part = bytes.fromhex(buffer).decode('ansi')
                            self.text_panel.append(f"Found directory: {decoded_part}\n")
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

    def save_changes(self):
        if not self.loaded_file_name:
            QMessageBox.warning(self, "No File Loaded", "Please load a file before trying to save.")
            return

        # Revalidate the offsets list before saving
        if len(self.pattern_offsets) != self.data_grid.rowCount():
            QMessageBox.critical(self, "Save Failed", "Pattern offsets do not match the number of rows in the grid. Unable to save changes.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Save STQR File", self.loaded_file_name, "STQ Files (*.stqr);;All Files (*)")
        if file_name:
            try:
                modified_content = bytearray(self.original_content)
                for row in range(self.data_grid.rowCount()):
                    offset = self.pattern_offsets[row]
                    for col in range(1, 7):
                        cell_item = self.data_grid.item(row, col)
                        if not cell_item:
                            raise ValueError(f"Missing data at row {row}, column {col}. Unable to save changes.")

                        int_value = int(cell_item.text())
                        hex_value = struct.pack('<i', int_value)
                        start = offset + (col - 1) * 4
                        modified_content[start:start + 4] = hex_value

                with open(file_name, 'wb') as file:
                    file.write(modified_content)
                QMessageBox.information(self, "Save Successful", f"File saved successfully to {file_name}")
            except IndexError as e:
                QMessageBox.critical(self, "Save Failed", f"An error occurred: {str(e)}")
            except ValueError as e:
                QMessageBox.critical(self, "Save Failed", f"An error occurred: {str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "Save Failed", f"An unexpected error occurred: {str(e)}")


    def clear_data(self):
        reply = QMessageBox.question(
            self, 'Clear Data', 
            "Are you sure you want to clear all data? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.store_state()  # Store the current state before clearing
            self.text_edit.clear()  # Clear the original hex code display
            self.text_panel.clear()  # Clear the additional text panel
            self.text_panel.hide()   # Hide the text panel when clearing
            self.data_grid.clearContents()  # Clear the grid content
            self.data_grid.setRowCount(0)  # Reset the row count in the grid
            self.pattern_offsets.clear()  # Clear the pattern offsets
            self.setWindowTitle("Handburger's STQ Reader Tool")  # Reset the window title
            self.pattern_search_button.setEnabled(True)  # Re-enable the search button
            self.background_label.hide()  # Hide the background label
            self.loaded_file_name = ""  # Clear the loaded file name
            self.original_content = b""  # Reset the original content
            QMessageBox.information(self, "Clear Successful", "All data has been cleared.")
            
    def undo(self):
        if self.undo_stack:
            current_state = {
                'text_edit': self.text_edit.toPlainText(),
                'text_panel': self.text_panel.toPlainText(),
                'grid_data': [],
                'pattern_offsets': self.pattern_offsets[:],
                'file_name': self.loaded_file_name,
                'original_content': self.original_content
            }
            
            for row in range(self.data_grid.rowCount()):
                row_data = []
                for col in range(self.data_grid.columnCount()):
                    item = self.data_grid.item(row, col)
                    row_data.append(item.text() if item else "")
                current_state['grid_data'].append(row_data)
            
            self.redo_stack.append(current_state)  # Push the current state to the redo stack
            
            previous_state = self.undo_stack.pop()  # Pop the last state from the undo stack
            self.restore_state(previous_state)  # Restore the previous state

    def redo(self):
        if self.redo_stack:
            current_state = {
                'text_edit': self.text_edit.toPlainText(),
                'text_panel': self.text_panel.toPlainText(),
                'grid_data': [],
                'pattern_offsets': self.pattern_offsets[:],
                'file_name': self.loaded_file_name,
                'original_content': self.original_content
            }
            
            for row in range(self.data_grid.rowCount()):
                row_data = []
                for col in range(self.data_grid.columnCount()):
                    item = self.data_grid.item(row, col)
                    row_data.append(item.text() if item else "")
                current_state['grid_data'].append(row_data)
            
            self.undo_stack.append(current_state)  # Push the current state to the undo stack
            
            next_state = self.redo_stack.pop()  # Pop the last state from the redo stack
            self.restore_state(next_state)  # Restore the next state

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_styles()

    def apply_styles(self):
        style = "background-color: black; color: white;" if self.dark_mode else "background-color: white; color: black;"
        button_style = "border: 1px solid white; color: white; padding-top: 10px; padding-bottom: 10px; font-weight: bold;" if self.dark_mode else "border: 1px solid black; color: black; padding-top: 10px; padding-bottom: 10px; font-weight: bold;"
        self.setStyleSheet(style)
        self.text_edit.setStyleSheet(style)
        self.text_panel.setStyleSheet(style)
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
    def store_state(self):
        state = {
            'text_edit': self.text_edit.toPlainText(),
            'text_panel': self.text_panel.toPlainText(),
            'grid_data': [],
            'pattern_offsets': self.pattern_offsets[:],
            'file_name': self.loaded_file_name,
            'original_content': self.original_content
        }
        
        for row in range(self.data_grid.rowCount()):
            row_data = []
            for col in range(self.data_grid.columnCount()):
                item = self.data_grid.item(row, col)
                row_data.append(item.text() if item else "")
            state['grid_data'].append(row_data)
        
        # Push the current state to the undo stack and clear the redo stack
        self.undo_stack.append(state)
        self.redo_stack.clear()

    def restore_state(self, state):
        self.text_edit.setText(state['text_edit'])
        self.text_panel.setText(state['text_panel'])
        self.text_panel.setVisible(bool(state['text_panel']))  # Show text panel if there is content

        self.data_grid.setRowCount(len(state['grid_data']))
        for row, row_data in enumerate(state['grid_data']):
            for col, cell_data in enumerate(row_data):
                self.data_grid.setItem(row, col, QTableWidgetItem(cell_data))
        
        self.pattern_offsets = state['pattern_offsets']
        self.loaded_file_name = state['file_name']
        self.original_content = state['original_content']
        self.setWindowTitle(f"Handburger's STQ Reader Tool - Editing {os.path.basename(self.loaded_file_name)}")



    def show_about_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setGeometry(300, 300, 400, 200)
        layout = QVBoxLayout(dialog)

        about_label = QLabel(self.create_about_text(), self)
        about_label.setFont(QFont("Arial", 12))
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
            "Version 1.2\n\n"
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
        link_label.setFont(QFont("Arial", 12))
        link_label.setStyleSheet("color: white;" if self.dark_mode else "color: black;")
        layout.addWidget(link_label)
        return layout

    def get_resource_path(self, filename):
        return os.path.join(os.getcwd(), filename)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    reader = STQReader()
    reader.show()
    sys.exit(app.exec_())
