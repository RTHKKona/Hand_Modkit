
# Hand_Modkit

Hand_Modkit, also known as the Handburger Modkit, is a versatile tool designed for modding Monster Hunter Generations Ultimate (MHGU). With a suite of specialized utilities, this toolkit empowers modders to easily edit, analyze, and manage various game files. Whether you're injecting audio headers, calculating audio properties, or organizing mod folders, Hand_Modkit simplifies the complex tasks involved in MHGU modding.

[![]("https://gamebanana.com/tools/embeddables/17846?type=thumbnail")](https://gamebanana.com/tools/17846)

## Features

- **STQ Editor Tool**: Edit and view STQ/STQR files, including hex pattern analysis and specific hexadecimal editing.
- **STQ Merge Tool**: Merge modified STQR files for multiple mod usage. Includes hexadecimal editing, conflict management and saving functionality.
- **Opus Header Injector**: Modify Opus headers and inject edited ones onto headerless Opus audio files.
- **Audio Calculator**: Calculate audio properties such as bitrate, file size, and duration.
- **FolderMaker**:  Create folders and directories for your projects.
- **Hex Enc/Decoder**: Encode or decode hexadecimal data, useful for file conversions and analysis.
- **NSOpus Converter**: Convert audio files to and from the Opus format, with support for Nintendo Switch .Opus format for MHGU.
- **Opus Metadata Extractor**: Extract metadata from Opus files for easier management and editing.

## Screenshots

<img src="./assets/Screenshot.png" alt="Screenshot" width="600"/>
<img src="./assets/Screenshot1.png" alt="Screenshot1" width="600"/>
<img src="./assets/Screenshot2.png" alt="Screenshot2" width="600"/>
<img src="./assets/Screenshot3.png" alt="Screenshot3" width="600"/>
<img src="./assets/Screenshot4.png" alt="Screenshot4" width="600"/>
<img src="./assets/Screenshot5.png" alt="Screenshot5" width="600"/>
<img src="./assets/Screenshot6.png" alt="Screenshot6" width="600"/>

## Getting Started

### Prerequisites

- **Python 3.x**: Ensure you have Python installed on your machine. You can download it [here](https://www.python.org/downloads/).
- **PyQt5**: Install PyQt5, the library used for the GUI. You can install it via pip:
  ```
  pip install PyQt5
  ```

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/RTHKKona/Hand_Modkit.git
   ```
2. Navigate to the project directory:
   ```
   cd Hand_Modkit
   ```
3. Open up Hb_Modkit.py or any standalone python script in /scripts/

## Future Features

I'm working to improve Hand_Modkit and expand its capabilities. Here's a glimpse of what's coming in future updates:

- STQR Conflict Manager: Fixes multi-mod conflicts of the stqr files.
- Audio to MCA Converter: A tool to convert various audio formats directly to MCA, simplifying the audio modding process.
- MCA Header Injector/Editor: An advanced tool for injecting and editing headers in MCA files, allowing for more detailed control over audio modifications.
- Kuriimu2 Compatibility: Integration with Kuriimu2, including support for .dll files, opening .arc files, and editing .tex files. This will enhance Hand_Modkit's versatility and allow seamless editing of game assets.
- Compile into Full Exe: The goal is to compile Hand_Modkit into a standalone executable, making it easier to distribute and use without requiring a Python environment.
- Better GUI for Easier Use: We're working on refining the graphical user interface to make it more intuitive and user-friendly, ensuring that even new users can navigate and use the tool effectively.

Stay tuned for these updates!

# Contributions

Contributions are welcome! If you have suggestions for improvements, feel free to fork the repository, make your changes, and submit a pull request.

## Contributers
#### Lead Developer
![Handburger](https://github.com/user-attachments/assets/a927ae22-ae98-4c3d-94ed-63e170ef1daf)

#### Translators
![LucioPalmucci](https://github.com/user-attachments/assets/b270bb04-fb07-4ea5-843b-a426a5596af3)
![nichoconutzy](https://github.com/user-attachments/assets/79dd1a82-94e9-422b-a8dd-5cfac00132ce)

## Bug Reports & Feature Requests

Please use the [issue tracker](https://github.com/RTHKKona/Hand_Modkit/issues) to report bugs or request new features.

## Support

If you find this tool useful and would like to support its development, consider buying me a coffee!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/L3L711AIP8)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
