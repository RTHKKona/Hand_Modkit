import sys
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QRadioButton, QPushButton, QApplication
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from decimal import Decimal, getcontext, InvalidOperation

# Set precision high enough to handle all operations accurately
getcontext().prec = 20
SAMPLE_RATE = Decimal('48000')

class AudioCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.font_size = 12  # Default font size
        self.dark_mode = True  # Start in dark mode by default
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout(self)
        self.display = QLineEdit(self, placeholderText="Enter value (e.g., 03:09.9 for duration)")
        layout.addWidget(self.display, 0, 0, 1, 4)

        self.mode_samples_to_duration = QRadioButton("Samples to Duration", self)
        self.mode_duration_to_samples = QRadioButton("Duration to Samples", self)
        self.mode_samples_to_duration.setChecked(True)
        layout.addWidget(self.mode_samples_to_duration, 1, 0, 1, 2)
        layout.addWidget(self.mode_duration_to_samples, 1, 2, 1, 2)

        self.calculate_btn = QPushButton("Calculate", self, clicked=self.calculate)
        layout.addWidget(self.calculate_btn, 2, 0, 1, 4)

        self.result_label = QLabel("Result will be shown here", self)
        layout.addWidget(self.result_label, 3, 0, 1, 4)

        self.toggle_theme_btn = QPushButton("Toggle Theme", self)
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.toggle_theme_btn, 4, 0, 1, 4)

        self.setLayout(layout)
        self.update_font_size()

    def calculate(self):
        input_text = self.display.text().strip()
        try:
            if self.mode_samples_to_duration.isChecked():
                samples = Decimal(input_text)
                minutes, seconds = divmod(samples / SAMPLE_RATE, 60)
                self.result_label.setText(f"Duration: {int(minutes):02}:{seconds:06.3f}")
            else:
                if ':' in input_text:
                    minutes, seconds = map(Decimal, input_text.split(':'))
                    total_seconds = minutes * 60 + seconds
                else:
                    total_seconds = Decimal(input_text)
                samples = total_seconds * SAMPLE_RATE
                self.result_label.setText(f"Samples: {samples}")
        except InvalidOperation:
            self.result_label.setText("Invalid input! Please enter a valid value.")

    def update_font_size(self):
        font = QFont()
        font.setPointSize(self.font_size)
        for widget in [self.display, self.mode_samples_to_duration, self.mode_duration_to_samples, self.calculate_btn, self.result_label, self.toggle_theme_btn]:
            widget.setFont(font)

    def change_font_size(self, increment):
        self.font_size = max(1, self.font_size + increment)
        self.update_font_size()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget { background-color: #2b2b2b; color: #ffebcd; }
                QLineEdit { background-color: #4d4d4d; color: #ffebcd; }
                QLabel { color: #ffebcd; }
                QRadioButton { color: #ffebcd; }
                QPushButton { background-color: #4d4d4d; color: #ffebcd; }
            """)
        else:
            self.setStyleSheet("")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    calculator = AudioCalculator()
    calculator.show()
    sys.exit(app.exec_())
