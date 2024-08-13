import sys
import struct
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QAction, QMessageBox, QSizePolicy, QLabel
)
from PyQt5.QtGui import QFont, QIcon, QColor, QTextCharFormat
from PyQt5.QtCore import Qt

class OpusHeaderInjector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Start in dark mode by default
        self.loaded_file_name = ""
        self.edited_header = b""
        self.second_file_loaded = False
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
        self.help_button.setGeometry(10,10,80,30)
        self.help_button.clicked.connect(self.show_help)
        top_widget = QWidget()
        top_widget.setLayout(top_layout)

        # Text Box for Hex Data (Displaying the header)
        self.hex_view = QTextEdit(self, readOnly=True, font=QFont("Consolas", 11))  # Increased font size by 1
        self.hex_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Grid for Editing int32 Data
        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(12)
        self.table_widget.setHorizontalHeaderLabels(self.headers)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_widget.horizontalHeader().setFont(QFont("Arial", weight=QFont.Bold))
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

        self.dark_mode_button = QPushButton("Toggle Theme", self)
        self.dark_mode_button.clicked.connect(self.toggle_theme)
        button_layout.addWidget(self.dark_mode_button)

        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(top_widget)
        main_layout.addWidget(splitter)
        main_layout.addLayout(button_layout)

        self.init_menu()
        self.apply_styles()  # Apply the initial styles
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

    def show_help(self):
        help_text = (
            "1. Import the .opus file you want to replace inside of nativeNX.\n"
            "2. Press the Load Opus File and open your desired opus file.\n"
            "3. Find out and edit your total number of samples of your replacement .opus file. "
            "You can use vgmstream or XMplay with the vgmstream add-on.\n"
            "4. Adjust the loop start and loop end times, in samples. I like to use XMplay to listen "
            "through and find suitable times for looping. See the Audio Calculator tab to convert from "
            "minutes:seconds to samples and vice-versa.\n"
            "5. Save as new file. This part is so then your changes are retained (note this is somewhat buggy, "
            "so keep your changes to the header in a hex editor like HxD.)\n"
            "6. Press Append Header to Another File, and open your headerless .opus file you want to append the data to.\n"
            "7. Save the new completed .opus file with your desired changes.\n"
            "8. Test and listen to your new opus file with correct looping, sample, and header, fit for MHGU."
        )

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Opus Header Injector Help")
        msg_box.setText(help_text)
        if self.dark_mode:
            msg_box.setStyleSheet("QMessageBox { background-color: #4d4d4d; color: #ffebcd; }")
        msg_box.exec_()

    def load_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open OPUS File", "", "Opus Files (*.opus);;All Files (*)", options=options)
        if file_name:
            with open(file_name, "rb") as file:
                self.original_content = file.read()
                self.loaded_file_name = file_name
            if self.second_file_loaded:
                self.display_second_file_header()
            else:
                self.setWindowTitle(f"Opus Header Injector - Editing: {os.path.basename(file_name)}")
                header_end_offset = self.find_full_header_size()
                self.display_hex_content(header_end_offset)
                self.populate_grid(header_end_offset)
                self.header_info_label.setText(f"Header Size: {header_end_offset} bytes")
                self.second_file_loaded = True

    def find_full_header_size(self):
        # Search from the beginning
        start_index = self.original_content.find(self.target_pattern)
        # Search from the end
        end_index = len(self.original_content) - self.original_content[::-1].find(self.target_pattern[::-1])
        if start_index != -1 and end_index != -1 and end_index > start_index:
            return end_index
        return len(self.original_content)

    def display_hex_content(self, header_end_offset):
        hex_view = []
        for i in range(0, min(header_end_offset, len(self.original_content)), 32):
            row = ' '.join(
                [self.original_content[i+j:i+j+4].hex().upper() for j in range(0, 32, 4)]
            )
            hex_view.append(row)

        # Add 3 grey rows after the header
        grey_row = ' '.join(['00' * 4] * 8)
        for _ in range(3):
            hex_view.append(f'<span style="color:grey">{grey_row}</span>')

        self.hex_view.setHtml('<br>'.join(hex_view))

    def populate_grid(self, header_end_offset):
        self.table_widget.setRowCount(1)
        for col in range(12):
            offset = col * 4
            if offset + 4 <= header_end_offset:
                int_value = struct.unpack('<i', self.original_content[offset:offset+4])[0]
                item = QTableWidgetItem(str(int_value))
                if offset >= 48 and offset < header_end_offset:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    item.setForeground(QColor(150, 150, 150))
                self.table_widget.setItem(0, col, item)
        self.table_widget.itemChanged.connect(self.on_item_changed)

    def on_item_changed(self, item):
        row = item.row()
        col = item.column()
        value = int(item.text())
        offset = col * 4
        hex_value = struct.pack('<i', value)
        original_hex = self.original_content[offset:offset+4]

        format = QTextCharFormat()
        if hex_value != original_hex:
            format.setForeground(QColor("yellow") if self.dark_mode else QColor("red"))
        else:
            format.setForeground(QColor("white") if self.dark_mode else QColor("black"))

        cursor = self.hex_view.textCursor()
        cursor.movePosition(cursor.Start)
        cursor.movePosition(cursor.Down, cursor.MoveAnchor, row)
        cursor.movePosition(cursor.Right, cursor.MoveAnchor, col * 8)  # Move to the correct column
        cursor.movePosition(cursor.Right, cursor.KeepAnchor, 8)  # Select the hex string
        cursor.insertText(hex_value.hex().upper(), format)

    def save_file_as(self):
        if not self.loaded_file_name:
            QMessageBox.warning(self, "Error", "No file loaded to save.")
            return

        base_name = os.path.basename(self.loaded_file_name)
        directory = os.path.dirname(self.loaded_file_name)
        save_file_name = os.path.join(directory, f"new_{base_name}")
        options = QFileDialog.Options()
        save_file_name, _ = QFileDialog.getSaveFileName(self, "Save OPUS File As", save_file_name, "Opus Files (*.opus);;All Files (*)", options=options)
        if save_file_name:
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

            base_name = os.path.basename(file_name)
            directory = os.path.dirname(file_name)
            save_file_name = os.path.join(directory, f"new_{base_name}")
            options = QFileDialog.Options()
            save_file_name, _ = QFileDialog.getSaveFileName(self, "Save Appended OPUS File As", save_file_name, "Opus Files (*.opus);;All Files (*)", options=options)
            if save_file_name:
                with open(save_file_name, "wb") as file:
                    file.write(self.original_content[:self.find_full_header_size()] + original_content)

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

            preview_content = self.original_content[:self.find_full_header_size()] + original_content
            preview_hex_view = '\n'.join(
                ' '.join(
                    [preview_content[i+j:i+j+4].hex().upper() for j in range(0, 32, 4)]
                ) for i in range(0, min(160, len(preview_content)), 32)
            )

            if len(preview_content) > 160:
                preview_hex_view += "\n..."

            preview_window = QTextEdit(readOnly=True, font=QFont("Consolas", 11))  # Increased font size by 1
            preview_window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            preview_window.setHtml(preview_hex_view)

            preview_dialog = QMainWindow(self)
            preview_dialog.setWindowTitle("Header Preview")
            preview_dialog.setCentralWidget(preview_window)
            preview_dialog.setGeometry(100, 100, 1600, 800)
            preview_dialog.show()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_styles()

    def apply_styles(self):
        style = """
            QMainWindow { background-color: #2b2b2b; color: #ffebcd; }
            QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
            QLabel { color: #ffebcd; }
            QPushButton { background-color: #4d4d4d; color: #ffebcd; }
            QTableWidget { background-color: #4d4d4d; color: #ffebcd; gridline-color: white; }
            QHeaderView::section { background-color: grey; color: white; }
        """ if self.dark_mode else ""

        self.setStyleSheet(style)

    def clear_all(self):
        self.loaded_file_name = ""
        self.edited_header = b""
        self.hex_view.clear()
        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        self.header_info_label.setText("No header loaded")
        self.setWindowTitle("Opus Header Injector")
        self.second_file_loaded = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    injector = OpusHeaderInjector()
    injector.show()
    sys.exit(app.exec_())
