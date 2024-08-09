# Handburger's STQ Reader Tool

**Handburger's STQ Reader Tool** is a Python-based application designed to analyze and read `.stqr` files, providing a comprehensive interface for examining hexadecimal data. This tool is particularly useful for those working with audio files and data within the `.stqr` format, offering easy-to-use functionality to inspect and manage hex data, with features such as pattern recognition and flexible grid views.

## Features

- **Hexadecimal Viewer**: Display and inspect raw hex data from `.stqr` files in an organized and readable format.
- **Pattern Recognition**: Automatically detect and process specific data patterns within the hex content, such as sound file references and metadata.
- **Interactive Data Grid**: Visualize parsed data in a table format with resizable and auto-adjusting headers.
- **Random Easter Egg**: 20% chance of displaying an `egg.png` image upon loading a file, adding a bit of fun to your work.
- **Theming**: Toggle between dark and light modes for better readability depending on your preference.
- **Customizable Interface**: Adjust header sizes, and the application automatically spaces out headers to ensure they are legible on startup.
- **Dynamic App Title**: The application title dynamically updates to include the currently loaded file, making it easy to keep track of your work.

## Installation

### Prerequisites

- Python 3.x
- PyQt5

### Installation Steps

1. **Clone the repository:**

    ```bash
    git clone https://github.com/YourUsername/your-repo-name.git
    cd your-repo-name
    ```

2. **Install dependencies:**

    You can install the required Python packages using pip:

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the application:**

    ```bash
    python stq_tool.py
    ```

## Usage

1. **Loading a File:**
   - Click the "Load .stqr File" button to open and load a `.stqr` file. The application will parse the file and display its contents in both a text editor and a data grid.

2. **Viewing Hex Data:**
   - The hex data of the loaded file is displayed in the text editor, where you can inspect the raw data.

3. **Pattern Search:**
   - Use the "Search Patterns" button to automatically identify and parse known patterns in the hex data, such as sound file references.

4. **Customizing the Interface:**
   - Double-click column headers to auto-size them to fit the content.
   - Use the "Increase Header Size" and "Decrease Header Size" buttons to adjust the font size of the headers.

5. **Toggle Dark/Light Mode:**
   - Switch between dark and light themes to suit your preferences.

6. **Clear Data:**
   - Use the "Clear" button to reset the interface and start over with a new file.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes with a descriptive message.
4. Push your changes to your forked repository.
5. Open a pull request to the main repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Special thanks to the contributors of PyQt5 for providing the tools necessary to build this application.
- Inspired by the need to manage and inspect `.stqr` files effectively in a user-friendly way.

## Support

If you encounter any issues or have questions, feel free to open an issue in the [GitHub repository](https://github.com/YourUsername/your-repo-name/issues) or reach out via email.

---

*Handburger's STQ Reader Tool* is designed with flexibility and ease of use in mind, ensuring that your work with `.stqr` files is as smooth as possible. Enjoy!
