import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QDesktopWidget
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtCore import Qt, QTimer
from scripts import stq_tool, OpusHeaderInjector, AudioCalculator, FolderMaker, HexConverterEncoder, NSOpusConverter

class HbModkit(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Handburger Modkit v.0.5")
        self.setGeometry(100, 100, 1600, 900)
        self.setWindowIcon(QIcon(self.get_icon_path("egg.ico")))

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        self.tab_widget = QTabWidget(self)
        layout.addWidget(self.tab_widget)

        self.add_tabs()

    def add_tabs(self):
        tools = {
            "STQ Editor Tool": stq_tool.STQTool,
            "Opus Header Injector": OpusHeaderInjector.OpusHeaderInjector,
            "Audio Calculator": AudioCalculator.AudioCalculator,
            "FolderMaker": FolderMaker.FolderMaker,
            "Hex Enc/Decoder": HexConverterEncoder.HexConverterEncoder,
            "NSOpus Converter": NSOpusConverter.NSOpusConverter,  # Updated the name
        }

        for name, tool in tools.items():
            try:
                tab_instance = tool()
                self.tab_widget.addTab(tab_instance, name)
            except Exception as e:
                print(f"Error adding tab '{name}': {e}")

    def get_icon_path(self, icon_name):
        """
        Searches for the icon in the /assets/ directory located
        in the same directory as Hb_Modkit.py.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(script_dir, 'assets')
        icon_path = os.path.join(assets_dir, icon_name)

        if not os.path.exists(icon_path):
            raise FileNotFoundError(f"Icon not found at {icon_path}")
        
        return icon_path


class SplashScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Load and display the splash image from the assets directory
        splash_label = QLabel(self)
        splash_image_path = self.get_splash_image_path()
        pixmap = QPixmap(splash_image_path)

        # Scale the image to the desired size
        scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Adjust the size as needed
        splash_label.setPixmap(scaled_pixmap)
        splash_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(splash_label)

        # Center the splash screen on the client's window
        self.center_on_screen()

        # Display the splash screen for 3 seconds
        self.show_splash_screen()

    def get_splash_image_path(self):
        """
        Searches for the splash image in the /assets/ directory located
        in the same directory as Hb_Modkit.py.
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(script_dir, 'assets')
        splash_image_filename = "funnycharacta.png"  # Updated with the correct image name
        splash_image_path = os.path.join(assets_dir, splash_image_filename)

        if not os.path.exists(splash_image_path):
            raise FileNotFoundError(f"Splash image not found at {splash_image_path}")
        
        return splash_image_path

    def center_on_screen(self):
        """
        Centers the splash screen on the client's window.
        """
        screen = QDesktopWidget().screenGeometry()
        window_size = self.geometry()
        x = (screen.width() - window_size.width()) // 2
        y = (screen.height() - window_size.height()) // 2
        self.move(x, y)

    def show_splash_screen(self):
        # Using QTimer to properly close the splash screen after 3 seconds
        QTimer.singleShot(3000, self.close)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Show the splash screen
    splash = SplashScreen()
    splash.show()

    # Start the main application
    main_window = HbModkit()
    main_window.show()

    sys.exit(app.exec_())
