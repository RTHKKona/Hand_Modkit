# Audio Calculator module
# Version management
VERSION = "1.0.5"

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox,
    QPushButton, QWidget, QRadioButton, QFrame, QTextEdit, QAction, QMenuBar
)
from PyQt5.QtGui import QFont
from decimal import Decimal, getcontext, InvalidOperation, DivisionImpossible

## Set precision for accurate calculations
getcontext().prec = 20
SAMPLE_RATE = Decimal('48000')

class AudioCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  ## Start in dark mode
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        self.setWindowTitle("Audio Calculator")
        self.setGeometry(100, 100, 1600, 800)

        ## Main layout
        central_widget = QWidget(self)
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(self.create_left_column())
        main_layout.addWidget(self.create_center_column())
        main_layout.addWidget(self.create_right_column())
        self.setCentralWidget(central_widget)

        ## Menu bar
        menubar = self.menuBar()
        help_menu = menubar.addMenu("Help")
        help_action = QAction("About", self)
        help_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(help_action)

        self.update_font_size()
        
        self.calculate_button.setEnabled(False)
        self.calculate_button.setStyleSheet("""
        QPushButton:disabled {
            color: #090500;             
            border: 1px solid #c0c0c0; 
        }
    """)
        self.audio_input.textChanged.connect(self.check_input)
        
    def check_input(self):
        ## Enable the calculate button if there's text in the input box, otherwise disable it
        input_text = self.audio_input.toPlainText().strip()
        if input_text:
            self.calculate_button.setEnabled(True)
        else:
            self.calculate_button.setEnabled(False)

    def create_left_column(self):
        ## Left column for input
        left_frame = QFrame(self)
        left_layout = QVBoxLayout(left_frame)
        self.input_label = QLabel("Audio Samples/Duration Input", self)
        self.audio_input = QTextEdit(self)
        self.audio_input.setPlaceholderText("Enter value (e.g., 03:09.9 for duration) or (e.g., 1337420 for samples).")
        left_layout.addWidget(self.input_label)
        left_layout.addWidget(self.audio_input)
        return left_frame

    def create_center_column(self):
        ## Center column with settings and buttons
        center_frame = QFrame(self)
        center_layout = QVBoxLayout(center_frame)
        self.settings_label = QLabel(f"Audio Calculator v{VERSION}\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nConversion Settings", self)
        self.mode_samples_to_duration = QRadioButton("Samples to Duration", self)
        self.mode_duration_to_samples = QRadioButton("Duration to Samples", self)
        self.mode_samples_to_duration.setChecked(True)

        ## Buttons
        self.calculate_button = QPushButton("Calculate", self)
        self.calculate_button.clicked.connect(self.calculate)
        clear_button = QPushButton("Clear", self)
        clear_button.clicked.connect(self.clear_inputs)
        toggle_theme_button = QPushButton("Toggle Theme", self)
        toggle_theme_button.clicked.connect(self.toggle_theme)

        ## Add to layout
        for widget in [self.settings_label, self.mode_samples_to_duration, self.mode_duration_to_samples, self.calculate_button, clear_button, toggle_theme_button]:
            center_layout.addWidget(widget)

        return center_frame

    def create_right_column(self):
        ## Right column for result display
        right_frame = QFrame(self)
        right_layout = QVBoxLayout(right_frame)
        self.result_label = QLabel("Converted Result", self)
        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(True)
        right_layout.addWidget(self.result_label)
        right_layout.addWidget(self.result_output)
        return right_frame

    def show_about_dialog(self):
        ## About dialog
        about_text = f"Audio Calculator\nVersion {VERSION}\n\nCalculates various properties of audio files."
        QMessageBox.about(self, "About", about_text)

    def calculate(self):
        ## Perform the calculation
        input_text = self.audio_input.toPlainText().strip()
        
        try:
            if self.mode_samples_to_duration.isChecked():
                samples = Decimal(input_text)

                ## Validate the input range (for practical purposes in audio calculation)
                if samples <= 0 or samples > Decimal('1e15'):  # Arbitrary large number to limit input size
                    raise ValueError("Sample count is too large or invalid!")

                minutes, seconds = divmod(samples / SAMPLE_RATE, 60)
                result = f"Duration: {int(minutes):02}:{seconds:06.3f}"
            else:
                total_seconds = self.parse_time_to_seconds(input_text)
                result = f"Samples: {total_seconds * SAMPLE_RATE}"
            
            self.result_output.setText(result)
        except (InvalidOperation, ValueError, DivisionImpossible) as e:
            self.result_output.setText("Invalid input! Please enter a valid or reasonable value.")
            print(f"Error: {e}")


    def parse_time_to_seconds(self, time_str):
        ## Parse time from MM:SS or seconds format
        try:
            time_parts = time_str.split(':')
            if len(time_parts) == 2:
                minutes, seconds = map(Decimal, time_parts)
                return minutes * 60 + seconds
            return Decimal(time_str)
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Error parsing time input: {e}")

    def clear_inputs(self):
        ## Clear input and output fields
        self.audio_input.clear()
        self.result_output.clear()

    def update_font_size(self):
        ## Update font size for all widgets
        font = QFont("Consolas", 11)
        widgets = [self.input_label, self.audio_input, self.settings_label, self.mode_samples_to_duration, self.mode_duration_to_samples, self.result_label, self.result_output]
        for widget in widgets:
            widget.setFont(font)

    def toggle_theme(self):
        ## Toggle between dark and light theme
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        ## Apply the theme based on current mode
        common_styles = """
            QPushButton { font-family: Consolas; font-size: 12pt; font-weight: bold; padding: 6px; margin: 5px; border-style: outset; min-width: 120px;}
            QPushButton::hover, QPushButton::pressed {border-style: inset;}
        """
        dark_mode_styles = """
            QMainWindow { background-color: #272727; color: #ffebcd; }
            QTextEdit { background-color: #404040; color: #ffebcd; border: 2px solid #ffebcd; }
            QLabel, QRadioButton { color: #ffebcd; font-weight:  bold; font-family: Consolas;}
            QPushButton { background-color: #1e1e1e; color: #ffebcd; border:  2px solid #ffebcd; }
            QPushButton::hover, QPushButton::pressed {background-color: #ffebcd; color: #000000;}
        """
        light_mode_styles = """
            QMainWindow { background-color: white; color: black; }
            QTextEdit { background-color: #f0f0f0; color: black; border: 2px solid black; }
            QLabel, QRadioButton { color: black; font-weight: bold; font-family: Consolas; }
            QPushButton { background-color: #f0f0f0; color: black; border:  2px solid #cacaca; }
            QPushButton::hover, QPushButton::pressed { background-color: #cacaca; color: #000000; }

        """
        self.setStyleSheet(common_styles + (dark_mode_styles if self.dark_mode else light_mode_styles))


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        calculator = AudioCalculator()
        calculator.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
