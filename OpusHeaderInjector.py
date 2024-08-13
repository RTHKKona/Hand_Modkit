import sys
import struct
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QAction, QMessageBox, QSizePolicy, QLabel
)
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt

class OpusHeaderInjector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.loaded_file_name = ""
        self.edited_header = b""
        self.headers = [
            "Stream Total Samples", "Number of Channels", "Loop Start (samples)", "Loop End (samples)",
            "Buffer 1", "Buffer 2", "Buffer 3", "Buffer 4", "Unknown 1", "Unknown 2", "Unknown 3", "Unknown 4"
        ]
        self.target_pattern = b"\x01\x00\x00\x80\x18\x00\x00\x00\x00\x02\xF0\x00\x80\xBB\x00\x00" \
                              b"\x20\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x78\x00\x00\x00"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Opus Header Injector")
        self.setGeometry(100, 100, 1600, 800)
        self.setWindowIcon(QIcon("icon.png"))

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        splitter = QSplitter(Qt.Vertical, main_widget)

        # Top label and Help button
        top_layout = QHBoxLayout()
        self.header_info_label = QLabel("No header loaded", self)
        self.help_button = QPushButton("Help", self)
        top_layout.addWidget(self.header_info_label)
        top_layout.addStretch()
        top_layout.addWidget(self.help_button)
        top_widget = QWidget()
        top_widget.setLayout(top_layout)

        # Text Box for Hex Data (Displaying the header)
        self.hex_view = QTextEdit(self, readOnly=True, font=QFont("Consolas", 10))
        self.hex_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.hex_view.setStyleSheet("background-color: rgba(255, 255, 255, 0.8);")

        # Grid for Editing int32 Data
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(12)
        self.table_widget.setHorizontalHeaderLabels(self.headers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.setEditTriggers(QTableWidget.AllEditTriggers)

        splitter.addWidget(self.hex_view)
        splitter.addWidget(self.table_widget)
        
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("Load Opus File", self)
        self.load_button.clicked.connect(self.load_file)
        button_layout.addWidget(self.load_button)
        
        self.save_button = QPushButton("Save As New File", self)
        self.save_button.clicked.connect(self.save_file_as)
        button_layout.addWidget(self.save_button)
        
        self.append_button = QPushButton("Append Header to Another File", self)
        self.append_button.clicked.connect(self.append_header)
        button_layout.addWidget(self.append_button)

        self.preview_button = QPushButton("Preview Appended Header", self)
        self.preview_button.clicked.connect(self.preview_appended_header)
        button_layout.addWidget(self.preview_button)

        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(top_widget)
        main_layout.addWidget(splitter)
        main_layout.addLayout(button_layout)

        self.init_menu()
        self.show()

    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")
        
        open_file_action = QAction("&Open", self)
        open_file_action.triggered.connect(self.load_file)
        file_menu.addAction(open_file_action)

        save_file_action = QAction("&Save As", self)
        save_file_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_file_action)

    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open OPUS File", "", "Opus Files (*.opus);;All Files (*)", options=options)
        if file_name:
            with open(file_name, "rb") as file:
                self.original_content = file.read()
                self.loaded_file_name = file_name
            self.setWindowTitle(f"Opus Header Injector - Editing: {os.path.basename(file_name)}")
            header_end_offset = self.find_header_end()
            self.display_hex_content(header_end_offset)
            self.populate_grid(header_end_offset)
            self.header_info_label.setText(f"Header Size: {header_end_offset} bytes")

    def find_header_end(self):
        # Always include the first 12 4-byte chunks in the header.
        header_end_offset = 48
        # Continue to include values until the pattern is detected.
        pattern_index = self.original_content.find(self.target_pattern, header_end_offset)
        if pattern_index != -1:
            return pattern_index
        return len(self.original_content)

    def display_hex_content(self, header_end_offset):
        # Display the header in the text box (everything before the pattern)
        hex_view = '\n'.join(
            ' '.join(
                [self.original_content[i+j:i+j+4].hex().upper() for j in range(0, 32, 4)]
            ) for i in range(0, min(header_end_offset, len(self.original_content)), 32)
        )
        self.hex_view.setText(hex_view)

    def populate_grid(self, header_end_offset):
        # Convert the first 12 4-byte chunks within the header into signed int32 and populate the grid
        self.table_widget.setRowCount(1)  # Only one row since we're dealing with 12 columns
        for col in range(12):
            offset = col * 4
            if offset + 4 <= header_end_offset:
                int_value = struct.unpack('<i', self.original_content[offset:offset+4])[0]
                item = QTableWidgetItem(str(int_value))
                # If the data is between the 12th chunk and the pattern, make it non-editable and greyed out
                if offset >= 48 and offset < header_end_offset:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setForeground(QColor(150, 150, 150))  # Grey out non-editable cells
                self.table_widget.setItem(0, col, item)

    def save_file_as(self):
        if not self.loaded_file_name:
            QMessageBox.warning(self, "Error", "No file loaded to save.")
            return

        # Pre-set name with "new" prefix and save to the same directory as the input file
        base_name = os.path.basename(self.loaded_file_name)
        directory = os.path.dirname(self.loaded_file_name)
        save_file_name = os.path.join(directory, f"new_{base_name}")
        options = QFileDialog.Options()
        save_file_name, _ = QFileDialog.getSaveFileName(self, "Save OPUS File As", save_file_name, "Opus Files (*.opus);;All Files (*)", options=options)
        if save_file_name:
            # Save the edited grid data back to the new file
            self.edited_header = bytearray(self.original_content[:48])
            for col in range(12):
                item = self.table_widget.item(0, col)
                if item:
                    value = int(item.text())
                    offset = col * 4
                    hex_value = struct.pack('<i', value)
                    self.edited_header[offset:offset+4] = hex_value

            with open(save_file_name, "wb") as file:
                file.write(self.edited_header)

            QMessageBox.information(self, "Saved", f"File saved as: {os.path.basename(save_file_name)}")

    def append_header(self):
        if not self.edited_header:
            QMessageBox.warning(self, "Error", "No header data available. Please save the edited header first.")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open OPUS File to Append Header", "", "Opus Files (*.opus);;All Files (*)", options=options)
        if file_name:
            with open(file_name, "rb") as file:
                original_content = file.read()
            
            # Pre-set name with "new" prefix and save to the same directory as the input file
            base_name = os.path.basename(file_name)
            directory = os.path.dirname(file_name)
            save_file_name = os.path.join(directory, f"new_{base_name}")
            options = QFileDialog.Options()
            save_file_name, _ = QFileDialog.getSaveFileName(self, "Save Appended OPUS File As", save_file_name, "Opus Files (*.opus);;All Files (*)", options=options)
            if save_file_name:
                # Create a new file with the full header (data header + additional values) at the beginning of the original content
                with open(save_file_name, "wb") as file:
                    file.write(self.original_content[:self.find_header_end()] + original_content)

                QMessageBox.information(self, "Saved", f"Appended file saved as: {os.path.basename(save_file_name)}")
                self.clear_all()

    def preview_appended_header(self):
        if not self.edited_header:
            QMessageBox.warning(self, "Error", "No header data available to preview.")
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select OPUS File for Preview", "", "Opus Files (*.opus);;All Files (*)", options=options)
        if file_name:
            with open(file_name, "rb") as file:
                original_content = file.read()

            preview_content = self.original_content[:self.find_header_end()] + original_content
            preview_hex_view = '\n'.join(
                ' '.join(
                    [preview_content[i+j:i+j+4].hex().upper() for j in range(0, 32, 4)]
                ) for i in range(0, min(160, len(preview_content)), 32)
            )

            if len(preview_content) > 160:
                preview_hex_view += "\n..."

            preview_window = QTextEdit(readOnly=True, font=QFont("Consolas", 10))
            preview_window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            preview_window.setStyleSheet("background-color: rgba(255, 255, 255, 0.8);")
            preview_window.setText(preview_hex_view)

            preview_dialog = QMainWindow(self)
            preview_dialog.setWindowTitle("Header Preview")
            preview_dialog.setCentralWidget(preview_window)
            preview_dialog.setGeometry(100, 100, 1600, 800)
            preview_dialog.show()

    def clear_all(self):
        # Clear all UI components and reset state
        self.loaded_file_name = ""
        self.edited_header = b""
        self.hex_view.clear()
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        self.header_info_label.setText("No header loaded")
        self.setWindowTitle("Opus Header Injector")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    injector = OpusHeaderInjector()
    sys.exit(app.exec_())
