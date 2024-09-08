# MCA Converter
# Version management
VERSION = "1.0.7"

import os, sys,subprocess
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QTextEdit, 
    QLabel, QMessageBox, QAction, QMenuBar, QApplication
)
from PyQt5.QtGui import QFont

class WavToMcaConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Start in dark mode by default
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.wav_files = []  # List of WAV files for batch conversion
        self.converted_mca_files = []  # Store converted MCA files for opening file explorer later
        self.first_launch = True
        self.license_file = os.path.join(self.base_dir, "dasdep", "LICENSE", "wav2dsp.LICENSE.txt")
        self.setup_ui()
        self.apply_initial_theme()
        self.check_dependencies()

    def setup_ui(self):
        ### UI Setup with Layout and Buttons
        self.setWindowTitle('Audio to MCA Converter')
        self.setGeometry(100, 100, 1600, 800)

        main_layout = QVBoxLayout()
        self.log_output = QTextEdit(self, readOnly=True)
        self.log_output.setFont(QFont("Consolas", 11))
        main_layout.addWidget(self.log_output)

        button_font = QFont()
        button_font.setPointSize(11)
        
        bottom_layout = QHBoxLayout()
        buttons = [
            ("Import Audio", self.open_files),
            ("Convert", self.convert_to_mca),
            ("Help", self.show_help),
            ("Change Theme", self.toggle_theme)
        ]
        for text, func in buttons:
            btn = QPushButton(text, self, font=button_font, clicked=func)
            btn.setStyleSheet("QPushButton { padding: 10px; }")
            bottom_layout.addWidget(btn)

        main_layout.addLayout(bottom_layout)
        self.setup_menu()

        central_widget = QLabel(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def setup_menu(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        help_menu = menubar.addMenu("Help")
        help_action = QAction("About", self)
        help_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(help_action)

    def check_dependencies(self):
        self.log("[INFO] Checking dependencies...\n")
        dependencies = {
            "wav2dsp.exe": os.path.join(self.base_dir, "dasdep", "wav2dsp.exe"),
            "python27/python.exe": os.path.join(self.base_dir, "dasdep", "python27", "python.exe"),
            "mcatool.py": os.path.join(self.base_dir, "dasdep", "mcatool.py"),
        }
        missing = []
        for dep_name, dep_path in dependencies.items():
            if os.path.exists(dep_path):
                self.log(f"[✔] {dep_name} found at '{dep_path}'")
            else:
                self.log(f"[✘] {dep_name} is missing.")
                missing.append(dep_name)
        if missing:
            self.show_dependency_error(missing)
        else:
            self.log("[INFO] All dependencies are satisfied.")

        if self.first_launch:
            self.show_license()
            self.first_launch = False

    def show_license(self):
        ### Show LICENSE.txt on first launch
        if os.path.exists(self.license_file):
            with open(self.license_file, 'r') as file:
                license_text = file.read()
            self.log(f"[INFO] Displaying License:\n{license_text}")
        else:
            self.log("[ERROR] License file not found.")

    def open_files(self):
        ### Open file dialog for selecting multiple audio files
        files, _ = QFileDialog.getOpenFileNames(self, "Open Audio Files", "", 
            "Audio Files (*.wav *.ogg *.flac *.mp3 *.mp4);;All Files (*)")
        if files:
            self.wav_files = files
            self.log(f"[INFO] Selected Files: {', '.join(self.wav_files)}")
            for file in self.wav_files:
                self.convert_to_wav(file)

    def convert_to_wav(self, audio_file):
        ### Convert any supported audio file to a 1-channel WAV file
        file_ext = os.path.splitext(audio_file)[1].lower()
        if file_ext in ['.ogg', '.flac', '.mp3', '.mp4', '.wav']:
            wav_file = os.path.splitext(audio_file)[0] + "_temp.wav"
            command = f'ffmpeg -i "{audio_file}" -ac 1 "{wav_file}"'
            result = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            if result.returncode != 0:
                self.log(f"[ERROR] Failed to convert {audio_file} to WAV.")
            else:
                self.log(f"[INFO] Converted {audio_file} to {wav_file}.")
        else:
            self.log(f"[ERROR] Unsupported file type: {audio_file}")

    def convert_to_mca(self):
        if not self.wav_files:
            self.show_error("No Files", "Please select audio files before converting.")
            return

        self.converted_mca_files = []  # Reset converted MCA files
        self.log("[INFO] Starting batch conversion...")

        with ThreadPoolExecutor() as executor:
            executor.map(self.process_conversion, self.wav_files)

        if self.converted_mca_files:
            self.open_file_explorer(self.converted_mca_files[0])
        self.log("[INFO] Batch conversion complete!")

    def process_conversion(self, audio_file):
        temp_wav = os.path.splitext(audio_file)[0] + "_temp.wav"
        converted_mca = WavToMcaFunctionality(temp_wav, audio_file).run()
        if converted_mca:
            self.converted_mca_files.append(converted_mca)

    def open_file_explorer(self, file_path):
        directory = os.path.dirname(file_path)
        subprocess.Popen(f'explorer /select,"{os.path.abspath(file_path)}"')
        self.log(f"[INFO] Opened file explorer for: {directory}")

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
                padding: 6px;
            }
            QMessageBox QLabel{
                font-weight: bold;
                font-size: 12pt;
                font-family: Consolas;
                padding: 10px;
            }
        """

        dark_mode_styles = """
            QMainWindow { background-color: #2b2b2b; color: #ffebcd; }
            QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
            QPushButton { background-color: #4d4d4d; color: #ffebcd; }
            QMessageBox QLabel { color: #ffebcd; }  /* Ensure QLabel inside QMessageBox is styled */
            QMessageBox QPushButton { background-color: #4d4d4d; color: #ffebcd; }  /* Button styling inside QMessageBox */
            QMessageBox { background-color: #4d4d4d; }  /* Background styling for QMessageBox */
        """

        light_mode_styles = """
            QMainWindow { background-color: #f0f0f0; color: #000000; }
            QTextEdit { background-color: #ffffff; color: #000000; }
            QPushButton { background-color: #ffffff; color: #000000; }
            QMessageBox QLabel { color: #000000; }  /* Ensure QLabel inside QMessageBox is styled */
            QMessageBox QPushButton { background-color: #ffffff; color: #000000; }  /* Button styling inside QMessageBox */
            QMessageBox { background-color: #ffffff; }  /* Background styling for QMessageBox */
        """

        # Apply common styles plus mode-specific styles
        if self.dark_mode:
            full_stylesheet = common_styles + dark_mode_styles
        else:
            full_stylesheet = common_styles + light_mode_styles

        # Apply the combined stylesheet
        self.setStyleSheet(full_stylesheet)


    def show_about_dialog(self):
        about_text = f"Audio to MCA Converter Version {VERSION}\nConverts supported audio files to MCA format."
        QMessageBox.about(self, "About", about_text)

    def show_help(self):
        help_text = "Instructions on how to use the Audio to MCA Converter."
        self.log("[INFO] Showing help dialog.")
        QMessageBox.information(self, "Help", help_text)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def show_dependency_error(self, missing_deps):
        message = f"Missing dependencies:\n{', '.join(missing_deps)}"
        self.show_error("Missing Dependencies", message)

    def log(self, message):
        self.log_output.append(message)
        self.log_output.ensureCursorVisible()


class WavToMcaFunctionality:
    def __init__(self, temp_wav_file, original_audio_file):
        self.temp_wav_file = temp_wav_file
        self.original_audio_file = original_audio_file
        self.dsp_file = os.path.splitext(temp_wav_file)[0] + ".dsp"
        self.mca_file = os.path.splitext(temp_wav_file)[0] + ".mca"
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.python27_path = os.path.join(self.base_dir, "dasdep", "python27", "python.exe")
        self.wav2dsp_exe = os.path.join(self.base_dir, "dasdep", "wav2dsp.exe")
        self.mcatool_py = os.path.join(self.base_dir, "dasdep", "mcatool.py")

    def run(self):
        if not os.path.exists(self.temp_wav_file):
            return

        if self.run_wav2dsp() and self.run_mcatool():
            self.cleanup()
            return self.rename_mca_file()

    def run_wav2dsp(self):
        command = f'"{self.wav2dsp_exe}" "{self.temp_wav_file}"'
        return self.run_command(command, "WAV to DSP conversion failed")

    def run_mcatool(self):
        command = f'"{self.python27_path}" "{self.mcatool_py}" --mhx "{self.temp_wav_file}"'
        return self.run_command(command, "DSP to MCA conversion failed")

    def run_command(self, command, error_message):
        result = subprocess.run(command, shell=True)
        if result.returncode != 0:
            return False
        return True

    def cleanup(self):
        os.remove(self.temp_wav_file)
        os.remove(self.dsp_file)

    def rename_mca_file(self):
        new_mca_name = os.path.splitext(self.original_audio_file)[0] + ".mca"
        os.rename(self.mca_file, new_mca_name)
        return new_mca_name


if __name__ == "__main__":
    app = QApplication([])
    window = WavToMcaConverter()
    window.show()
    sys.exit(app.exec_())
