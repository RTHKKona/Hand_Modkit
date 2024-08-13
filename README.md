# Handburger's MHGU Mod Platform (Hand_Modkit)

## Overview

My MHGU Mod Platform, also known as Hand_Modkit, is a comprehensive tool designed for modding Monster Hunter Generations Ultimate (MHGU). This platform integrates multiple tools into a single, user-friendly application, allowing users to easily modify and customize their game files.

### Features

- **STQ Tool**: Edit and manage .opus STQR files with an intuitive hex editor.
- **Opus Header Injector**: Modify and inject headers into headerless OPUS audio files.
- **FolderMaker** : Create a directory to the exact name of the file you want to replace.
- **Hex De/Encoder** : Convert from hexadecimal to little Endian 32-bit signed integer and Windows ANSI.
- **Audio Calculator**: Convert between audio samples and duration in MM:SS.s format, with support for high-precision calculations. (For Opus Header Injector)
- **Adjustable Font Size**: Increase or decrease the font size within the application using `Ctrl +` and `Ctrl -` hotkeys.

## Getting Started

### Prerequisites

Ensure you have the following installed on your system:

- Python 3.6 or higher
- PyQt5
- Decimal module (included in Python's standard library)

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/Hand_Modkit.git
    cd Hand_Modkit
    ```

2. **Install the required Python packages**:
    ```bash
    pip install -r requirements.txt
    ```

   **Note**: If a `requirements.txt` file is not available, you can manually install `PyQt5`:
    ```bash
    pip install PyQt5
    ```

3. **Run the application**:
    ```bash
    python Hb_Modtool.py
    ```

### Usage

- **STQ Tool**: Open, view, and edit STQR files. Use the hex editor to directly modify file contents in the grid.
- **Opus Header Injector**: Load OPUS files, modify their headers, and save the changes. Preview the header modifications before saving.
- **Audio Calculator**: Convert audio samples to duration and vice versa. Enter duration in `MM:SS.s` format for accurate sample calculations.

### Hotkeys

- **Increase Font Size**: `Ctrl +`
- **Decrease Font Size**: `Ctrl -`

## Screenshots

![STQ Tool](/assets/Cap1.png) 
*Caption: A screenshot showing the STQ Tool in action.*

![Opus Header Injector](/assets/Cap2.png)
*Caption: A screenshot of the Opus Header Injector interface.*

![Audio Calculator](/assets/Cap3.png)
*Caption: The Audio Calculator performing a conversion.*

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -m 'Add some new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a Pull Request.
6. [![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/L3L711AIP8) ;) 

Please ensure that your code follows the project's style guidelines and includes appropriate tests.

## License

This project is licensed under the GPL 3.0 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Special thanks to the MHGU modding community for their ongoing support and contributions.
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro) for the GUI framework.
