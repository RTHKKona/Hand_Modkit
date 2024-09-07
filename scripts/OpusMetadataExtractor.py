# Opus Metadata Extractor
# Version management
VERSION = "1.1.0"

import os
import sys
import subprocess
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import json
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTextEdit, 
    QApplication, QLabel, QMessageBox, QAction, QMenu, QMenuBar
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QPoint
from tabulate import tabulate

class OpusMetadataExtractor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Start in dark mode by default
        self.base_directory = os.path.dirname(os.path.abspath(__file__))
        self.meta_dep_data_folder = os.path.join(self.base_directory, "MetaDepData")
        self.license_file = os.path.join(self.meta_dep_data_folder, "vgm_COPYING.txt")
        self.first_launch = True
        self.dependencies_file = os.path.join(self.meta_dep_data_folder, "OpusMetaDependencies.txt")
        self.vgmstream_cli = os.path.join(self.meta_dep_data_folder, "vgmstream-cli.exe")
        self.dependencies_valid = False
        self.metadata_list = []  # Store metadata after processing
        self.init_ui()
        self.apply_initial_theme()  # Apply the initial theme
        self.check_dependencies()

    def init_ui(self):
        main_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()

        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 11))  # Set monospaced font for CMD style
        main_layout.addWidget(self.log_output)

        # Create buttons with consistent font size and buffer
        button_font = QFont()
        button_font.setPointSize(11)  # Set the font size for all buttons

        # Create a menu bar
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        help_menu = menubar.addMenu("Help")
        help_action = QAction("About", self)
        help_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(help_action)

        self.browse_button = QPushButton("Browse .Opus Files", self)
        self.browse_button.setFont(button_font)
        self.browse_button.setStyleSheet("QPushButton { padding: 20px; }")  # Apply 20px buffer
        self.browse_button.clicked.connect(self.open_file)
        self.browse_button.setAcceptDrops(True)
        self.browse_button.setEnabled(False)  # Initially disabled until dependency check passes
        self.browse_button.dragEnterEvent = self.dragEnterEvent
        self.browse_button.dragLeaveEvent = self.dragLeaveEvent
        self.browse_button.dropEvent = self.dropEvent
        bottom_layout.addWidget(self.browse_button)

        export_button = QPushButton("Export Data", self)
        export_button.setFont(button_font)
        export_button.setStyleSheet("QPushButton { padding: 20px; }")  # Apply 20px buffer
        export_button.setEnabled(False)  # Initially disabled until metadata is processed
        export_button.clicked.connect(self.show_export_menu)
        self.export_button = export_button
        bottom_layout.addWidget(export_button)

        help_button = QPushButton("Help", self)
        help_button.setFont(button_font)
        help_button.setStyleSheet("QPushButton { padding: 20px; }")  # Apply 20px buffer
        help_button.clicked.connect(self.show_help)
        bottom_layout.addWidget(help_button)

        self.toggle_theme_btn = QPushButton("Toggle Theme", self)
        self.toggle_theme_btn.setFont(button_font)
        self.toggle_theme_btn.setStyleSheet("QPushButton { padding: 20px; }")  # Apply 20px buffer
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        bottom_layout.addWidget(self.toggle_theme_btn)

        main_layout.addLayout(bottom_layout)
        central_widget = QLabel(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle('Opus Metadata Extractor')
        self.setGeometry(100, 100, 1600, 800)  # Set the window size to 1600x800, positioned at 100,100
        
    
    def show_about_dialog(self):
        about_text = (
            "Opus Metadata Extractor\n"
            f"Version {VERSION}\n\n"
            "Extracts metadata from Opus audio files."
        )
        QMessageBox.about(self, "About", about_text)

    def check_dependencies(self):
        """
        Checks the dependencies listed in OpusMetaDependencies.txt and logs the result.
        If all dependencies are valid, enables the browse button; otherwise, shows an error.
        """
        self.log("Starting dependency check...\n")

        if not os.path.exists(self.dependencies_file):
            self.log(f"Error: Dependency list file '{self.dependencies_file}' not found.\n")
            return

        self.log(f"Dependency list file '{self.dependencies_file}' found. Checking each dependency...\n")
        
        missing_dependencies = []

        with open(self.dependencies_file, 'r') as file:
            dependencies = [line.strip() for line in file.readlines()]

        for dependency in dependencies:
            dependency_path = os.path.join(self.meta_dep_data_folder, dependency)
            if os.path.exists(dependency_path):
                self.log(f"[✔] Dependency '{dependency}' found at '{dependency_path}'.")
            else:
                self.log(f"[✘] Dependency '{dependency}' is missing.")
                missing_dependencies.append(dependency)

        if missing_dependencies:
            self.log("\nDependency check failed. The following dependencies are missing:\n")
            for dep in missing_dependencies:
                self.log(f" - {dep}")
            self.show_dependency_error(missing_dependencies)
        else:
            self.log("\nAll dependencies found. Dependency check complete.\n")
            self.dependencies_valid = True
            self.browse_button.setEnabled(True)
        
        if self.first_launch:
            self.show_license()
            self.first_launch = False
            
    def show_license(self):
        ### Show LICENSE on first launch
        if os.path.exists(self.license_file):
            with open(self.license_file, 'r') as file:
                license_text = file.read()
            self.log("[INFO] Displaying License:\n" + license_text)
        else:
            self.log("[ERROR] vgm_COPYING.txt License file not found.")
    

    def show_dependency_error(self, missing_dependencies):
        """
        Displays an error message with missing dependencies and a link to the GitHub repository.
        """
        message = (
            f"The following dependencies are missing:\n{', '.join(missing_dependencies)}\n\n"
            f"Please download the missing files from the GitHub repository:\n"
            "https://github.com/RTHKKona/Hand_Modkit/tree/main/scripts"
        )
        error_box = QMessageBox(self)
        error_box.setWindowTitle("Missing Dependencies")
        error_box.setText(message)
        error_box.setStandardButtons(QMessageBox.Ok)

        # Apply the current theme to the error box
        if self.dark_mode:
            error_box.setStyleSheet("""
                QMessageBox { background-color: #2b2b2b; color: #ffebcd; }
                QPushButton { background-color: #4d4d4d; color: #ffebcd; }
            """)
        else:
            error_box.setStyleSheet("")

        error_box.exec_()

    def show_help(self):
        help_text = (
            "1. Select the .opus files you want to extract metadata from.\n"
            "2. Drag and drop the files onto the Opus Metadata Extractor tab.\n"
            "3. The metadata will be processed and displayed in the output log.\n"
            "4. You can choose to save the metadata in CSV, JSON, or XML format."
        )
        help_box = QMessageBox(self)
        help_box.setWindowTitle("Help")
        help_box.setText(help_text)
        help_box.setStandardButtons(QMessageBox.Ok)

        # Apply the current theme to the help box
        if self.dark_mode:
            help_box.setStyleSheet("""
                QMessageBox { background-color: #2b2b2b; color: #ffebcd; }
                QPushButton { background-color: #4d4d4d; color: #ffebcd; }
            """)
        else:
            help_box.setStyleSheet("")

        help_box.exec_()

    def open_file(self):
        if not self.dependencies_valid:
            return  # Don't allow opening files if dependencies aren't valid

        files, _ = QFileDialog.getOpenFileNames(self, "Open .Opus Files", "", "Opus Files (*.opus);;All Files (*)")
        if files:
            self.log(f"Selected Files: {', '.join(files)}")
            self.extract_metadata(files)
            self.export_button.setEnabled(True)  # Enable the export button after processing

    def dragEnterEvent(self, event):
        if not self.dependencies_valid:
            return  # Don't allow dragging if dependencies aren't valid

        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.browse_button.setText(f"Import {event.mimeData().urls()[0].fileName()}")
            self.browse_button.setStyleSheet("""
                QPushButton {
                    border: 2px solid #FFD700;
                    padding: 30px 10px;  /* Increase padding when dragging */
                }
            """)

    def dragLeaveEvent(self, event):
        self.browse_button.setText("Browse .Opus Files")
        self.browse_button.setStyleSheet("QPushButton { padding: 20px; }")

    def dropEvent(self, event):
        if not self.dependencies_valid:
            return  # Don't allow dropping if dependencies aren't valid

        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.log(f"Selected Files: {', '.join(files)}")
        self.browse_button.setText("Browse .Opus Files")
        self.browse_button.setStyleSheet("QPushButton { padding: 20px; }")
        self.extract_metadata(files)
        self.export_button.setEnabled(True)  # Enable the export button after processing

    def extract_metadata(self, files):
        try:
            self.metadata_list = self.process_files(files)

            # Preview the metadata in the CLI format
            self.preview_metadata(self.metadata_list)

        except Exception as e:
            self.log(f"Error during metadata extraction: {e}")

    def extract_metadata_single(self, opus_file):
        try:
            # Run vgmstream-cli.exe to extract metadata
            result = subprocess.run(
                [self.vgmstream_cli, "-m", opus_file],
                capture_output=True,
                text=True
            )
            return opus_file, result.stdout
        except Exception as e:
            return opus_file, f"Error: {e}"

    def process_files(self, opus_files):
        metadata_list = []

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            future_to_file = {executor.submit(self.extract_metadata_single, file): file for file in opus_files}
            for future in as_completed(future_to_file):
                opus_file, metadata_raw = future.result()
                self.log(f"[INFO] Processing complete for: {opus_file}")
                metadata = self.parse_metadata(metadata_raw)

                # Modify 'File' to only include the second-to-last folder and file name
                file_path_parts = os.path.normpath(opus_file).split(os.sep)
                if len(file_path_parts) >= 2:
                    folder_name = file_path_parts[-2]
                    file_name = file_path_parts[-1]
                    metadata['File'] = f"{folder_name}~\\{file_name}"
                else:
                    metadata['File'] = opus_file  # Fallback to full path if structure is unexpected

                # Add custom metadata
                metadata['Size of File (Bytes)'] = os.path.getsize(opus_file)
                metadata['Loop Start (Samples)'] = ""  # Placeholder for loop start
                metadata['Loop End (Samples)'] = ""  # Placeholder for loop end

                metadata_list.append(metadata)

        return metadata_list

    def parse_metadata(self, metadata):
        metadata_dict = {}
        lines = metadata.splitlines()
        for line in lines:
            # Match lines in the format "key: value"
            match = re.match(r"^\s*(.*?):\s*(.*)$", line)
            if match:
                key = match.group(1).strip().lower()
                value = match.group(2).strip()

                # Process specific keys
                if key == "play duration":
                    value = re.match(r"\d+", value).group(0)  # Keep only the first integer
                    key = "Number of Samples"  # Rename the key
                elif key == "sample rate":
                    value = re.match(r"\d+", value).group(0)  # Keep only the integer
                    key = "Sample Rate (Hz)"  # Rename the key
                elif key == "bitrate":
                    value = re.match(r"\d+", value).group(0)  # Keep only the integer
                    key = "Bitrate (kbps)"  # Rename the key
                elif key in ["channel mask", "layout", "metadata for c", "encoding", "stream total samples"]:
                    continue  # Skip these keys
                elif key == "channels":
                    key = "Channels"  # Capitalize the key

                metadata_dict[key] = value

        return metadata_dict

    def preview_metadata(self, metadata_list):
        # Display a preview of the metadata in the CLI
        self.log("\nMetadata Preview:")
        preview_data = []
        for metadata in metadata_list:
            preview_row = {key: metadata.get(key, "") for key in ["File", "Size of File (Bytes)", "Number of Samples", "Channels", "Sample Rate (Hz)"]}
            preview_data.append(preview_row)

        # Use tabulate for better CLI table formatting
        self.log(tabulate(preview_data, headers="keys", tablefmt="grid"))

    def show_export_menu(self):
        if not self.metadata_list:
            self.log("[ERROR] No metadata to export.")
            return

        menu = QMenu(self)
        menu.addAction("CSV", lambda: self.export_data("csv"))
        menu.addAction("JSON", lambda: self.export_data("json"))
        menu.addAction("XML", lambda: self.export_data("xml"))

        menu.exec_(self.export_button.mapToGlobal(QPoint(0, self.export_button.height())))

    def export_data(self, format_choice):
        # Determine file extension and description
        if format_choice == "json":
            file_extension = ".json"
            file_type_description = "JSON Files"
        elif format_choice == "xml":
            file_extension = ".xml"
            file_type_description = "XML Files"
        else:
            file_extension = ".csv"
            file_type_description = "CSV Files"

        # Open file dialog to choose save location
        output_file, _ = QFileDialog.getSaveFileName(self, "Save File", f"{file_type_description}{file_extension}", f"{file_type_description} (*{file_extension})")
        if not output_file:
            self.show_error_message("No file location selected. Exiting.")
            return

        # Save the file in the chosen format
        if format_choice == "json":
            self.save_as_json(self.metadata_list, output_file)
        elif format_choice == "xml":
            self.save_as_xml(self.metadata_list, output_file)
        else:
            self.save_as_csv(self.metadata_list, output_file)

    def save_as_csv(self, metadata_list, output_file):
        # Reordered and Capitalized Headers
        fieldnames = ["File", "Size of File (Bytes)", "Number of Samples", "Channels", "Sample Rate (Hz)", "Loop Start (Samples)", "Loop End (Samples)"]
        try:
            with open(output_file, mode="w", newline='', encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for metadata in metadata_list:
                    filtered_metadata = {key: metadata.get(key, "") for key in fieldnames}
                    writer.writerow(filtered_metadata)
            self.log(f"[INFO] Metadata saved to CSV: {output_file}")
        except Exception as e:
            self.log(f"[ERROR] Failed to save CSV: {e}")

    def save_as_json(self, metadata_list, output_file):
        try:
            with open(output_file, "w", encoding="utf-8") as jsonfile:
                json.dump(metadata_list, jsonfile, indent=4)
            self.log(f"[INFO] Metadata saved to JSON: {output_file}")
        except Exception as e:
            self.log(f"[ERROR] Failed to save JSON: {e}")

    def save_as_xml(self, metadata_list, output_file):
        try:
            root = ET.Element("Metadata")
            for metadata in metadata_list:
                file_element = ET.SubElement(root, "File")
                for key, value in metadata.items():
                    element = ET.SubElement(file_element, key.replace(" ", "_"))
                    element.text = str(value)
            tree = ET.ElementTree(root)
            tree.write(output_file, encoding="utf-8", xml_declaration=True)
            self.log(f"[INFO] Metadata saved to XML: {output_file}")
        except Exception as e:
            self.log(f"[ERROR] Failed to save XML: {e}")

    def show_error_message(self, message):
        error_box = QMessageBox(self)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.setStandardButtons(QMessageBox.Ok)

        # Apply the current theme to the error box
        if self.dark_mode:
            error_box.setStyleSheet("""
                QMessageBox { background-color: #2b2b2b; color: #ffebcd; }
                QPushButton { background-color: #4d4d4d; color: #ffebcd; }
            """)
        else:
            error_box.setStyleSheet("")

        error_box.exec_()

    def log(self, message):
        self.log_output.append(message)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_initial_theme(self):
        self.apply_theme()

    def apply_theme(self):
        stylesheet = """
            QMainWindow { background-color: #2b2b2b; color: #ffebcd; }
            QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
            QLabel { color: #ffebcd; }
            QPushButton { background-color: #4d4d4d; color: #ffebcd; }
        """ if self.dark_mode else ""
        self.setStyleSheet(stylesheet)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = OpusMetadataExtractor()
    window.show()

    # Start the application event loop
    sys.exit(app.exec_())
