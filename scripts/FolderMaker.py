# FolderMaker module
# Version management
VERSION = "1.1.1"

import os
import sys
import subprocess
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, 
    QMessageBox, QTextEdit, QApplication,
    QAction, QWidget
)
from PyQt5.QtGui import QFont


class FolderMaker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dark_mode = True  # Start in dark mode by default
        self.initUI()
        self.apply_initial_theme()  # Apply the initial theme
        self.display_welcome_message()  # Display the welcome message and ASCII art on launch

    def initUI(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        bottom_layout = QHBoxLayout()

        # Create a menu bar
        menubar = self.menuBar()  # Use menuBar() method of QMainWindow
        help_menu = menubar.addMenu("Help")
        help_action = QAction("About", self)
        help_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(help_action)

        self.cmd_output = QTextEdit(self)
        self.cmd_output.setReadOnly(True)
        self.cmd_output.setFont(QFont("Consolas", 11))  # Set monospaced font for CMD style
        main_layout.addWidget(self.cmd_output)

        self.folder_input = QLineEdit(self)
        self.folder_input.setPlaceholderText("Click 'Browse' to select a directory you'd like to analyse. (likely nativeNX)")
        bottom_layout.addWidget(self.folder_input)

        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self.browse_folder)
        bottom_layout.addWidget(browse_button)

        self.file_input = QLineEdit(self)
        self.file_input.setPlaceholderText("Input exact file you want to replace. (i.e bgm_v03.opus)")
        bottom_layout.addWidget(self.file_input)

        create_button = QPushButton("Create Directory/Folders", self)
        create_button.clicked.connect(self.create_folders)
        bottom_layout.addWidget(create_button)

        self.toggle_theme_btn = QPushButton("Toggle Theme", self)
        self.toggle_theme_btn.clicked.connect(self.toggle_theme)
        bottom_layout.addWidget(self.toggle_theme_btn)

        main_layout.addLayout(bottom_layout)

        self.setWindowTitle('FolderMaker')
        self.setGeometry(100, 70, 1600, 1000)  # Set the window size to 1600x800, positioned at 100,100

        self.update_font_size()  # Increase the font size

    def update_font_size(self):
        font = QFont("Consolas", 11)  # Increased font size by 1 point
        widgets = [
            self.folder_input, self.file_input, self.cmd_output,
            self.toggle_theme_btn
        ]
        for widget in widgets:
            widget.setFont(font)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if folder:
            self.folder_input.setText(folder)

    def create_folders(self):
        analysis_folder = self.folder_input.text().strip()
        filename = self.file_input.text().strip()

        if not analysis_folder or not filename:
            QMessageBox.warning(self, "Input Error", "Please provide both a folder and a file name.")
            return

        relative_path = self.find_file(analysis_folder, filename)
        
        if relative_path:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            result_path = self.create_path_to_file(script_directory, analysis_folder, relative_path)
            
            if result_path:
                self.log(f"Created folders leading to: {result_path}")
                self.open_directory(result_path)
            else:
                self.log("No matching folders were created.")
        else:
            self.log(f"Error: File '{filename}' not found in the directory structure.")

    def find_file(self, base_path, filename):
        for root, _, files in os.walk(base_path):
            if filename in files:
                return os.path.relpath(root, base_path)
        return None

    def create_path_to_file(self, script_directory, analysis_folder, relative_path):
        root_folder_name = os.path.basename(analysis_folder)
        target_path = os.path.join(script_directory, root_folder_name, relative_path)
        
        try:
            os.makedirs(target_path, exist_ok=True)
            return target_path
        except Exception as e:
            self.log(f"Error creating directory {target_path}: {e}")
            return None

    def show_about_dialog(self):
        about_text = (
            "FolderMaker\n"
            f"Version {VERSION}\n\n"
            "Creates a set of predefined folders within a selected directory."
        )
        QMessageBox.about(self, "About", about_text)
    
    def open_directory(self, path):
        try:
            if os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                subprocess.Popen(['open', path])
        except Exception as e:
            self.log(f"Error opening directory: {e}")

    def log(self, message, is_preformatted=False):
        if is_preformatted:
            self.cmd_output.append(f"<pre>{message}</pre>")
        else:
            self.cmd_output.append(message)

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_initial_theme(self):
        # Apply the theme once during initialization.
        self.apply_theme()

    def apply_theme(self):
        # Apply the appropriate stylesheet based on the current theme.
        common_styles = """
            QPushButton {
                font-family: Consolas;
                font-size: 12pt;
                padding: 6px;
            }
        """
        
        dark_mode_styles = """
            QWidget { background-color: #2b2b2b; color: #ffebcd; }
            QTextEdit { background-color: #4d4d4d; color: #ffebcd; }
            QLabel { color: #ffebcd; }
            QLineEdit { background-color: #4d4d4d; color: #ffebcd; border: 1px solid #ffebcd; }
            QPushButton { background-color: #4d4d4d; color: #ffebcd; }
        """
        
        light_mode_styles = """
            QWidget { background-color: white; color: black; }
            QTextEdit { background-color: white; color: black; }
            QLabel { color: black; }
            QLineEdit { background-color: white; color: black; border: 1px solid black; }
            QPushButton { background-color: #f0f0f0; color: black; }
        """
        
        # Combine common styles with the mode-specific styles
        if self.dark_mode:
            full_stylesheet = common_styles + dark_mode_styles
        else:
            full_stylesheet = common_styles + light_mode_styles

        # Apply the combined stylesheet
        self.setStyleSheet(full_stylesheet)


    def display_welcome_message(self):
        #Display ASCII art and welcome message when the app launches.
        art = r"""                                                                                                                                         
                                                                       
                  {Æ›zÆü                                                                   
                    6  íÅ                   ÏígÇÇÇÇGü                                      
               ÆÇ  ÅÏÇ› —Þ              zÆÆ—›        ÞÆÇ                                   
              üÇ›—Æ— ÏÆ› Å            ÇÆ›              ›gÆü                                
               GÆg››› {Å››zÆÅÅÅÆ    ÇÆ›                   GG                               
                  íÆ—›         ›Æ  Æ{                      ›Æí                             
                   Æ›  › ›Æ—››››  g›                         ÅÅ                            
                    ÅÅ —Æü      —Æ›                           ÇÆ                           
                     Ç›g       —Ï                              zÆ                          
                     6—Æ      —Ç     › ›    ›    ››  ›   ›      zÆÇ                        
                     íÞÆ     zÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆÆ6                       
                      ÆÅ6    Æ gÆÆÆÆÆÆÆÆ—ÅÆ  ÆÆÆÆÆÆÆÆÆ ÆÆí        Æg                       
                      Å{g6  g  GÆÆÆÆÆÆÆÆÅÆ›  ÞÆÆÆÆÆÆÆgÆÆg          Æz                      
                       gÞ—ÆÆz   ÆÆÆÆÆÆÆÆÆÞ    ÆÆÆÆÆÆÆÆÆÆ›           gÇ                     
                        zÆ—Æ     ÆÆÆÆÆÆÆÆ      ÆÆÆÆÆÆÆÆ               gÏ                   
                          ÆÏ       ÅÆÆg{         ——›               {Æ  ›Æ                  
                         íÆ                 ›Ç                       ÆG  ÆÏ                
                         íg              ÏÅÅ       g6                ÞÆÆ› ÅÏ               
                         g—        Þ›            gÅÏ                 ›ÆÆgÇ Æz              
                         Æ          ÅÅÅg6666ÇÅÆÅzÅ›                   ÆÆ  6 Æ              
                         Æ           G—        Çg                     ÆÆ› üí›g             
                         Æ            6Ç›    ÞG                       ÆÆ  Å{ Æ             
                         Æ              ›gÅg› ›                       ÆÆÅ—zÆÞ              
                         g—                                      ›ÅÆg{›ÞÞGÆ{Æ              
                         íÆ                                     Æ—  ›íÆÆ—í—{g              
                          Æ›                                    Æ› › ››ÆÆ›{Åg              
                          íÆ                                    ÅÆ›      —Æz               
                           zÏ                                   {ÆÆgGíGíÆg                 
                            ÏÇ                                   ›ÆÆÆÏ                     
                             zÆ                                   ÅÆ                       
                               Çü                               {ÆÏ                        
                                 gü                           ›ÆÇ                          
                                  íGÆ›                      ÏÆÇ                            
                                     íÆÆ6›              zÆÆÆz                              
                                     íG—Å ›{GGÆÆÆÆÆgGí— ›Æ 6í                              
                                      Å{í                Þ——í                              
                                       íÆ—6            ÏÆígz                               
                                         ÆüÆ         {Å—Æí                                 
                                          gÅÅü     ›Å Å6                                   
                                züü6ü6666üÏÆÞ›Å{  gü Æz   zÏüÅÆÆÆÆÆÆGGÏ                    
                            zGÆÆ6í—› › › ›››—› ›GÆ{ íÆÆÆÆÅ{››        ›{g                   
                          zÆÆ›                › ›Æ›› › ››   ››› ››››››{6ü                  
                          ÇÆÆÆÆÆÆÆÆÆÆÆÆÆÆÞÞgí{{zzíííííízzzzzzzzzzzzzzzz                    
        """
        self.log(art, is_preformatted=True)
        self.log(
            f"\nYou see that? That funny little characta?<br><br>"
            f"\nThis FolderMaker tool helps you create nested directories easy. No more right-clicking and New Folder.<br>"
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FolderMaker()
    window.show()
    sys.exit(app.exec_())
