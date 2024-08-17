import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QWidget, QRadioButton, QFrame, QTextEdit, QAction, QMenuBar
)
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import Qt

from decimal import Decimal, getcontext, InvalidOperation

# Set precision high enough to handle all operations accurately
getcontext().prec = 20
SAMPLE_RATE = Decimal('48000')

class AudioCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Start in dark mode by default
        self.init_ui()
        self.apply_initial_theme()

    def init_ui(self):
        self.setWindowTitle("Audio Calculator")
        self.setGeometry(100, 100, 1600, 800)

        # Main widget and layout
        central_widget = QWidget(self)
        main_layout = QHBoxLayout(central_widget)

        # Create and add columns to the main layout
        main_layout.addWidget(self.create_left_column())
        main_layout.addWidget(self.create_center_column())
        main_layout.addWidget(self.create_right_column())

        self.setCentralWidget(central_widget)

        # Increase the font size
        self.update_font_size()
        
        # Create a menu bar
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        help_menu = menubar.addMenu("Help")
        help_action = QAction("About", self)
        help_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(help_action)

    def create_left_column(self):
        left_frame = QFrame(self)
        left_frame.setFrameShape(QFrame.Box)
        left_layout = QVBoxLayout(left_frame)

        self.input_label = QLabel("Audio Input", self)
        self.audio_input = QTextEdit(self)
        self.audio_input.setPlaceholderText("Enter value (e.g., 03:09.9 for duration)")
        
        left_layout.addWidget(self.input_label)
        left_layout.addWidget(self.audio_input)
        
        return left_frame

    def create_center_column(self):
        center_frame = QFrame(self)
        center_frame.setFrameShape(QFrame.Box)
        center_layout = QVBoxLayout(center_frame)

        self.settings_label = QLabel("Conversion Settings", self)
        self.mode_samples_to_duration = QRadioButton("Samples to Duration", self)
        self.mode_duration_to_samples = QRadioButton("Duration to Samples", self)
        self.mode_samples_to_duration.setChecked(True)
        
        calculate_button = QPushButton("Calculate", self)
        calculate_button.clicked.connect(self.calculate)

        clear_button = QPushButton("Clear", self)
        clear_button.clicked.connect(self.clear_inputs)

        toggle_theme_button = QPushButton("Toggle Theme", self)
        toggle_theme_button.clicked.connect(self.toggle_theme)

        for widget in [self.settings_label, self.mode_samples_to_duration, self.mode_duration_to_samples, calculate_button, clear_button, toggle_theme_button]:
            center_layout.addWidget(widget)
        
        return center_frame

    def create_right_column(self):
        right_frame = QFrame(self)
        right_frame.setFrameShape(QFrame.Box)
        right_layout = QVBoxLayout(right_frame)

        self.result_label = QLabel("Converted Result", self)
        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(True)
        
        right_layout.addWidget(self.result_label)
        right_layout.addWidget(self.result_output)
        
        return right_frame
    
    def show_about_dialog(self):
        about_text = (
            "Audio Calculator\n"
            "Version 1.0\n\n"
            "Calculates various properties of audio files."
        )
        QMessageBox.about(self, "About", about_text)
        
    def calculate(self):
        input_text = self.audio_input.toPlainText().strip()
        try:
            if self.mode_samples_to_duration.isChecked():
                samples = Decimal(input_text)
                minutes, seconds = divmod(samples / SAMPLE_RATE, 60)
                result = f"Duration: {int(minutes):02}:{seconds:06.3f}"
            else:
                time_parts = input_text.split(':')
                if len(time_parts) == 2:
                    minutes, seconds = map(Decimal, time_parts)
                    total_seconds = minutes * 60 + seconds
                else:
                    total_seconds = Decimal(input_text)
                result = f"Samples: {total_seconds * SAMPLE_RATE}"
            self.result_output.setText(result)
        except (InvalidOperation, ValueError) as e:
            self.result_output.setText("Invalid input! Please enter a valid value.")
            print(f"Error: {e}")

    def clear_inputs(self):
        """Clears the input and output fields."""
        self.audio_input.clear()
        self.result_output.clear()

    def update_font_size(self):
        font = QFont()
        font.setPointSize(11)  # Increased font size by 1 point
        widgets = [
            self.input_label, self.audio_input, self.settings_label,
            self.mode_samples_to_duration, self.mode_duration_to_samples,
            self.result_label, self.result_output
        ]
        for widget in widgets:
            widget.setFont(font)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_initial_theme(self):
        """Apply the theme once during initialization."""
        self.apply_theme()

    def apply_theme(self):
        """Apply the appropriate stylesheet based on the current theme."""
        stylesheet = """
            QMainWindow { background-color: #2b2b2b; color: #ffebcd; }
            QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
            QLabel { color: #ffebcd; }
            QRadioButton { color: #ffebcd; }
            QPushButton { background-color: #4d4d4d; color: #ffebcd; }
            QFrame { background-color: #2b2b2b; color: #ffebcd; }
        """ if self.dark_mode else ""
        self.setStyleSheet(stylesheet)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calculator = AudioCalculator()
    calculator.show()
    sys.exit(app.exec_())
