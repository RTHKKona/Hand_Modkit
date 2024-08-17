
# Hand_Modkit

Hand_Modkit is a versatile tool designed for modding Monster Hunter Generations Ultimate (MHGU). With a suite of specialized utilities, this toolkit empowers modders to easily edit, analyze, and manage various game files. Whether you're injecting audio headers, calculating audio properties, or organizing mod folders, Hand_Modkit simplifies the complex tasks involved in MHGU modding.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/L3L711AIP8)

## Features

- **STQ Editor Tool**: Edit and view STQ/STQR files, including hex pattern analysis.
- **Opus Header Injector**: Modify Opus headers within audio files.
- **Audio Calculator**: Calculate audio properties such as bitrate, file size, and duration.
- **FolderMaker**: Organize and create folders for your modding projects.
- **Hex Enc/Decoder**: Encode or decode hexadecimal data, useful for file conversions and analysis.
- **NSOpus Converter**: Convert audio files to and from the Opus format, with support for NSOpus-specific formats.
- **Opus Metadata Extractor**: Extract metadata from Opus files for easier management and editing.

## Getting Started

### Prerequisites

- **Python 3.x**: Ensure you have Python installed on your machine. You can download it [here](https://www.python.org/downloads/).
- **PyQt5**: Install PyQt5, the library used for the GUI. You can install it via pip:
  \`\`\`bash
  pip install PyQt5
  \`\`\`

### Installation

1. Clone the repository:
   \`\`\`bash
   git clone https://github.com/RTHKKona/Hand_Modkit.git
   \`\`\`
2. Navigate to the project directory:
   \`\`\`bash
   cd Hand_Modkit
   \`\`\`
3. Install the required Python packages:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

### Usage

To start the Hand_Modkit application, run the following command:
\`\`\`bash
python Hb_Modkit.py
\`\`\`
This will open the main application window, where you can access the various tools via the tabs.

## Future Features

I'm working to improve Hand_Modkit and expand its capabilities. Here's a glimpse of what's coming in future updates:

- Audio to MCA Converter: A tool to convert various audio formats directly to MCA, simplifying the audio modding process.
- MCA Header Injector/Editor: An advanced tool for injecting and editing headers in MCA files, allowing for more detailed control over audio modifications.
- Kuriimu2 Compatibility: Integration with Kuriimu2, including support for .dll files, opening .arc files, and editing .tex files. This will enhance Hand_Modkit's versatility and allow seamless editing of game assets.
- Compile into Full Exe: The goal is to compile Hand_Modkit into a standalone executable, making it easier to distribute and use without requiring a Python environment.
- Better GUI for Easier Use: We're working on refining the graphical user interface to make it more intuitive and user-friendly, ensuring that even new users can navigate and use the tool effectively.

Stay tuned for these updates!

## Contributing

Contributions are welcome! If you have suggestions for improvements, feel free to fork the repository, make your changes, and submit a pull request.

### Bug Reports & Feature Requests

Please use the [issue tracker](https://github.com/RTHKKona/Hand_Modkit/issues) to report bugs or request new features.

## Support

If you find this tool useful and would like to support its development, consider buying me a coffee!

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/L3L711AIP8)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
