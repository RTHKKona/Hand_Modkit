# NS Opus Converter
# Version management
VERSION = "1.7.6"

import os, sys, shutil, subprocess, webbrowser, random
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTextEdit, QApplication, 
    QLabel, QMessageBox, QAction, QMenuBar
)
from PyQt5.QtGui import QFont

class ns_OpusConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Start in dark mode by default
        self.base_directory = os.path.dirname(os.path.abspath(__file__))
        self.data_folder = os.path.join(self.base_directory, "data")
        self.temp_folder = os.path.join(self.data_folder, "temp_conversion")
        self.output_folder = os.path.abspath(os.path.join(self.base_directory, "..", "ConvertedOpus"))
        self.dependencies_file = os.path.join(self.data_folder, "NSOpusDirectory.txt")
        self.license_file = os.path.join(self.data_folder, "COPYING.GPLv2.txt")
        self.ffmpeg_path = os.path.join(self.data_folder, "ffmpeg.exe")
        self.nxaenc_path = os.path.join(self.data_folder, "NXAenc.exe")
        self.dependencies_valid = False
        self.first_launch = True
        self.init_ui()
        self.apply_initial_theme()  # Apply the initial theme
        
        
    def log(self, message):  # Moved this method above where it's first used
        self.log_output.append(message)
        

    def init_ui(self):
        main_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()

        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 11))  # Set monospaced font for CMD style
        main_layout.addWidget(self.log_output)

        # Create buttons with consistent font size and buffer
        button_font = QFont()
        button_font.setPointSize(12)  # Set the font size for all buttons

        # Create a menu bar
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        help_menu = menubar.addMenu("Help")
        help_action = QAction("About", self)
        help_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(help_action)
        
        self.browse_button = QPushButton("Browse Audio Files", self)
        self.browse_button.setFont(button_font)
        self.browse_button.setStyleSheet("QPushButton { padding: 10px; }")
        self.browse_button.clicked.connect(self.open_file)
        self.browse_button.setAcceptDrops(True)
        self.browse_button.setEnabled(False)  # Initially disabled until dependency check passes
        bottom_layout.addWidget(self.browse_button)

        help_button = QPushButton("Help", self)
        help_button.setFont(button_font)
        help_button.setStyleSheet("QPushButton { padding: 10px; }")
        help_button.clicked.connect(self.show_help)
        bottom_layout.addWidget(help_button)

        self.toggle_theme_btn = QPushButton("Toggle Theme", self)
        self.toggle_theme_btn.setFont(button_font)
        self.toggle_theme_btn.setStyleSheet("QPushButton { padding: 10px; }")
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        bottom_layout.addWidget(self.toggle_theme_btn)

        main_layout.addLayout(bottom_layout)
        central_widget = QLabel(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setWindowTitle('NS Opus Converter')
        self.setGeometry(100, 100, 1600, 800)  # Set the window size to 1600x800, positioned at 100,100

        # Ensure the window is visible before proceeding
        self.show()
        QApplication.processEvents()  # Ensure all events are processed so the window is fully visible
        self.start_print_sequence()

    def show_about_dialog(self):
        about_text = (
            "NS Opus Converter\n"
            f"Version {VERSION}\n\n"
            "Converts various audio files (.mp3, .wav, .flac, .ogg) into valid .Opus audio format used by MHGU."
        )
        QMessageBox.about(self, "About", about_text)

    def start_print_sequence(self):
        if self.first_launch:
            self.show_license_and_dependencies()
            self.first_launch = False

    def show_license_and_dependencies(self):
        # Show LICENSE first, then check dependencies
        if os.path.exists(self.license_file):
            with open(self.license_file, 'r') as file:
                license_text = file.read()
            self.log("[INFO] Displaying License:\n" + license_text)
        else:
            self.log("[ERROR] COPYING.GPLv2.txt License file not found.")

        # Now check dependencies
        self.check_dependencies()

    def check_dependencies(self):
        self.log("\n[INFO] Listing dependencies:\n")

        if not os.path.exists(self.dependencies_file):
            self.log(f"Error: Dependency list file '{self.dependencies_file}' not found.\n")
            return

        self.log(f"Dependency list file '{self.dependencies_file}' found. Checking each dependency...\n")
        
        missing_dependencies = []

        with open(self.dependencies_file, 'r') as file:
            dependencies = [line.strip() for line in file.readlines()]

        for dependency in dependencies:
            dependency_path = os.path.join(self.data_folder, dependency)
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

        self.log("\nBrowse audio files to convert various audio files (mp3, wav, flac) into a valid .Opus audio format used by MHGU.\n\n\n\n\n")

    def show_dependency_error(self, missing_dependencies):
        message = (
            f"The following dependencies are missing:\n{', '.join(missing_dependencies)}\n\n"
            f"Please download the missing files from the GitHub repository:\n"
            "https://github.com/RTHKKona/Hand_Modkit/tree/main/scripts"
        )
        error_box = QMessageBox(self)
        error_box.setWindowTitle("Missing Dependencies")
        error_box.setText(message)
        error_box.setStandardButtons(QMessageBox.Ok)

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
            "1. Pinpoint which .opus files you would like to replace and note them down.\n\n"
            "2. Get your own audio files that you would like to replace, my tool supports mp4, mp3, flac, wav, and ogg.\n\n"
            "3. Browse for them in the NSOpus Converter tab.\n\n"
            "4. Let the conversion occur.\n\n"
            "5. Get your converted MHGU .opus files."
        )
        help_box = QMessageBox(self)
        help_box.setWindowTitle("Help")
        help_box.setText(help_text)
        help_box.setStandardButtons(QMessageBox.Ok)

        # Apply the current theme to the help box
        if self.dark_mode:
            help_box.setStyleSheet("""
                QMessageBox { background-color: #2b2b2b; color: #ffebcd; }
                QPushButton { background-color: #4d4d4d; color: #ffebcd; margin: 2px; border: 2px solid #ffebcd; }

            """)
        else:
            help_box.setStyleSheet("")

        help_box.exec_()

    def open_file(self):
        if not self.dependencies_valid:
            return  # Don't allow opening files if dependencies aren't valid

        files, _ = QFileDialog.getOpenFileNames(self, "Open Audio Files", "", "Audio Files (*.mp3 *.mp4 *.wav *.flac *.ogg);;All Files (*)")
        if files:
            self.log(f"Selected Files: {', '.join(files)}")
            self.convert_to_opus(files)

    def convert_to_opus(self, files):
        if not files:
            self.log("No files selected for conversion.")
            return

        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        try:
            for file in files:
                self.log(f"Processing: {file}")
                self.update_progress(0, f"Starting Conversion...", file)

                temp_wav = os.path.join(self.temp_folder, f"{os.path.basename(file)}_temp.wav")
                resampled_wav = os.path.join(self.temp_folder, f"{os.path.basename(file)}_resampled.wav")
                raw_file = os.path.join(self.temp_folder, f"{os.path.basename(file)}.raw")
                output_file = os.path.join(self.output_folder, f"{os.path.splitext(os.path.basename(file))[0]}.opus")

                if not file.lower().endswith('.wav'):
                    command_convert_wav = f"\"{self.ffmpeg_path}\" -i \"{file}\" \"{temp_wav}\""
                    self.run_command(command_convert_wav, "Detected non .wav, converting to WAV", temp_wav)
                    self.update_progress(int(random.randint(1,10)), "Detected non .wav, converting to WAV", file)
                else:
                    temp_wav = file

                command_resample = f"\"{self.ffmpeg_path}\" -i \"{temp_wav}\" -ar 48000 -ac 2 -hide_banner -loglevel error \"{resampled_wav}\""
                self.run_command(command_resample, "Resampling WAV", resampled_wav)
                self.update_progress(int(random.randint(14,40)), "Resampled .wav into 48kHz", file)

                command_pcm = f"\"{self.ffmpeg_path}\" -i \"{resampled_wav}\" -f s16le -acodec pcm_s16le -hide_banner -loglevel error \"{raw_file}\""
                self.run_command(command_pcm, "Convert to PCM", raw_file)
                self.update_progress(int(random.randint(41,93)), "PCM Conversion Done", file)

                command_opus = f"\"{self.nxaenc_path}\" -i \"{raw_file}\" -o \"{output_file}\""
                self.run_command(command_opus, "Convert to Opus", output_file)
                self.update_progress(100, f"Conversion Completed.", file)

            self.log("All conversions completed successfully.")
            webbrowser.open(self.output_folder)

        except Exception as e:
            self.log(f"Error during conversion: {e}")
        finally:
            self.cleanup_temp_files()

    def run_command(self, command, step_description, output_file):
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode != 0 or not os.path.exists(output_file):
            self.log(f"Error during {step_description}: {result.stderr}")
            raise Exception(f"{step_description} failed.")

    def cleanup_temp_files(self):
        try:
            if os.path.exists(self.temp_folder):
                shutil.rmtree(self.temp_folder)
        except Exception as e:
            self.log(f"Error deleting temporary folder: {e}")


    def update_progress(self, progress, status, file):
        progress_bar_length = 50  # Length of the progress bar
        progress_blocks = int(progress / 100 * progress_bar_length)
        progress_bar = "[" + "#" * progress_blocks + "." * (progress_bar_length - progress_blocks) + "]"
        
        # Clear the QTextEdit and rewrite the progress line
        self.log_output.append(f"Processing {file} - {status} - {progress_bar} {progress}%")
        QApplication.processEvents()  # Ensure the UI updates immediately


    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_initial_theme(self):
        self.apply_theme()

    def apply_theme(self):
        common_styles = """
            QPushButton {
                font-family: Consolas;
                font-size: 12pt;
                font-weight:  bold;
                padding: 6px;
                border-style: outset;
            }
            QPushButton::hover{
                border-style: inset;
            }
        """

        dark_mode_styles = """
            QMainWindow { background-color: #2b2b2b; color: #ffebcd; }
            QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
            QPushButton { background-color: #4d4d4d; color: #ffebcd; border: 2px solid #ffebcd; }
            QPushButton::hover { background-color: #ffebcd; color: #000000}
            QMessageBox QLabel { color: #ffebcd; }  
            QMessageBox QPushButton { background-color: #4d4d4d; color: #ffebcd; }  
            QMessageBox { background-color: #4d4d4d; } 
        """

        light_mode_styles = """
            QMainWindow { background-color: #f0f0f0; color: #000000; }
            QTextEdit { background-color: #ffffff; color: #000000; }
            QPushButton { background-color: #ffffff; color: #000000; border: 2px solid #cacaca;}
            QPushButton::hover { background-color:  #cacaca; }

            QMessageBox QLabel { color: #000000; }  
            QMessageBox QPushButton { background-color: #ffffff; color: #000000; }  
            QMessageBox { background-color: #ffffff; }  
        """

        # Apply common styles plus mode-specific styles
        if self.dark_mode:
            full_stylesheet = common_styles + dark_mode_styles
        else:
            full_stylesheet = common_styles + light_mode_styles

        # Apply the combined stylesheet
        self.setStyleSheet(full_stylesheet)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ns_OpusConverter()
    window.show()
    sys.exit(app.exec_())
