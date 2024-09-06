# Version Define
VERSION = "0.6.1"


import sys, os, random, json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, 
    QDesktopWidget, QHBoxLayout, QTextBrowser, QPushButton, QStyle, QMenu,
    QProgressBar, QSpacerItem, QSizePolicy, 
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from scripts import (
    stq_tool, OpusHeaderInjector, AudioCalculator, FolderMaker, HexConverterEncoder, 
    NSOpusConverter, OpusMetadataExtractor, STQ_Merge, MCAConverter, MCA_Forge
)


class LocaleManager:
    ## Handles loading and managing translations for multiple locales.
    def __init__(self, supported_locales, default_locale='eng'):
        self.supported_locales = supported_locales
        self.current_locale = default_locale
        self.translations = {}
        self.load_translations(self.current_locale)

    def set_locale(self, locale):
        ## Set the application locale and reload translations.
        if locale in self.supported_locales:
            if locale != self.current_locale:
                self.current_locale = locale
                self.load_translations(locale)

    def load_translations(self, locale):
        ## Loads the translations from the JSON file for the given locale.
        locale_file = os.path.join(os.path.dirname(__file__), 'locales', f'{locale}.json')
        try:
            with open(locale_file, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except FileNotFoundError:
            pass  ## Locale file not found, proceed without translations
        except json.JSONDecodeError:
            pass  ## JSON decoding error, proceed without translations
        except Exception:
            pass  ## General exception, proceed without translations

    def get_translation(self, key, default_value=None):
        ## Retrieve a translation for the given key.
        return self.translations.get(key, default_value)


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
        self.title_label.setFont(QFont("", 11))  ## Increased font size by 1
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

        ## Dictionary of tools for easy access
        self.tools = {
            "STQ Editor Tool": stq_tool.STQTool,
            "Opus Header Injector": OpusHeaderInjector.OpusHeaderInjector,
            "Audio Calculator": AudioCalculator.AudioCalculator,
            "FolderMaker": FolderMaker.FolderMaker,
            "Hex Enc/Decoder": HexConverterEncoder.HexConverterEncoder,
            "NSOpus Converter": NSOpusConverter.NSOpusConverter,
            "Opus Metadata Extractor": OpusMetadataExtractor.OpusMetadataExtractor,
            "STQ Merge Tool": STQ_Merge.STQMergeTool,
            "MCA Converter" : MCAConverter.WavToMcaConverter,
            "MCA Forge" : MCA_Forge.MCA_Forge
        }

    def show_tab_context_menu(self, position):
        ## Show context menu for tab options like popping out.
        index = self.tabBar().tabAt(position)
        tab_name = self.tabText(index)
        if tab_name == "About":
            return  ## Skip the About tab

        menu = QMenu()

        ## Create the "New Instance" submenu
        new_instance_menu = menu.addMenu("New Instance")
        for tool_name in self.tools:
            new_instance_menu.addAction(tool_name, lambda t=tool_name: self.create_tool_instance(t))

        menu.addAction("Pop Out Tab", lambda: self.pop_out_tab(index))
        menu.exec_(self.mapToGlobal(position))

    def create_tool_instance(self, tool_name):
        ## Create a new instance of the selected tool.
        tool_class = self.tools.get(tool_name)
        if tool_class:
            self.create_new_window(tool_class(), f"{tool_name} - New Instance", {})
    
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
            supported_locales={'eng', 'zho', 'spa', 'ind'},  ## Add locale support here
            default_locale='eng'
        )
        self.init_ui()

    def init_ui(self):
        ## Initialize the main UI.
        self.setWindowTitle(f"Handburger Modkit v{VERSION}")
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
        self.create_menu_bar()  ## Create the menu bar with the settings

    def create_menu_bar(self):
        ## Create the settings menu and apply translations.
        menu_bar = self.menuBar()
        menu_bar.clear()

        settings_menu = menu_bar.addMenu(self.locale_manager.get_translation("settings_label", "Settings"))
        menu_bar.setStyleSheet("""
        QMenuBar {
            background-color: #2b2b2b;  /* Background color of the menu bar */
            color: #ffebcd;  /* Default text color */
            font-size: 11px;
        }
        QMenuBar::item {
            background-color: #2b2b2b;  /* Background color of items */
            color: #ffebcd;  /* Default text color of items */
            padding: 5px 10px; /* Padding top&bottom, leftright */
            margin: 2px; /* buffer */
            min-width: 100px; 
        }
        QMenuBar::item:selected {  /* Hover effect */
            background-color: #555555;  /* Background color on hover */
            color: #ffebcd;  /* Text color on hover */
        }
        QMenuBar::item:pressed {
            background-color: #333333;  /* Background color when pressed */
            color: #ffebcd;  /* Text color when pressed */
        }
    """)

        ## Language selection submenu
        language_menu = QMenu(self.locale_manager.get_translation("language_label", "Language"), self)
        for language, locale in {'English': 'eng', '中文': 'zho', 'Español': 'spa', 'Bahasa Indonesia': 'ind'}.items():
            language_menu.addAction(language, lambda l=locale: self.set_locale(l))
        settings_menu.addMenu(language_menu)

    def add_tabs(self):
        ## Add tool tabs to the main window.
        tools = {  ## Add Tools here when created, remember to add commas
            "About": AboutTab,  ## Initialize AboutTab with locale_manager
            "STQ Editor Tool": stq_tool.STQTool,
            "Opus Header Injector": OpusHeaderInjector.OpusHeaderInjector,
            "Audio Calculator": AudioCalculator.AudioCalculator,
            "FolderMaker": FolderMaker.FolderMaker,
            "Hex Enc/Decoder": HexConverterEncoder.HexConverterEncoder,
            "NSOpus Converter": NSOpusConverter.NSOpusConverter,
            "Opus Metadata Extractor": OpusMetadataExtractor.OpusMetadataExtractor,
            "STQ Merge Tool": STQ_Merge.STQMergeTool,
            "MCA Converter" : MCAConverter.WavToMcaConverter,
            "MCA Forge" : MCA_Forge.MCA_Forge,
        }
        sorted_tools = {k: tools[k] for k in sorted(tools.keys())}
        
        for name, tool in sorted_tools.items():
            try:
                if name == "About":
                    self.tab_widget.addTab(tool(self.locale_manager),name)
                else:
                    self.tab_widget.addTab(tool(), name)
            except Exception as e:
                print(f"error adding tab '{name}' : {e}")

    def apply_dark_mode_theme(self):
        ## Apply dark mode styling to the main window.
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; color: #ffebcd; }
            QTabWidget::pane { border: 1px solid #444; }
            QWidget { background-color: #3c3c3c; color: #ffffff; }
            QTabBar::tab { background: #4d4d4d; color: #ffffff; padding: 10px; }
            QTabBar::tab:selected { background: #555; }
        """)

    def get_icon_path(self, icon_name):
        ## Get the path to an icon file in the assets directory.
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
        icon_path = os.path.join(assets_dir, icon_name)
        if not os.path.exists(icon_path):
            raise FileNotFoundError(f"Icon not found at {icon_path}")
        return icon_path
    
    def set_locale(self, locale):
        ## Set the application locale and reload translations.
        self.locale_manager.set_locale(locale)
        self.create_menu_bar()  ## Recreate menu bar to apply translations
        self.update_about_tab()  ## Update the About tab with new translations
        self.update_tool_translations()  ## Update all tool translations
    
    def update_about_tab(self):
        ## Updates the About tab with the current translations.
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == "About":
                about_tab = self.tab_widget.widget(i)
                if isinstance(about_tab, AboutTab):
                    about_tab.update_translations(self.locale_manager.translations)

    def update_tool_translations(self):
        ## Updates all tools with the current translations.
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'update_translations'):
                widget.update_translations(self.locale_manager.translations)


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
        pixmap = QPixmap(self.get_splash_image_path()).scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        splash_label.setPixmap(pixmap)
        splash_label.setAlignment(Qt.AlignCenter)

        ## Loading Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #3c3c3c;
                color: #fff;
                border-style: none;
                border-radius: 5px;
                text-align: center;
            }                      
            QProgressBar::chunk {
                background-color: #555;
                width: 20px;
            }          
        """)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        layout.addWidget(splash_label)
        layout.addWidget(self.progress_bar)

        self.show_splash_screen()
        self.center_on_screen()

    def get_splash_image_path(self):
        ## Get the path to the splash image in the assets directory.
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
        splash_image_path = os.path.join(assets_dir, "funnycharacta.png")
        if not os.path.exists(splash_image_path):
            raise FileNotFoundError(f"Splash image not found at {splash_image_path}")
        return splash_image_path

    def center_on_screen(self):
        ## Center the splash screen on the user's display.
        screen = QDesktopWidget().screenGeometry()
        window_size = self.geometry()
        self.move((screen.width() - window_size.width()) // 2, (screen.height() - window_size.height()) // 2)

    def show_splash_screen(self):
        ## Display the splash screen with a simulated loading process.
        for i in range(101):
            QTimer.singleShot(i * 30, lambda v=i: self.progress_bar.setValue(v))
        QTimer.singleShot(3000, self.close)
        self.show()

class AboutTab(QWidget):
    def __init__(self, locale_manager):
        super().__init__()
        self.locale_manager = locale_manager
        self.scale_factor = 0.70  # Scale to 60% of window height
        self.portrait_label = QLabel(self)
        
        # Timer to throttle resizing events
        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.set_character_portrait)
        
        self.init_ui()

    def init_ui(self):
        # Create the main layout (horizontal: text on the left, portrait on the right)
        self.layout = QHBoxLayout()

        # Left column for text and links
        right_layout = QVBoxLayout()
        self.text_browser = QTextBrowser(self)
        right_layout.addWidget(self.text_browser)

        # Create a layout for the links (GitHub, Ko-fi)
        self.link_layout = QVBoxLayout()
        right_layout.addLayout(self.link_layout)

        # Right column for the portrait
        left_layout = QVBoxLayout()
        self.set_character_portrait()  # Set the portrait dynamically
        left_layout.addWidget(self.portrait_label)

        # Add a spacer to push the image to the bottom
        left_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Add both the left and right layouts to the main horizontal layout
        self.layout.addLayout(left_layout)
        self.layout.addLayout(right_layout)

        # Set the layout for the widget
        self.setLayout(self.layout)

        # Add the links once during the initial setup
        self.add_links()

        # Initially set up the translations (this won't add links again)
        self.update_translations({})

    def resizeEvent(self, event):
        # Handle window resizing and throttle the portrait resizing
        # Start a timer when the window is resized; delay execution by 100ms
        self.resize_timer.start(100)

    def set_character_portrait(self):
        # Set and scale the character portrait based on window size.
        try:
            portrait_path = self.get_resource_path("HandburgerPortrait.png")
            pixmap = QPixmap(portrait_path)

            # Calculate the scaled height as 60% of the window's height
            scaled_height = int(self.height() * self.scale_factor)
            scaled_pixmap = pixmap.scaledToHeight(
                scaled_height,
                Qt.SmoothTransformation
            )

            self.portrait_label.setPixmap(scaled_pixmap)
            self.portrait_label.setAlignment(Qt.AlignCenter)
            self.portrait_label.setStyleSheet("""
                QLabel {
                    border: 2px solid black; /* Thickness and Colour*/
                    border-radius: 5px; /*Rounded*/
                }
                
            """)
        except FileNotFoundError:
            self.portrait_label.setText("Portrait not found.")
            self.portrait_label.setAlignment(Qt.AlignCenter)

    def get_resource_path(self, filename):
        #Get the path to a resource file in the assets directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(script_dir, 'assets', filename)
        if not os.path.exists(assets_path):
            raise FileNotFoundError(f"Resource not found: {filename}")
        return assets_path

    def add_links(self):
        #Add the GitHub and Ko-fi links to the layout
        try:
            self.link_layout.addLayout(self.create_link_layout(
                self.get_resource_path("github.png"),
                self.locale_manager.get_translation('github_link', "GitHub - RTHKKona"),
                "https://github.com/RTHKKona", 64
            ))

            self.link_layout.addLayout(self.create_link_layout(
                self.get_resource_path("ko-fi.png"),
                self.locale_manager.get_translation('kofi_link', "Ko-fi - Handburger"),
                "https://ko-fi.com/handburger", 64
            ))
        except FileNotFoundError as e:
            print(f"Error loading link images: {e}")

    def create_link_layout(self, icon_path, text, url, icon_size):
        #Create a layout for a hyperlink with an icon.
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
        #Update the About tab content with the current translations.
        about_text = f"""
        <h2>{translations.get('handburger_modkit_title', 'Handburger Modkit')}</h2>
        <p>{translations.get('version', f'This is version {VERSION}.').replace('{version}', VERSION)}<br><br></p>
        <p>{translations.get('about_content', 'This multi-use tool was developed to assist with and automate various modding tasks for Monster Hunter Generations Ultimate.')}</p>
        <p>{translations.get('tutorial', 'Click on any tab to use it. Right-click a tab to pop-out or create a new instance of a particular tab.')}</p>
        <p>{translations.get('plug', 'Find more about the developer (me!) and support them below.')}</p>
        <p>{translations.get('thanks', 'Massive thanks to my translators, ffmpeg & Dasding for their conversion functions, masagrator for the NXAenc variation for MHGU, and vgmstream for their audio software and dependencies.')}</p>
        <br>
        <h3>{translations.get('tool_descriptions_title', 'Tool Descriptions')}</h3>
        <ul>
        """

        tools = {
            "STQ Editor Tool": translations.get('stq_editor_tool_desc', "A tool for editing and viewing STQ/STQR files, including hex pattern analysis."),
            "STQ Merge Tool": translations.get('stq_merge_tool_desc', "Merging and managing STQR file conflicts between multiple mods."),
            "Opus Header Injector": translations.get('opus_header_injector_desc', "Allows users to inject or modify .Opus headers within .Opus files."),
            "Audio Calculator": translations.get('audio_calculator_desc', "A utility for calculating audio properties such as bitrate, file size, and duration."),
            "FolderMaker": translations.get('foldermaker_desc', "Helps in organizing and creating folders necessary for modding projects."),
            "MCA Converter": translations.get('mcaconvert_desc', "Converts audio files into .MCA format. For use with the MCA Header Injector for modding."),
            "MCA Forger": translations.get('mcaforge_desc', "Allows users to import two .MCA files—an original and a replacement—and merge key elements to create a new custom header with a preset structure."),
            "Hex Enc/Decoder": translations.get('hex_enc_decoder_desc', "Encodes or decodes hexadecimal data, useful for file conversions and analysis."),
            "NSOpus Converter": translations.get('nsopus_converter_desc',"Converts audio files to and from the Opus format, with support for Nintendo Switch Opus MHGU-specific formats."),
            "Opus Metadata Extractor": translations.get('opus_metadata_extractor_desc', "Extracts metadata from Opus files for easier management and editing.")
        }

        sorted_tools = dict(sorted(tools.items()))
        for tool, description in sorted_tools.items():
            about_text += f"<li><b>{tool}:</b> {description}</li>"

        about_text += "</ul>"

        self.text_browser.setHtml(about_text)
        self.text_browser.setOpenExternalLinks(True)

        # Set font size
        font = QFont()
        font.setPointSize(11)
        self.text_browser.setFont(font)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    main_window = HbModkit()
    main_window.setWindowState(Qt.WindowMinimized)
    
    splash = SplashScreen()
    splash.show()
    splash_duration = random.randint(3000,7000)

    event_loop = QEventLoop()
    QTimer.singleShot(splash_duration, event_loop.quit)
    
    event_loop.exec_()

    main_window.setWindowState(Qt.WindowNoState)    
    main_window.showNormal()

    sys.exit(app.exec_())
