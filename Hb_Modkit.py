# Handburger's Hb_Modkit alpha release 
# Version management
VERSION = "0.6.2b"

import sys
import os
import json
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, 
    QDesktopWidget, QHBoxLayout, QTextBrowser, QPushButton, QMenu,
    QProgressBar, QSpacerItem, QSizePolicy, QMessageBox, QStyle
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
from scripts import (
    OpusConverter, stq_tool, OpusHeaderInjector, AudioCalculator, FolderMaker, HexConverterEncoder, 
    OpusMetadataExtractor, STQ_Merge, MCAConverter, MCA_Forge
)

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Global exception handler
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Allow KeyboardInterrupt to close the application gracefully
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    # Log the error
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    # Show a user-friendly error message
    QMessageBox.critical(None, "Application Error", "An unexpected error occurred. Please check the logs.", QMessageBox.Ok)

# Set the global exception handler
sys.excepthook = handle_exception

class LocaleManager:
    ## Handles loading and managing translations for multiple locales.
    def __init__(self, supported_locales, default_locale='eng'):
        self.supported_locales = supported_locales
        self.current_locale = default_locale
        self.translations = {}
        self.language_name = ""
        self.font_family = "Arial"  # Default font
        self.load_translations(self.current_locale)

    def set_locale(self, locale):
        ## Set the application locale and reload translations.
        if locale in self.supported_locales:
            if locale != self.current_locale:
                self.current_locale = locale
                self.load_translations(locale)

    def load_translations(self, locale):
        locale_file = os.path.join(sys.path[0], 'locales', f'{locale}.json')
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
                self.language_name = self.translations.get('language_name', locale)
                self.font_family = self.translations.get('font_family', "Arial")
        except FileNotFoundError:
            logging.error(f"Locale file not found: {locale_file}")
            self.show_error_message(f"Locale file not found: {locale_file}")
            self.translations = {}
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON file: {locale_file}")
            self.show_error_message(f"Error decoding JSON file: {locale_file}")
            self.translations = {}
        except Exception as e:
            logging.error(f"Unexpected error while loading translations: {str(e)}")
            self.show_error_message(f"Unexpected error while loading translations: {str(e)}")
            self.translations = {}

    def get_font_family(self):
        return self.font_family

    def get_translation(self, key, default_value=None):
        ## Retrieve a translation for the given key.
        return self.translations.get(key, default_value)

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.exec_()

class CustomTitleBar(QWidget):
    ## Custom title bar with minimize, maximize/restore, and close buttons.
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.title = title
        self.init_ui()

    def init_ui(self):
        ## Initialize the title bar UI.
        self.setAutoFillBackground(True)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  ## Remove margins around the layout

        self.title_label = QLabel(self.title, self)
        self.title_label.setFont(QFont("Times New Roman", 11))  ## Increased font size by 1
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
        ## Minimize the application window.
        self.window().showMinimized()

    def maximize_restore(self):
        ## Toggle between maximize and restore window size.
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def close_window(self):
        ## Close the application window.
        self.window().close()

class PoppableTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_tab_context_menu)
        self.tab_windows = {}
        self.tab_data_store = {}

        self.setStyleSheet("""
            QTabBar::tab { 
                background: #4d4d4d; 
                color: #00ced1; 
                padding: 12px; 
            }
            QTabBar::tab:selected { 
                background: #555; 
                color:  #1ffcff; 
            }
            QTabWidget::pane { 
                border: 1px solid #444; 
            }
        """)

        ## Dictionary of tools for easy access
        self.tools = {
            "STQ Editor Tool": stq_tool.STQTool,
            "Opus Header Injector": OpusHeaderInjector.OpusHeaderInjector,
            "Audio Calculator": AudioCalculator.AudioCalculator,
            "FolderMaker": FolderMaker.FolderMaker,
            "Hex Enc/Decoder": HexConverterEncoder.HexConverterEncoder,
            "Opus Converter": OpusConverter.OpusConverter,
            "Opus Metadata Extractor": OpusMetadataExtractor.OpusMetadataExtractor,
            "STQ Merge Tool": STQ_Merge.STQMergeTool,
            "MCA Converter" : MCAConverter.WavToMcaConverter,
            "MCA Forge" : MCA_Forge.MCA_Forge
        }
        self.tabBar().setFont(QFont("Arial", 11))

    def show_tab_context_menu(self, position):
        ## Show context menu for tab options like popping out.
        index = self.tabBar().tabAt(position)
        tab_name = self.tabText(index)
        if tab_name == "Main Hub":
            return  ## Skip the Main Hub tab

        menu = QMenu()

        ## Create the "New Instance" submenu
        new_instance_menu = menu.addMenu("New Instance")
        for tool_name in self.tools:
            new_instance_menu.addAction(tool_name, lambda t=tool_name: self.create_tool_instance(t))

        menu.addAction("Pop Out Tab", lambda: self.pop_out_tab(index))
        menu.exec_(self.mapToGlobal(position))

    def create_tool_instance(self, tool_name):
        tool_class = self.tools.get(tool_name)
        if tool_class:
            try:
                self.create_new_window(tool_class(), f"{tool_name} - New Instance", {})
            except Exception as e:
                logging.error(f"Failed to create tool instance '{tool_name}': {str(e)}")
                self.show_error_message(f"Failed to create tool instance '{tool_name}'. Please try again.")

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.exec_()

    def serialize_tab_state(self, widget):
        ## Serialize the state of the tab for potential restoration.
        state = {'title': self.tabText(self.indexOf(widget))}
        if hasattr(widget, 'text_edit') and hasattr(widget.text_edit, 'toPlainText'):
            state['text'] = widget.text_edit.toPlainText()
        if hasattr(widget, 'file_list') and hasattr(widget.file_list, 'count'):
            state['files'] = [widget.file_list.item(i).text() for i in range(widget.file_list.count())]
        return state

    def pop_out_tab(self, index):
        ## Pop out the selected tab into a new window.
        widget = self.widget(index)
        if widget:
            state = self.serialize_tab_state(widget)
            self.removeTab(index)
            self.create_new_window(type(widget)(), state['title'], state)

    def create_new_window(self, widget, title, state):
        ## Create a new window for the popped-out tab.
        new_window = QMainWindow()
        new_window.setWindowTitle(title)
        new_window.setCentralWidget(widget)
        new_window.resize(800, 600)
        new_window.show()
        self.tab_windows[title] = new_window
        self.setup_window_context_menu(new_window, widget, title)

    def setup_window_context_menu(self, window, widget, title):
        ## Set up the context menu for the popped-out window.
        window.setContextMenuPolicy(Qt.CustomContextMenu)
        window.customContextMenuRequested.connect(lambda pos: self.show_window_context_menu(window, widget, title, pos))

    def remerge_tab(self, widget, title):
        ## Re-merge the popped-out tab back into the main window.
        if title in self.tab_windows:
            self.tab_windows.pop(title).close()
        self.addTab(widget, title)
        if title in self.tab_data_store:
            self.deserialize_tab_state(widget, self.tab_data_store.pop(title))

    def show_window_context_menu(self, window, widget, title, position):
        ## Show context menu for options in the popped-out window.
        menu = QMenu(window)
        new_instance_menu = menu.addMenu("New Instance")
        for tool_name in self.tools:
            new_instance_menu.addAction(tool_name, lambda t=tool_name: self.create_tool_instance(t))
        menu.addAction("Re-merge Tab", lambda: self.remerge_tab(widget, title))
        menu.exec_(window.mapToGlobal(position))

class HbModkit(QMainWindow):
    ## Main application class for the Handburger Modkit.
    def __init__(self):
        super().__init__()
        self.locale_manager = LocaleManager(
            supported_locales=self.get_supported_locales(),
            default_locale='eng'
        )
        self.set_application_font()
        self.init_ui()
        
    def set_application_font(self):
        font_family = self.locale_manager.get_font_family()
        app.setFont(QFont(font_family, 10))

    def set_locale(self, locale):
        ## Set the application locale and reload translations.
        self.locale_manager.set_locale(locale)
        self.set_application_font()  # Update the application font
        self.create_menu_bar()  ## Recreate menu bar to apply translations
        self.update_main_hub_tab()  ## Update the Main Hub tab with new translations
        self.update_tool_translations()  ## Update all tool translations

    def get_supported_locales(self):
        ## Automatically detect available locales by scanning the 'locales' directory.
        locales_dir = os.path.join(sys.path[0], 'locales')
        supported_locales = set()
        if os.path.exists(locales_dir):
            for filename in os.listdir(locales_dir):
                if filename.endswith('.json'):
                    locale_code = os.path.splitext(filename)[0]
                    supported_locales.add(locale_code)
        else:
            logging.error(f"Locales directory not found at {locales_dir}")
            self.show_error_message("Locales directory not found.")
        return supported_locales

    def get_available_languages(self):
        ## Build a mapping from language names to locale codes by reading 'language_name' from each locale file.
        locales_dir = os.path.join(sys.path[0], 'locales')
        languages = {}
        if os.path.exists(locales_dir):
            for filename in os.listdir(locales_dir):
                if filename.endswith('.json'):
                    locale_code = os.path.splitext(filename)[0]
                    locale_file = os.path.join(locales_dir, filename)
                    try:
                        with open(locale_file, 'r', encoding='utf-8') as f:
                            translations = json.load(f)
                            language_name = translations.get('language_name', locale_code)
                            languages[language_name] = locale_code
                    except Exception as e:
                        logging.error(f"Error loading locale file {locale_file}: {str(e)}")
                        continue
        else:
            logging.error(f"Locales directory not found at {locales_dir}")
            self.show_error_message("Locales directory not found.")
        return languages

    def init_ui(self):
        ## Initialize the main UI.
        self.setWindowTitle(f"Handburger's Modkit v{VERSION}")
        self.setGeometry(100, 50, 1650, 1000)
        self.setWindowIcon(QIcon(self.get_icon_path("egg.ico")))

        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.tab_widget = PoppableTabWidget(self)
        main_layout.addWidget(self.tab_widget)

        self.setCentralWidget(central_widget)
        self.add_tabs()
        self.create_menu_bar()  ## Create the menu bar with the settings
        self.tab_widget.currentChanged.connect(self.toggle_stylesheet_based_on_tab)
        
        self.toggle_stylesheet_based_on_tab(0)
    
    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.exec_()

    def create_menu_bar(self):
        ## Create the settings menu and apply translations.
        menu_bar = self.menuBar()
        menu_bar.clear()

        settings_menu = menu_bar.addMenu(self.locale_manager.get_translation("settings_label", "Settings"))
        menu_bar.setStyleSheet("""
        QMenuBar {
            background-color: #2b2b2b;
            color: #ffebcd;
            font-size: 12px;
        }
        QMenuBar::item {
            background-color: #2b2b2b;
            color: #ffebcd; 
            padding: 5px 10px; 
            margin: 2px;
            min-width: 100px; 
        }
        QMenuBar::item:selected {  
            background-color: #555555; 
            color: #ffebcd;
        }
        QMenuBar::item:pressed {
            background-color: #333333; 
            color: #ffebcd;
        }
    """)

        ## Language selection submenu
        language_menu = QMenu(self.locale_manager.get_translation("language_label", "Language"), self)
        languages = self.get_available_languages()

        # Adding each language to the menu
        for language, locale in languages.items():
            language_menu.addAction(language, lambda l=locale: self.set_locale(l))

        settings_menu.addMenu(language_menu)

    def add_tabs(self):
        ## Add the "Main Hub" tab first
        self.tab_widget.addTab(MainHubTab(self.locale_manager), "Main Hub")
        
        ## Dictionary of the other tools
        tools = {
            "STQ Editor Tool": stq_tool.STQTool,
            "Opus Header Injector": OpusHeaderInjector.OpusHeaderInjector,
            "Audio Calculator": AudioCalculator.AudioCalculator,
            "FolderMaker": FolderMaker.FolderMaker,
            "Hex Enc/Decoder": HexConverterEncoder.HexConverterEncoder,
            "Opus Converter": OpusConverter.OpusConverter,
            "Opus Metadata Extractor": OpusMetadataExtractor.OpusMetadataExtractor,
            "STQ Merge Tool": STQ_Merge.STQMergeTool,
            "MCA Converter": MCAConverter.WavToMcaConverter,
            "MCA Forge": MCA_Forge.MCA_Forge
        }

        ## Sort the remaining tools alphabetically
        sorted_tools = {k: tools[k] for k in sorted(tools.keys())}
        
        ## Add the sorted tools as tabs
        for name, tool in sorted_tools.items():
            try:
                self.tab_widget.addTab(tool(), name)
            except Exception as e:
                print(f"Error adding tab '{name}': {e}")

    def get_icon_path(self, icon_name):
        try:
            assets_dir = os.path.join(sys.path[0], 'assets')
            icon_path = os.path.join(assets_dir, icon_name)
            if not os.path.exists(icon_path):
                raise FileNotFoundError(f"Icon not found at {icon_path}")
            return icon_path
        except FileNotFoundError as e:
            logging.error(str(e))
            self.show_error_message(f"Icon '{icon_name}' not found. Please check your assets directory.")
            return None

    def set_locale(self, locale):
        ## Set the application locale and reload translations.
        self.locale_manager.set_locale(locale)
        self.create_menu_bar()  ## Recreate menu bar to apply translations
        self.update_main_hub_tab()  ## Update the Main Hub tab with new translations
        self.update_tool_translations()  ## Update all tool translations
    
    def update_main_hub_tab(self):
        ## Updates the Main Hub tab with the current translations.
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "Main Hub":
                main_hub_tab = self.tab_widget.widget(i)
                if isinstance(main_hub_tab, MainHubTab):
                    main_hub_tab.update_translations(self.locale_manager.translations)

    def update_tool_translations(self):
        ## Updates all tools with the current translations.
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'update_translations'):
                widget.update_translations(self.locale_manager.translations)
    
    def toggle_stylesheet_based_on_tab(self, index):
        ## Toggle the stylesheet based on the selected tab
        tab_name = self.tab_widget.tabText(index)
        if tab_name == "Main Hub":
            # Apply the stylesheet when the "Main Hub" tab is selected
            self.setStyleSheet("""
                QMainWindow {
                    font-family: Arial;
                    background-color: #2c2c2c;
                    color: #ffebcd;
                }
                QTextBrowser {
                    background-color: #2c2c2c;
                    color: #ffebcd;
                    font:  13pt Arial;
                }
            """)
        else:
            # Remove the stylesheet when other tabs are selected
            self.setStyleSheet("")

class SplashScreen(QMainWindow):
    ## Splash screen displayed during application startup.
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        ## Initialize the splash screen UI.
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        ## Funny Splash Image
        splash_label = QLabel(self)
        pixmap = QPixmap(self.get_splash_image_path())
        if pixmap.isNull():
            splash_label.setText("Splash image not found.")
        else:
            pixmap = pixmap.scaled(1000, 800, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            splash_label.setPixmap(pixmap)
        splash_label.setAlignment(Qt.AlignCenter)

        ## Loading Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #3c3c3c;
                border-style: outset;
                border-radius: 6px;
                border: 2px solid #ffebcd; 
                text-align: center;
                font: bold 14px;
                padding: 2px;
                color: #000000;
            }                      
            QProgressBar::chunk {
                background-color: #30d5c8;
                width: 10px;
            }          
        """)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        layout.addWidget(splash_label)
        layout.addWidget(self.progress_bar)

        self.show_splash_screen()
        self.center_on_screen()

    def get_splash_image_path(self):
        try:
            assets_dir = os.path.join(sys.path[0], 'assets')
            for file_name in os.listdir(assets_dir):
                if file_name.lower().startswith("hbmodkit") and file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    return os.path.join(assets_dir, file_name)
            raise FileNotFoundError("No splash image found matching 'HBModkit*'.")
        except FileNotFoundError as e:
            logging.error(str(e))
            self.show_error_message("Splash image not found. Please make sure the assets directory contains a valid splash image.")
            return None

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.exec_()

    def center_on_screen(self):
        ## Center the splash screen on the user's display.
        screen = QDesktopWidget().screenGeometry()
        window_size = self.geometry()
        self.move((screen.width() - window_size.width()) // 2, (screen.height() - window_size.height()) // 2)

    def show_splash_screen(self):
        ## Display the splash screen with a simulated loading process.
        self.progress = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)  # Update every 30 ms
        self.show()

    def update_progress(self):
        self.progress += 1
        self.progress_bar.setValue(self.progress)
        if self.progress >= 100:
            self.timer.stop()
            self.close()

class MainHubTab(QWidget):
    def __init__(self, locale_manager):
        super().__init__()
        self.locale_manager = locale_manager
        self.scale_factor = 0.70  # 70% Scaling
        self.portrait_label = QLabel(self)

        # Initialize UI
        self.init_ui()

    def init_ui(self):
        # Set background color for the entire MainHubTab widget using QStyleSheet
        self.setStyleSheet("""
            QWidget {
                color: #ffebcd;             /* Text color */
                font-family: Arial;         /* Font style */
                font-size: 13px;            /* Font size for consistency */
            }
        """)
        # Create the main layout (horizontal: text on the left, portrait on the right)
        self.layout = QHBoxLayout()

        # Left column for the portrait image
        left_layout = QVBoxLayout()
        self.set_character_portrait()  # Set the portrait dynamically
        left_layout.addWidget(self.portrait_label)

        # Add a spacer to push the image to the bottom
        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Right column for text and links
        right_layout = QVBoxLayout()

        # Set style for the QTextBrowser to remove white background and use dark theme
        self.text_browser = QTextBrowser(self)
        self.text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #2c2c2c;
                color: #ffebcd;
                border: 2px solid #ffebcd;
                font: 13pt Arial;
            }
        """)
        right_layout.addWidget(self.text_browser)

        # Layout for external links (GitHub, Ko-fi)
        self.link_layout = QVBoxLayout()
        right_layout.addLayout(self.link_layout)

        # Add both the left and right layouts to the main horizontal layout
        self.layout.addLayout(left_layout)
        self.layout.addLayout(right_layout)

        # Set the layout for the widget
        self.setLayout(self.layout)

        # Add the links once during the initial setup
        self.add_links()

        # Initially set up the translations
        self.update_translations(self.locale_manager.translations)

    def set_character_portrait(self):
        # Set and scale the character portrait based on window size.
        try:
            portrait_path = self.get_resource_path("HandburgerPortrait.png")
            if portrait_path:
                pixmap = QPixmap(portrait_path)
                scaled_pixmap = pixmap.scaledToHeight(
                    int(self.height()),
                    Qt.SmoothTransformation
                )
                self.portrait_label.setPixmap(scaled_pixmap)
                self.portrait_label.setAlignment(Qt.AlignCenter)
                self.portrait_label.setStyleSheet("""
                    QLabel {
                        border: 2px solid black; /* Thickness and Colour */
                        border-radius: 5px; /*Rounded */
                    }
                """)
            else:
                self.portrait_label.setText("Portrait not found.")
                self.portrait_label.setAlignment(Qt.AlignCenter)
        except Exception as e:
            logging.error(str(e))
            self.portrait_label.setText("Error loading portrait.")
            self.portrait_label.setAlignment(Qt.AlignCenter)

    def get_resource_path(self, filename):
        # Get the path to a resource file in the assets directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(script_dir, 'assets', filename)
        if not os.path.exists(assets_path):
            logging.error(f"Resource not found: {filename}")
            self.show_error_message(f"Resource not found: {filename}")
            return None
        return assets_path

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.exec_()

    def add_links(self):
        # Add the GitHub and Ko-fi links to the layout
        try:
            github_icon = self.get_resource_path("github.png")
            kofi_icon = self.get_resource_path("ko-fi.png")

            if github_icon:
                self.link_layout.addLayout(self.create_link_layout(
                    github_icon,
                    self.locale_manager.get_translation('github_link', "GitHub - RTHKKona"),
                    "https://github.com/RTHKKona", 64
                ))

            if kofi_icon:
                self.link_layout.addLayout(self.create_link_layout(
                    kofi_icon,
                    self.locale_manager.get_translation('kofi_link', "Ko-fi - Handburger"),
                    "https://ko-fi.com/handburger", 64
                ))
        except Exception as e:
            logging.error(str(e))

    def create_link_layout(self, icon_path, text, url, icon_size):
        # Create a layout for a hyperlink with an icon.
        layout = QHBoxLayout()

        icon_label = QLabel(self)
        icon_label.setPixmap(QPixmap(icon_path).scaled(icon_size, icon_size, Qt.KeepAspectRatio))
        layout.addWidget(icon_label)

        link_label = QLabel(f'<a href="{url}" style="color: yellow;">{text}</a>', self)
        link_label.setOpenExternalLinks(True)
        link_label.setFont(QFont("Arial", 14))
        layout.addWidget(link_label)

        layout.setAlignment(Qt.AlignLeft)
        return layout

    def update_translations(self, translations):
        # Method to update translations
        about_text = f"""
        <html>
        <body>
        <h2>{translations.get('handburger_modkit_title', "Handburger's Modkit")}</h2>
        <p>{translations.get('version', f'This is version v{VERSION}.').replace('{version}', VERSION)}</p>
        <br>
        <p>{translations.get('about_content', 'This multi-use modkit was developed to assist with and automate various modding tasks for Monster Hunter Generations Ultimate.')}</p>
        <p>{translations.get('tutorial', 'Click on any tab to use it. Right-click a tab to pop-out or create a new instance of a particular tab.')}</p>
        <p>{translations.get('plug', 'Find more about the developer (me!) and support them below.')}</p>
        <p>{translations.get('thanks', 'Massive thanks to my translators, ffmpeg & Dasding for their conversion functions and dependencies, masagrator for his NXAenc variation for MHGU, and vgmstream for their audio software and dependencies.')}</p>
        <br>
        <h3>{translations.get('tool_descriptions_title', 'Tool Descriptions')}</h3>
        <ul>
        """

        tools = {
            "Audio Calculator": (AudioCalculator.VERSION, translations.get('audio_calculator_desc', "A utility for calculating audio properties such as bitrate, file size, and duration.")),
            "FolderMaker": (FolderMaker.VERSION, translations.get('foldermaker_desc', "Helps in organizing and creating folders necessary for modding projects.")),
            "Hex Enc/Decoder": (HexConverterEncoder.VERSION, translations.get('hex_enc_decoder_desc', "Encodes or decodes hexadecimal data, useful for file conversions and analysis.")),
            "MCA Converter": (MCAConverter.VERSION, translations.get('mcaconvert_desc', "Converts audio files into .MCA format. For use alongside MCA Forge.")),
            "MCA Forge": (MCA_Forge.VERSION, translations.get('mcaforge_desc', "Allows users to import two .MCA files—an original and a replacement—and merge key elements to create a new custom header with a preset structure.")),
            "Opus Converter": (OpusConverter.VERSION, translations.get('nsopus_converter_desc', "Converts audio files to Opus format, with support for Nintendo Switch Opus MHGU-specific formats.")),
            "Opus Header Injector": (OpusHeaderInjector.VERSION, translations.get('opus_header_injector_desc', "Allows users to inject or modify .Opus headers within .Opus files.")),
            "Opus Metadata Extractor": (OpusMetadataExtractor.VERSION, translations.get('opus_metadata_extractor_desc', "Extracts metadata from Opus files for easier management and editing.")),
            "STQ Editor Tool": (stq_tool.VERSION, translations.get('stq_editor_tool_desc', "A tool for editing and viewing STQ/STQR files, including hex pattern analysis.")),
            "STQ Merge Tool": (STQ_Merge.VERSION, translations.get('stq_merge_tool_desc', "Merging and managing STQR file conflicts between multiple mods."))
        }

        sorted_tools = dict(sorted(tools.items()))
        for tool, (version, description) in sorted_tools.items():
            about_text += f"<li><b>{tool} (v{version}):</b> {description}</li>"

        about_text += "</ul></body></html>"

        self.text_browser.setHtml(about_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    splash = SplashScreen()
    main_window = HbModkit()
    # Close splash and show main window after a delay
    QTimer.singleShot(3000, lambda: (splash.close(), main_window.show()))
    sys.exit(app.exec_())
