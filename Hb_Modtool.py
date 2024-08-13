import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QLineEdit, QRadioButton, QPushButton, QGridLayout
from PyQt5.QtGui import QFont, QKeySequence
from PyQt5.QtCore import Qt
from decimal import Decimal, getcontext, InvalidOperation

import stq_tool
import OpusHeaderInjector

# Set precision high enough to handle all operations accurately
getcontext().prec = 20
SAMPLE_RATE = Decimal('48000')

class AudioCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.font_size = 12  # Default font size
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout(self)

        # Display Entry
        self.display = QLineEdit(self)
        self.display.setPlaceholderText("Enter value (e.g., 03:09.9 for duration)")
        layout.addWidget(self.display, 0, 0, 1, 4)

        # Mode Selection
        self.mode_samples_to_duration = QRadioButton("Samples to Duration", self)
        self.mode_duration_to_samples = QRadioButton("Duration to Samples", self)
        self.mode_samples_to_duration.setChecked(True)
        layout.addWidget(self.mode_samples_to_duration, 1, 0, 1, 2)
        layout.addWidget(self.mode_duration_to_samples, 1, 2, 1, 2)

        # Calculate Button
        self.calculate_btn = QPushButton("Calculate", self)
        self.calculate_btn.clicked.connect(self.calculate)
        layout.addWidget(self.calculate_btn, 2, 0, 1, 4)

        # Result Display
        self.result_label = QLabel("Result will be shown here", self)
        layout.addWidget(self.result_label, 3, 0, 1, 4)

        self.setLayout(layout)
        self.update_font_size()

    def calculate(self):
        input_text = self.display.text().strip()

        if self.mode_samples_to_duration.isChecked():
            try:
                samples = Decimal(input_text)
                result = samples / SAMPLE_RATE
                minutes = int(result // 60)
                seconds = result % 60
                self.result_label.setText(f"Duration: {minutes:02}:{seconds:06.3f}")
            except InvalidOperation:
                self.result_label.setText("Invalid input! Please enter a valid number of samples.")
        else:
            try:
                # Parse input as MM:SS.s format
                if ':' in input_text:
                    minutes, seconds = input_text.split(':')
                    total_seconds = Decimal(minutes) * 60 + Decimal(seconds)
                else:
                    total_seconds = Decimal(input_text)

                samples = total_seconds * SAMPLE_RATE
                self.result_label.setText(f"Samples: {samples}")
            except InvalidOperation:
                self.result_label.setText("Invalid input! Please enter a valid duration (MM:SS.s).")

    def update_font_size(self):
        font = QFont()
        font.setPointSize(self.font_size)

        self.display.setFont(font)
        self.mode_samples_to_duration.setFont(font)
        self.mode_duration_to_samples.setFont(font)
        self.calculate_btn.setFont(font)
        self.result_label.setFont(font)

    def increase_font_size(self):
        self.font_size += 1
        self.update_font_size()

    def decrease_font_size(self):
        if self.font_size > 1:
            self.font_size -= 1
            self.update_font_size()

class MHGU_Mod_Platform(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Update version and description
        self.version = "1.4"
        self.description = "v0.01 Handburger's MHGU Mod Platform"

        # Create the tab widget
        self.tab_widget = QTabWidget()

        # Initialize and add the STQ Tool tab
        self.stq_tool = stq_tool.STQTool()
        self.tab_widget.addTab(self.stq_tool, "STQ Tool")

        # Initialize and add the Opus Header Injector tab
        self.opus_injector = OpusHeaderInjector.OpusHeaderInjector()
        self.tab_widget.addTab(self.opus_injector, "Opus Header Injector")

        # Initialize and add the Audio Calculator tab
        self.audio_calculator = AudioCalculator()
        self.tab_widget.addTab(self.audio_calculator, "Audio Calculator")

        # Set the central widget as the tab widget
        self.setCentralWidget(self.tab_widget)
        self.setWindowTitle(self.description)

        # Set stylesheet for title bar and window
        self.setStyleSheet("QMainWindow { background-color: #f0f0f0; } QTabBar::tab { font-size: 12px; }")

    def keyPressEvent(self, event):
        # Ctrl + = to increase font size
        if event.matches(QKeySequence.ZoomIn):
            self.audio_calculator.increase_font_size()

        # Ctrl + - to decrease font size
        elif event.matches(QKeySequence.ZoomOut):
            self.audio_calculator.decrease_font_size()

        # Allow normal behavior for other key presses
        else:
            super().keyPressEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MHGU_Mod_Platform()
    main_window.show()
    sys.exit(app.exec_())
