import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QSplashScreen
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtCore import Qt, QTimer
from scripts import stq_tool, OpusHeaderInjector, AudioCalculator, FolderMaker, HexConverterEncoder  # Ensure this line is included

class MHGU_Mod_Platform(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        try:
            self.setWindowTitle("Handburger's MHGU Mod Platform Alpha v0.0.3")
            self.setGeometry(100, 100, 1400, 800)
            self.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")
            self.setWindowIcon(QIcon(self.get_resource_path("egg.ico")))

            self.tab_widget = QTabWidget(movable=True)
            self.tab_widget.setStyleSheet("QTabBar::tab { min-width: 150px; font-size: 12px; }")
            self.setCentralWidget(self.tab_widget)

            self.add_tabs()
        except Exception as e:
            print(f"Error initializing UI: {e}")
            sys.exit(1)

    def add_tabs(self):
        tools = {
            "STQ Editor Tool": stq_tool.STQTool,
            "Opus Header Injector": OpusHeaderInjector.OpusHeaderInjector,
            "Audio Calculator": AudioCalculator.AudioCalculator,
            "FolderMaker": FolderMaker.FolderMaker,
            "Hex Enc/Decoder": HexConverterEncoder.HexConverterEncoder
        }

        for name, tool in tools.items():
            try:
                tab_instance = tool()
                self.tab_widget.addTab(tab_instance, name)
            except Exception as e:
                print(f"Error adding tab '{name}': {e}")

    def keyPressEvent(self, event):
        try:
            if event.matches(QKeySequence.ZoomIn):
                self.findChild(AudioCalculator.AudioCalculator).change_font_size(1)
            elif event.matches(QKeySequence.ZoomOut):
                self.findChild(AudioCalculator.AudioCalculator).change_font_size(-1)
            else:
                super().keyPressEvent(event)
        except Exception as e:
            print(f"Error processing key event: {e}")

    def get_resource_path(self, filename):
        path = os.path.join(os.path.dirname(__file__), 'assets', filename)
        if not os.path.exists(path):
            print(f"Resource '{filename}' not found at {path}")
        return path

def show_splash_screen(app):
    splash_image_path = os.path.join(os.path.dirname(__file__), 'assets', 'funnycharacta.png')
    if not os.path.exists(splash_image_path):
        print(f"Error: Splash image '{splash_image_path}' not found.")
        return None

    pixmap = QPixmap(splash_image_path).scaled(550, 550, Qt.KeepAspectRatio)  # Splash Scale
    splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
    splash.setMask(pixmap.mask())

    splash.show()

    # Splash screen timer
    QTimer.singleShot(3400, splash.close)

    return splash

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        
        splash = show_splash_screen(app)
        
        main_window = MHGU_Mod_Platform()
        main_window.show()

        if splash:
            splash.finish(main_window)

        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)
