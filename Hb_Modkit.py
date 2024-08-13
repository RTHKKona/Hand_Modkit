import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtGui import QIcon
from scripts import stq_tool, OpusHeaderInjector, AudioCalculator, FolderMaker

class MHGU_Mod_Platform(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Handburger's MHGU Mod Platform Alpha v0.0.2")
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("QMainWindow { background-color: #f0f0f0; }")
        self.setWindowIcon(QIcon(self.get_resource_path("egg.ico")))

        self.tab_widget = QTabWidget(movable=True, styleSheet="QTabBar::tab { min-width: 150px; font-size: 12px; }")
        self.setCentralWidget(self.tab_widget)

        self.add_tabs()

    def add_tabs(self):
        tabs = [
            (stq_tool.STQTool(), "STQ Editor Tool"),
            (OpusHeaderInjector.OpusHeaderInjector(), "Opus Header Injector"),
            (AudioCalculator.AudioCalculator(), "Audio Calculator"),
            (FolderMaker.FolderMaker(), "FolderMaker")
        ]
        for tab, name in tabs:
            self.tab_widget.addTab(tab, name)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.ZoomIn):
            self.findChild(AudioCalculator.AudioCalculator).change_font_size(1)
        elif event.matches(QKeySequence.ZoomOut):
            self.findChild(AudioCalculator.AudioCalculator).change_font_size(-1)
        else:
            super().keyPressEvent(event)

    def get_resource_path(self, filename):
        return os.path.join(os.path.dirname(__file__), 'assets', filename)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MHGU_Mod_Platform()
    main_window.show()
    sys.exit(app.exec_())
