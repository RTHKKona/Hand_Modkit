# MCA Forge
# Version management
VERSION = "0.5.5"

import os, sys, subprocess, binascii, shutil
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTextEdit, 
    QLabel, QMessageBox, QAction, QMenuBar, QDialog, QFormLayout, QLineEdit, QPushButton
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

class MCA_Forge(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.original_mca_file = None
        self.replacement_mca_file = None
        self.init_ui()
        self.apply_initial_theme()

    def init_ui(self):
        main_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 11))
        main_layout.addWidget(self.log_output)

        button_font = QFont()
        button_font.setPointSize(11)
        
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        help_menu = menubar.addMenu("Help")
        help_action = QAction("About", self)
        help_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(help_action)

        self.import_original_button = QPushButton("Import Original MHGU .MCA", self)  # Renamed button
        self.import_original_button.setFont(button_font)
        self.import_original_button.setStyleSheet("QPushButton { padding: 10px; }")
        self.import_original_button.clicked.connect(self.open_original_mca_file)
        bottom_layout.addWidget(self.import_original_button)

        self.import_replacement_button = QPushButton("Import Replacement New .MCA", self)  # Renamed button
        self.import_replacement_button.setFont(button_font)
        self.import_replacement_button.setStyleSheet("QPushButton { padding: 10px; }")
        self.import_replacement_button.clicked.connect(self.open_replacement_mca_file)
        bottom_layout.addWidget(self.import_replacement_button)

        apply_button = QPushButton("Apply Headers", self)
        apply_button.setFont(button_font)
        apply_button.setStyleSheet("QPushButton { padding: 10px; }")
        apply_button.clicked.connect(self.apply_headers)
        bottom_layout.addWidget(apply_button)

        theme_button = QPushButton("Change Theme", self)
        theme_button.setFont(button_font)
        theme_button.setStyleSheet("QPushButton { padding: 10px; }")
        theme_button.clicked.connect(self.toggle_theme)
        bottom_layout.addWidget(theme_button)

        main_layout.addLayout(bottom_layout)
        central_widget = QLabel(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle('MCA Forge')
        self.setGeometry(100, 100, 1600, 800)

    def open_original_mca_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Open Original MHGU .MCA File", "", "MCA Files (*.mca);;All Files (*)")
        if files:
            self.original_mca_file = files[0]
            self.log(f"[INFO] Selected Original MHGU MCA File: {self.original_mca_file}")
            self.display_header(self.original_mca_file, header_size=0x78)

    def open_replacement_mca_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Open Replacement New .MCA File", "", "MCA Files (*.mca);;All Files (*)")
        if files:
            self.replacement_mca_file = files[0]
            self.log(f"[INFO] Selected Replacement MCA File: {self.replacement_mca_file}")
            self.display_header(self.replacement_mca_file, header_size=0xB0)

    def display_header(self, file_path, header_size):
        with open(file_path, 'rb') as f:
            header = f.read(header_size)
        
        hex_output = binascii.hexlify(header).decode('utf-8').upper()
        formatted_output = ""
        for i in range(0, len(hex_output), 64):
            row = ' '.join([hex_output[j:j+8] for j in range(i, i+64, 8)])
            formatted_output += row + '\n'
        
        self.log_output.append(f"Header from {file_path}:\n" + formatted_output)

    def apply_headers(self):
        if not self.original_mca_file or not self.replacement_mca_file:
            self.log("[ERROR] Please select both Original and Replacement MCA files.")
            QMessageBox.warning(self, "Missing Files", "You must select both MCA files before applying headers.")
            return

        # Validate magic numbers
        if not self.validate_header(self.original_mca_file, '02000000', 'Original'):
            return
        if not self.validate_header(self.replacement_mca_file, '4D414450', 'Replacement'):
            return

        # Check if the replacement MCA already has the Capcom .ADPCM header
        if self.check_replacement_header():
            return  # Stop further processing if the header is already correct

        total_samples, ok = self.get_total_samples()
        if ok:
            if self.validate_total_samples(total_samples):
                self.log(f"[INFO] Total Samples: {total_samples}")
                self.modify_header(total_samples)
            else:
                self.log("[ERROR] Invalid Total Samples value provided.")
        else:
            self.log("[ERROR] No total samples provided.")

    def check_replacement_header(self):
        """Check if the replacement MCA already has the Capcom .ADPCM header."""
        try:
            with open(self.replacement_mca_file, 'rb') as f:
                header = f.read(0xB0)
                expected_header = b'\x02\x00\x00\x00\x01\x00\x00\x01'  # Example of what the header should be
                if header[:8] == expected_header:
                    QMessageBox.information(self, "Header Check", "Replacement MCA Header is already Capcom .ADPCM Header.")
                    self.log("[INFO] Replacement MCA Header is already Capcom .ADPCM Header.")
                    return True
        except Exception as e:
            self.log(f"[ERROR] Failed to check replacement MCA header: {e}")
        return False

    def get_total_samples(self):
        ## Create a custom input dialog to capture total samples
        dialog = QDialog(self)
        dialog.setWindowTitle("Input Total Samples")
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.setStyleSheet("background-color: #4d4d4d; color: #ffebcd;")
        
        layout = QFormLayout(dialog)

        total_samples_input = QLineEdit()
        total_samples_input.setFont(QFont("Consolas", 12))
        layout.addRow("Total Samples:", total_samples_input)

        button_box = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        layout.addRow(button_box)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            try:
                return int(total_samples_input.text()), True
            except ValueError:
                QMessageBox.critical(self, "Invalid Input", "Please enter a valid integer.")
                return None, False
        else:
            return None, False

    def validate_total_samples(self, total_samples):
        ## Validate the total samples input
        if total_samples <= 0:
            QMessageBox.critical(self, "Invalid Input", "Total Samples cannot be 0 or negative.")
            return False
        if total_samples > 2147483647:  # Max value for 32-bit signed integer
            QMessageBox.critical(self, "Invalid Input", "Total Samples exceeds the 32-bit integer overflow limit.")
            return False
        return True

    def modify_header(self, total_samples):
        try:
            # Read headers from the original and replacement MCA files
            with open(self.original_mca_file, 'rb') as orig_file:
                original_header = orig_file.read(0x78)

            with open(self.replacement_mca_file, 'rb') as repl_file:
                replacement_header = repl_file.read(0xB0)

            # Modify header logic here: constructing new headers
            new_header = b'\x02\x00\x00\x00\x01\x00\x00\x01'
            new_header += replacement_header[12:16]
            new_header += original_header[12:16]
            new_header += original_header[16:24]
            new_header += replacement_header[56:88]
            new_header += b'\x00' * 40  # Padding

            # Insert total samples as ZZZZ0000
            zzzz_hex = total_samples.to_bytes(4, byteorder='little', signed=True)
            new_header += zzzz_hex
            new_header += original_header[100:104]  # Dynamic 80BB0000 from original MCA
            new_header += b'\x00' * 8
            yyyy_hex = (total_samples - 1).to_bytes(4, byteorder='little', signed=True)
            new_header += yyyy_hex
            new_header += b'\x00' * 4  # Final padding

            # Display the modified header in coloured format
            self.display_coloured_hex(original_header, replacement_header, total_samples)

            # Inject the new header
            self.inject_header(new_header)

        except Exception as e:
            self.log(f"[ERROR] Failed to modify header: {e}")

    def display_coloured_hex(self, original_header, replacement_header, total_samples):
        coloured_output = []
        column_count = 0

        def add_coloured_hex(hex_string, colour):
            nonlocal column_count
            coloured_output.append(self.colour_hex(hex_string, colour) + " ")
            column_count += 1
            if column_count == 8:
                coloured_output.append("<br>")
                column_count = 0

        # Colour-coding sections based on their origin
        add_coloured_hex("02000000", "#E6E6FA")  # Lavender for first 4 bytes
        add_coloured_hex("01000001", "#E6E6FA")  # Lavender for second 4 bytes
        add_coloured_hex(binascii.hexlify(replacement_header[12:16]).decode('utf-8'), "#FFA500")  # XXXXXXXX (orange)
        add_coloured_hex(binascii.hexlify(original_header[12:16]).decode('utf-8'), "#00FF00")  # AAAAAAAA (green)
        add_coloured_hex(binascii.hexlify(original_header[16:20]).decode('utf-8'), "#40E0D0")  # First part of turquoise
        add_coloured_hex(binascii.hexlify(original_header[20:24]).decode('utf-8'), "#40E0D0")  # Second part of turquoise

        # Special hex lines from replacement MCA (yellow)
        for i in range(56, 88, 4):
            add_coloured_hex(binascii.hexlify(replacement_header[i:i+4]).decode('utf-8'), "#FFFF00")

        # Padding (grey)
        for _ in range(10):
            add_coloured_hex("00000000", "#A9A9A9")

        # ZZZZ0000 (red) and constant + padding
        zzzz_hex = total_samples.to_bytes(4, byteorder='little', signed=True)
        add_coloured_hex(binascii.hexlify(zzzz_hex).decode('utf-8'), "#FF0000")
        add_coloured_hex(binascii.hexlify(original_header[100:104]).decode('utf-8'), "#FFD700")  # Dynamic 80BB0000 from original MCA
        add_coloured_hex("00000000", "#A9A9A9")
        add_coloured_hex("00000000", "#A9A9A9")

        # YYYY0000 (red) and final padding
        yyyy_hex = (total_samples - 1).to_bytes(4, byteorder='little', signed=True)
        add_coloured_hex(binascii.hexlify(yyyy_hex).decode('utf-8'), "#FF0000")
        add_coloured_hex("00000000", "#A9A9A9")

        self.log_output.append("".join(coloured_output))

    def colour_hex(self, hex_string, colour):
        return f'<span style="color:{colour};">{hex_string.upper()}</span>'

    def inject_header(self, new_header):
        try:
            # Backup the original replacement MCA
            backup_path = self.replacement_mca_file + ".backup"
            shutil.copyfile(self.replacement_mca_file, backup_path)
            self.log(f"[INFO] Backup created: {backup_path}")

            # Replace header in the replacement MCA
            with open(self.replacement_mca_file, 'r+b') as repl_file:
                repl_file.seek(0)
                repl_file.write(new_header)
                self.log("[INFO] Header injected into replacement MCA.")

            # Notify user
            QMessageBox.information(self, "Header Injection Complete", "The new header has been successfully injected.")
            subprocess.Popen(f'explorer /select,"{os.path.abspath(self.replacement_mca_file)}"')

        except Exception as e:
            self.log(f"[ERROR] Failed to inject header: {e}")

    def validate_header(self, file_path, expected_magic_number, file_type):
        ## Check if the magic number (first 4 bytes) of a file matches the expected hex value.
        try:
            with open(file_path, 'rb') as f:
                file_header = f.read(4)  # Only read the first 4 bytes (magic number)
                if binascii.hexlify(file_header).decode('utf-8').upper() != expected_magic_number:
                    self.log(f"[ERROR] {file_type} MCA file magic number does not match the expected value.")
                    QMessageBox.critical(self, "Header Mismatch", f"{file_type} MCA file has an unexpected magic number.")
                    return False
        except Exception as e:
            self.log(f"[ERROR] Failed to read {file_type} MCA file magic number: {e}")
            return False
        return True

    def show_about_dialog(self):
        about_text = (
            f"MCA Forge Version {VERSION}<br><br>" 
            "MCA Header Forge allows users to import two MCA files—an original and a replacement—and merge key elements to create a new custom header with a preset Capcom .ADPCM header structure."
        )
        QMessageBox.about(self, "About", about_text)

    def log(self, message):
        self.log_output.append(message)
        self.log_output.ensureCursorVisible()

    def apply_initial_theme(self):
        self.apply_theme()

    def apply_theme(self):
        stylesheet = """
            QMainWindow { background-color: #2b2b2b; color: #ffebcd; }
            QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
            QPushButton { background-color: #4d4d4d; color: #ffebcd; }
        """ if self.dark_mode else """
            QMainWindow { background-color: #f0f0f0; color: #000000; }
            QTextEdit { background-color: #ffffff; color: #000000; }
            QPushButton { background-color: #ffffff; color: #000000; }
        """
        self.setStyleSheet(stylesheet)
        
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MCA_Forge()
    window.show()
    sys.exit(app.exec_())
