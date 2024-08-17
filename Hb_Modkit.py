import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, 
    QDesktopWidget, QHBoxLayout, QTextBrowser, QPushButton, QStyle, QMenu
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from scripts import stq_tool, OpusHeaderInjector, AudioCalculator, FolderMaker, HexConverterEncoder, NSOpusConverter, OpusMetadataExtractor

class CustomTitleBar(QWidget):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.title = title
        self.init_ui()

    def init_ui(self):
        self.setAutoFillBackground(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins around the layout

        self.title_label = QLabel(self.title, self)
        self.title_label.setFont(QFont("", 11))  # Increased font size by 1
        self.title_label.setAlignment(Qt.AlignCenter)

        layout.addStretch(1)
        layout.addWidget(self.title_label)
        layout.addStretch(1)

        button_style = """
            QPushButton {
                background-color: #fff;  /* White background */
                color: #000;  /* Black icons */
                border: none;
            }
            QPushButton:hover {
                background-color: #ddd;  /* Slightly darker white on hover */
            }
            QPushButton:pressed {
                background-color: #bbb;  /* Even darker on press */
            }
        """
        for icon_type, method in [
            (QStyle.SP_TitleBarMinButton, self.minimize),
            (QStyle.SP_TitleBarMaxButton, self.maximize_restore),
            (QStyle.SP_TitleBarCloseButton, self.close_window)
        ]:
            button = QPushButton(self)
            button.setFixedSize(30, 30)
            button.setIcon(self.style().standardIcon(icon_type))
            button.setStyleSheet(button_style)
            button.clicked.connect(method)
            layout.addWidget(button, alignment=Qt.AlignTop)

        self.setLayout(layout)

    def minimize(self):
        self.window().showMinimized()

    def maximize_restore(self):
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def close_window(self):
        self.window().close()

class PoppableTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_tab_context_menu)
        self.tab_windows = {}
        self.tab_data_store = {}

    def show_tab_context_menu(self, position):
        index = self.tabBar().tabAt(position)
        tab_name = self.tabText(index)
        if tab_name == "About":
            return  # Skip the About tab

        menu = QMenu()
        menu.addAction("Pop Out Tab", lambda: self.pop_out_tab(index))
        menu.addAction("New Instance", self.create_new_instance)
        menu.exec_(self.mapToGlobal(position))

    def serialize_tab_state(self, widget):
        state = {'title': self.tabText(self.indexOf(widget))}  # Store the tab title
        if hasattr(widget, 'text_edit') and hasattr(widget.text_edit, 'toPlainText'):
            state['text'] = widget.text_edit.toPlainText()
        if hasattr(widget, 'file_list') and hasattr(widget.file_list, 'count'):
            state['files'] = [widget.file_list.item(i).text() for i in range(widget.file_list.count())]
        return state

    def deserialize_tab_state(self, widget, state):
        if 'text' in state and hasattr(widget, 'text_edit') and hasattr(widget.text_edit, 'setPlainText'):
            widget.text_edit.setPlainText(state['text'])
        if 'files' in state and hasattr(widget, 'file_list') and hasattr(widget.file_list, 'addItem'):
            widget.file_list.clear()
            for file in state['files']:
                widget.file_list.addItem(file)
        return state.get('title', "Untitled")  # Return the stored title or default to "Untitled"

    def pop_out_tab(self, index):
        widget = self.widget(index)
        if widget:
            state = self.serialize_tab_state(widget)
            self.removeTab(index)
            self.create_new_window(type(widget)(), state['title'], state)

    def create_new_instance(self):
        current_index = self.currentIndex()
        widget = self.widget(current_index)
        if widget:
            state = self.serialize_tab_state(widget)
            self.create_new_window(type(widget)(), f"{state['title']} - New Instance", state)

    def create_new_window(self, widget, title, state):
        title = self.deserialize_tab_state(widget, state)  # Get the correct title
        new_window = QMainWindow()
        new_window.setWindowTitle(title)
        new_window.setCentralWidget(widget)
        new_window.resize(800, 600)
        new_window.show()
        self.tab_windows[title] = new_window
        self.setup_window_context_menu(new_window, widget, title)

    def remerge_tab(self, widget, title):
        if title in self.tab_windows:
            self.tab_windows.pop(title).close()
            self.addTab(widget, title)
            if title in self.tab_data_store:
                self.deserialize_tab_state(widget, self.tab_data_store.pop(title))

    def setup_window_context_menu(self, window, widget, title):
        window.setContextMenuPolicy(Qt.CustomContextMenu)
        window.customContextMenuRequested.connect(lambda pos: self.show_window_context_menu(window, widget, title, pos))

    def show_window_context_menu(self, window, widget, title, position):
        menu = QMenu(window)
        menu.addAction("New Instance", self.create_new_instance)
        menu.addAction("Re-merge Tab", lambda: self.remerge_tab(widget, title))
        menu.exec_(window.mapToGlobal(position))

class AboutTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        about_text = """
        <h2>About - Handburger Modkit</h2>
        <p>This multi-use tool is developed to help with various modding tasks for Monster Hunter Generations Ultimate.</p>
        <p>Find more about the developer (me!) and support them below.</p>
        <p>Thanks to ffmpeg for the conversion functions, masagrator for the NXAenc variation for MHGU, and the MHGU modding community for their support. </p>
        """
        text_browser = QTextBrowser(self)
        text_browser.setHtml(about_text)
        text_browser.setOpenExternalLinks(True)
        
        font = QFont()
        font.setPointSize(10)
        text_browser.setFont(font)
        
        h2_font = QFont()
        h2_font.setPointSize(14)
        text_browser.setFont(h2_font)
        
        layout.addWidget(text_browser)

        # Adding icons to the About box
        layout.addLayout(self.create_link_layout(self.get_resource_path("github.png"),
                                                "GitHub - RTHKKona", "https://github.com/RTHKKona", 64))
        layout.addLayout(self.create_link_layout(self.get_resource_path("ko-fi.png"),
                                                "Ko-fi - Handburger", "https://ko-fi.com/handburger", 64))

    def get_resource_path(self, filename):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(script_dir, 'assets', filename)
        
        if not os.path.exists(assets_path):
            raise FileNotFoundError(f"Resource not found: {filename} in {assets_path}")
        return assets_path

    def create_icon_label(self, icon_path, size):
        label = QLabel(self)
        label.setPixmap(QPixmap(icon_path).scaled(size, size, Qt.KeepAspectRatio))
        return label

    def create_link_layout(self, icon_path, text, url, icon_size):
        layout = QHBoxLayout()
        layout.addWidget(self.create_icon_label(icon_path, icon_size))

        # Set link color to always be yellow
        link_color = "yellow"

        # Create the QLabel with HTML styling
        link_label = QLabel(f'<a href="{url}" style="color:{link_color};">{text}</a>', self)
        link_label.setOpenExternalLinks(True)
        link_label.setFont(QFont("Arial", 14))

        layout.addWidget(link_label)
        return layout

class HbModkit(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version = "v.0.5.3"
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Handburger Modkit {self.version}")
        self.setGeometry(100, 100, 1600, 900)
        self.setWindowIcon(QIcon(self.get_icon_path("egg.ico")))

        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = PoppableTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        self.setCentralWidget(central_widget)
        self.add_tabs()
        self.apply_dark_mode_theme()

    def add_tabs(self):
        tools = {
            "STQ Editor Tool": stq_tool.STQTool,
            "Opus Header Injector": OpusHeaderInjector.OpusHeaderInjector,
            "Audio Calculator": AudioCalculator.AudioCalculator,
            "FolderMaker": FolderMaker.FolderMaker,
            "Hex Enc/Decoder": HexConverterEncoder.HexConverterEncoder,
            "NSOpus Converter": NSOpusConverter.NSOpusConverter,
            "Opus Metadata Extractor": OpusMetadataExtractor.OpusMetadataExtractor,
            "About": AboutTab
        }
        # Separate the "About" tab and sort the rest alphabetically
        sorted_tools = {k: tools[k] for k in sorted(tools.keys()) if k != "About"}

        # Insert the "About" tab at the beginning
        sorted_tools = {"About": tools["About"], **sorted_tools}

        # Add the tabs in the correct order
        for name, tool in sorted_tools.items():
            try:
                self.tab_widget.addTab(tool(), name)
            except Exception as e:
                print(f"Error adding tab '{name}': {e}")

    def apply_dark_mode_theme(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; color: #ffebcd; }
            QTabWidget::pane { border: 1px solid #444; }
            QWidget { background-color: #3c3c3c; color: #ffffff; }
            QTabBar::tab { background: #4d4d4d; color: #ffffff; padding: 10px; }
            QTabBar::tab:selected { background: #555; }
        """)

    def get_icon_path(self, icon_name):
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
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

        splash_label = QLabel(self)
        pixmap = QPixmap(self.get_splash_image_path()).scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        splash_label.setPixmap(pixmap)
        splash_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(splash_label)

        self.show_splash_screen()
        self.center_on_screen()

    def get_splash_image_path(self):
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
        splash_image_path = os.path.join(assets_dir, "funnycharacta.png")
        if not os.path.exists(splash_image_path):
            raise FileNotFoundError(f"Splash image not found at {splash_image_path}")
        return splash_image_path

    def center_on_screen(self):
        screen = QDesktopWidget().screenGeometry()
        window_size = self.geometry()
        self.move((screen.width() - window_size.width()) // 2, (screen.height() - window_size.height()) // 2)

    def show_splash_screen(self):
        QTimer.singleShot(3000, self.close)
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()

    event_loop = QEventLoop()
    QTimer.singleShot(3000, event_loop.quit)
    event_loop.exec_()

    main_window = HbModkit()
    main_window.show()

    sys.exit(app.exec_())
