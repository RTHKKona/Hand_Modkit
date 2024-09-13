# Opus Header Injector
# Version management
VERSION = "1.1.0"

import sys,struct,os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QAction, QMessageBox, QSizePolicy, QLabel, QMenuBar
)
from PyQt5.QtGui import QFont, QIcon, QColor, QTextCharFormat
from PyQt5.QtCore import Qt

class OpusHeaderInjector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Start in dark mode by default
        self.loaded_file_name = ""
        self.edited_header = b""
        self.is_second_file_loaded = False  # Clearer naming
        self.headers = [
            "Stream Total Samples", "Number of Channels", "Loop Start (samples)", "Loop End (samples)"
        ]  # Removed 'Buffer' and 'Unknown' headers
        self.full_headers = [
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
        self.loaded_file_label = QLabel("No file loaded   ", self)
        self.header_info_label = QLabel("      No header loaded", self)
        self.help_button = QPushButton("Help", self)
        top_layout.addWidget(self.loaded_file_label)
        top_layout.addWidget(self.header_info_label)
        top_layout.addStretch()
        top_layout.addWidget(self.help_button)
        self.help_button.setGeometry(10, 10, 80, 30)
        self.help_button.clicked.connect(self.show_help)
        top_widget = QWidget()
        top_widget.setLayout(top_layout)

        # Create a menu bar
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        help_menu = menubar.addMenu("Help")
        help_action = QAction("About", self)
        help_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(help_action)

        # Text Box for Hex Data (Displaying the header)
        self.hex_view = QTextEdit(self, readOnly=True, font=QFont("Consolas", 11))  # Increased font size by 1
        self.hex_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Grid for Editing int32 Data
        self.header_table = QTableWidget(self)  # Renamed to indicate header table
        self.header_table.setColumnCount(4)  # Show only 4 headers
        self.header_table.setHorizontalHeaderLabels(self.headers)
        self.header_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.header_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section{
                background-color: #ffebcd;
                color: #000000;
                font-family: Consolas; font: 11pt;
                margin: 2px;
            }
        """)
        self.header_table.setEditTriggers(QTableWidget.AllEditTriggers)

        splitter.addWidget(self.hex_view)
        splitter.addWidget(self.header_table)

        button_layout = QHBoxLayout()


        self.load_button = QPushButton("Load .Opus File", self)
        self.load_button.clicked.connect(self.load_file)
        button_layout.addWidget(self.load_button)

        self.export_button = QPushButton("Export Header", self)  # Updated name
        self.export_button.clicked.connect(self.export_header)
        button_layout.addWidget(self.export_button)

        self.inject_button = QPushButton("Inject Header to New .Opus", self)  # Updated name
        self.inject_button.clicked.connect(self.inject_header)
        button_layout.addWidget(self.inject_button)

        self.preview_button = QPushButton("Preview Injected Header", self)  # Updated name
        self.preview_button.clicked.connect(self.preview_injected_header)
        button_layout.addWidget(self.preview_button)

        self.clear_button = QPushButton("Clear Headers", self)
        self.clear_button.clicked.connect(self.clear_headers)
        button_layout.addWidget(self.clear_button)

        self.theme_button = QPushButton("Toggle Theme", self)  # Updated name
        self.theme_button.clicked.connect(self.toggle_theme)
        button_layout.addWidget(self.theme_button)

        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(top_widget)
        main_layout.addWidget(splitter)
        main_layout.addLayout(button_layout)

        self.init_menu()
        self.apply_styles()  # Apply the initial styles
        self.show()

    def create_themed_messagebox(self, title, text):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)

        # Apply theme-based styles
        if self.dark_mode:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #4d4d4d;
                    color: #ffebcd;
                }
                QPushButton {
                    background-color: #2b2b2b;
                    color: #ffebcd;
                }
            """)
        else:
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: black;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: black;
                }
            """)

        return msg_box

    def clear_headers(self):
        self.loaded_file_name = ""
        self.edited_header = b""
        self.hex_view.clear()
        self.header_table.clearContents()  # Updated to new table name
        self.header_table.setRowCount(0)
        self.header_info_label.setText("No header loaded")
        self.setWindowTitle("Opus Header Injector")
        self.is_second_file_loaded = False
        msg_box = self.create_themed_messagebox("Cleared", "All Data has been cleared successfully.")
        msg_box.exec_()

    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&File")

        open_file_action = QAction("&Open", self)
        open_file_action.triggered.connect(self.load_file)
        file_menu.addAction(open_file_action)

        save_file_action = QAction("&Export Header", self)  # Updated name
        save_file_action.triggered.connect(self.export_header)
        file_menu.addAction(save_file_action)

    def show_about_dialog(self):
        about_text = (
            "Opus Header Injector\n"
            f"Version {VERSION}\n\n"
            "Injects custom headers into Opus audio files."
        )
        msg_box = self.create_themed_messagebox("About", about_text)
        msg_box.exec_()

    def show_help(self):
        help_text = (
            "1. Import the .opus file you want to replace inside of nativeNX.\n\n"
            "2. Press the Load Opus File and open your desired opus file.\n\n"
            "3. Find out and edit your total number of samples of your replacement .opus file. "
            "You can use vgmstream or XMPlay.\n\n"
            "4. Adjust the loop start and loop end times, in samples. Use XMPlay to listen "
            "through and find suitable times for looping.\n\n"
            "5. Export Header & Save. This part is so your edited changes are saved locally and retained.\n\n"
            "6. Press Inject Header to File, and open your headerless .opus file to inject the header data.\n\n"
            "7. Save the new .opus file with your desired changes.\n\n"
            "8. Test your new opus file with correct looping, sample, and header, fit for MHGU."
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
            if self.is_second_file_loaded:
                self.display_second_file_header()
            else:
                self.setWindowTitle(f"Opus Header Injector - Editing: {os.path.basename(file_name)}")
                header_end_offset = self.find_full_header_size()
                self.display_hex_content(header_end_offset)
                self.populate_grid(header_end_offset)
                self.header_info_label.setText(f"   Header Size: {header_end_offset} bytes")
                self.is_second_file_loaded = True
            self.update_loaded_file_label()

    def update_loaded_file_label(self):
        color = "yellow" if self.dark_mode else "darkgreen"
        self.loaded_file_label.setText(f"Loaded File: {self.loaded_file_name}")
        self.loaded_file_label.setStyleSheet(f"color: {color}; font: 10pt; font-weight: bold; font-family: Consolas")

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
        
        # Display the hex code up to the header end offset
        for i in range(0, min(header_end_offset, len(self.original_content)), 32):
            row = ' '.join(
                [self.original_content[i + j:i + j + 4].hex().upper() for j in range(0, 32, 4)]
            )
            hex_view.append(row)
        
        # Append a few lines of actual data after the header in a different color (#353535)
        num_additional_lines = 3  # Same as the original number of fake lines
        for i in range(header_end_offset, header_end_offset + (num_additional_lines * 32), 32):
            if i < len(self.original_content):
                row = ' '.join(
                    [self.original_content[i + j:i + j + 4].hex().upper() for j in range(0, 32, 4)]
                )
                # Wrap the additional rows with HTML for the color
                hex_view.append(f'<span style="color:#353535">{row}</span>')
            else:
                # Stop if we reach the end of the file content
                break

        # Add an ellipsis at the end to indicate that it's just a preview
        hex_view.append('<span style="color:grey">...</span>')

        # Convert the content into a formatted string for display
        formatted_hex_view = '<br>'.join(hex_view)
        
        # Display the formatted content in the hex view
        self.hex_view.setHtml(formatted_hex_view)

    def populate_grid(self, header_end_offset):
        self.header_table.setRowCount(1)
        for col in range(4):  # Only show first 4 columns
            offset = col * 4
            if offset + 4 <= header_end_offset:
                int_value = struct.unpack('<i', self.original_content[offset:offset+4])[0]
                item = QTableWidgetItem(str(int_value))
                self.header_table.setItem(0, col, item)
        self.header_table.itemChanged.connect(self.on_item_changed)

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

    def export_header(self):  # Updated function name
        if not self.loaded_file_name:
            msg_box = self.create_themed_messagebox("Error", "No file loaded to export.")
            msg_box.exec_()
            return

        base_name = os.path.basename(self.loaded_file_name)
        directory = os.path.dirname(self.loaded_file_name)
        export_file_name = os.path.join(directory, f"new_{base_name}")
        options = QFileDialog.Options()
        export_file_name, _ = QFileDialog.getSaveFileName(self, "Save OPUS File As", export_file_name, "Opus Files (*.opus);;All Files (*)", options=options)
        if export_file_name:
            self.edited_header = bytearray(self.original_content[:48])
            for col in range(4):  # Only update first 4 headers
                item = self.header_table.item(0, col)
                if item:
                    value = int(item.text())
                    offset = col * 4
                    hex_value = struct.pack('<i', value)
                    self.edited_header[offset:offset+4] = hex_value

            with open(export_file_name, "wb") as file:
                file.write(self.edited_header)

            msg_box = self.create_themed_messagebox("Saved", f"File saved as: {os.path.basename(export_file_name)}")
            self.is_second_file_loaded = False  # Allow next file loading

    def inject_header(self):  # Updated function name
        if not self.edited_header:
            msg_box = self.create_themed_messagebox("Error", "No header data available. Please save the edited header first.")
            msg_box.exec_()
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
                    file.write(self.edited_header + original_content)

                msg_box = self.create_themed_messagebox("Saved", f"Appended file saved as: {os.path.basename(save_file_name)}")
                msg_box.exec_()
                self.clear_headers()

    def preview_injected_header(self):  # Updated function name
        if not self.edited_header:
            msg_box = self.create_themed_messagebox("Error", "No header data available to preview.")
            msg_box.exec_()
            return

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select OPUS File for Preview", "", "Opus Files (*.opus);;All Files (*)", options=options)
        if file_name:
            with open(file_name, "rb") as file:
                original_content = file.read()

            preview_content = self.edited_header + original_content
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
        # Common styles (applies to both dark and light modes)
        common_styles = """
            QPushButton {
                font-family: Consolas;
                font-size: 12pt;
                padding: 6px;
                border-style: outset;
            }
            QPushButton::hover {
                border-style:  inset;
            }
        """
        
        # Dark mode-specific styles
        dark_mode_styles = """
            QMainWindow { background-color: #2b2b2b; color: #ffebcd; }
            QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
            QLabel { color: #ffebcd; }
            QPushButton { background-color: #4d4d4d; color: #ffebcd; border:  3px solid #ffebcd; }
            QPushButton::hover {background-color: #ffebcd; color: #000000;}
            QTableWidget { background-color: #4d4d4d; color: #ffebcd; gridline-color: white; }
            QHeaderView::section { background-color: grey; color: white; }
        """
        
        # Light mode-specific styles
        light_mode_styles = """
            QMainWindow { background-color: white; color: black; }
            QTextEdit { background-color: white; color: black; }
            QLabel { color: black; }
            QPushButton { background-color: #f0f0f0; color: black; border: 3px solid #cacaca; }
            QPushButton::hover { background-color: #cacaca;}
            QTableWidget { background-color: #f0f0f0; color: black; gridline-color: black; }
            QHeaderView::section { background-color: lightgrey; color: black; }
        """
        
        # Combine common styles with mode-specific styles
        if self.dark_mode:
            full_stylesheet = common_styles + dark_mode_styles
        else:
            full_stylesheet = common_styles + light_mode_styles
        
        # Apply the combined stylesheet
        self.setStyleSheet(full_stylesheet)
        self.update_loaded_file_label()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    injector = OpusHeaderInjector()
    injector.show()
    sys.exit(app.exec_())
