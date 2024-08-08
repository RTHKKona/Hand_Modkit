import os
import glob
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import struct
import shutil

class STQReaderWriter:
    def __init__(self, root):
        self.root = root
        self.root.title("STQ Reader/Writer Tool")
        self.file_data = []  # This will store data for each file

        # Set up the GUI layout
        self.setup_gui()

    def setup_gui(self):
        self.label = tk.Label(self.root, text="Drag and drop .stqr files or folders here", width=50, height=10, borderwidth=2, relief="groove")
        self.label.pack(pady=20)
        
        # Bind the label to a file selection event
        self.label.bind("<Button-1>", self.select_files)
        
        self.table = None
        self.current_file_label = None

    def select_files(self, event=None):
        # Open a file dialog to select files or folders
        file_paths = filedialog.askopenfilenames(title="Select .stqr files or folders", filetypes=[("STQ files", "*.stq *.stqr"), ("All files", "*.*")])
        
        for file_path in file_paths:
            if os.path.isdir(file_path):
                self.scan_folder(file_path)
            else:
                self.process_file(file_path)

        if self.file_data:
            self.display_table()

    def scan_folder(self, folder_path):
        # Recursively scan through folders and subfolders
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(('.stq', '.stqr')):
                    self.process_file(os.path.join(root, file))

    def process_file(self, file_path):
        with open(file_path, 'rb') as file:
            hex_data = file.read()

        # Extract relevant data from the hex_data
        file_size = os.path.getsize(file_path)
        duration = self.get_duration(hex_data)
        channels = self.get_channels(hex_data)
        sample_rate = self.get_sample_rate(hex_data)
        loop_start = self.get_loop_start(hex_data)
        loop_end = self.get_loop_end(hex_data)

        self.file_data.append({
            "Path": file_path,
            "Name": os.path.basename(file_path),
            "File Size": file_size,
            "Duration": duration,
            "Channels": channels,
            "Sample Rate": sample_rate,
            "Loop Start": loop_start,
            "Loop End": loop_end,
        })

    # Functions to extract data - Customize these with the correct hex offsets
    def get_duration(self, hex_data):
        # Replace 0x10 with the correct offset for Duration
        return struct.unpack('<I', hex_data[0x10:0x14])[0]

    def get_channels(self, hex_data):
        # Replace 0x14 with the correct offset for Channels
        return struct.unpack('<I', hex_data[0x14:0x18])[0]

    def get_sample_rate(self, hex_data):
        # Replace 0x18 with the correct offset for Sample Rate
        return struct.unpack('<I', hex_data[0x18:0x1C])[0]

    def get_loop_start(self, hex_data):
        # Replace 0x1C with the correct offset for Loop Start
        return struct.unpack('<I', hex_data[0x1C:0x20])[0]

    def get_loop_end(self, hex_data):
        # Replace 0x20 with the correct offset for Loop End
        return struct.unpack('<I', hex_data[0x20:0x24])[0]

    def display_table(self):
        self.df = pd.DataFrame(self.file_data)
        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(padx=20, pady=20)

        # Display the currently edited file
        self.current_file_label = tk.Label(self.root, text="Currently editing: None")
        self.current_file_label.pack(pady=10)

        # Create the table for editing
        self.table = tk.Text(self.table_frame, height=20, width=100)
        self.table.insert(tk.END, self.df.to_string(index=False))
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(self.table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.table.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.table.yview)

        # Add save button
        self.save_button = tk.Button(self.root, text="Save", command=self.save_edits)
        self.save_button.pack(pady=10)

    def save_edits(self):
        edited_text = self.table.get("1.0", tk.END)
        edited_df = pd.read_csv(pd.compat.StringIO(edited_text), delim_whitespace=True)

        for index, row in edited_df.iterrows():
            original_row = self.df.iloc[index]
            if not row.equals(original_row):
                self.current_file_label.config(text=f"Currently editing: {row['Name']}")
                self.edit_file(row)

        messagebox.showinfo("Info", "Files saved successfully!")

    def edit_file(self, row):
        file_path = row["Path"]
        backup_path = file_path + ".bak"
        
        # Create a backup before editing
        shutil.copyfile(file_path, backup_path)

        with open(file_path, 'r+b') as file:
            hex_data = file.read()

            # Modify the hex_data according to the new values
            hex_data = self.modify_hex_data(hex_data, row)

            # Write back the modified data
            file.seek(0)
            file.write(hex_data)
            file.truncate()

    def modify_hex_data(self, hex_data, row):
        # Modify each relevant part of the file using the offsets
        # Replace 0x00 with the correct offset for each data type

        # Modify File Size
        file_size = struct.pack('<I', row["File Size"])
        hex_data = hex_data[:0x00] + file_size + hex_data[0x04:]  # Replace 0x00 with actual offset for file size

        # Modify Duration
        duration = struct.pack('<I', row["Duration"])
        hex_data = hex_data[:0x10] + duration + hex_data[0x14:]  # Replace 0x10 with actual offset for duration

        # Modify Channels
        channels = struct.pack('<I', row["Channels"])
        hex_data = hex_data[:0x14] + channels + hex_data[0x18:]  # Replace 0x14 with actual offset for channels

        # Modify Sample Rate
        sample_rate = struct.pack('<I', row["Sample Rate"])
        hex_data = hex_data[:0x18] + sample_rate + hex_data[0x1C:]  # Replace 0x18 with actual offset for sample rate

        # Modify Loop Start
        loop_start = struct.pack('<I', row["Loop Start"])
        hex_data = hex_data[:0x1C] + loop_start + hex_data[0x20:]  # Replace 0x1C with actual offset for loop start

        # Modify Loop End
        loop_end = struct.pack('<I', row["Loop End"])
        hex_data = hex_data[:0x20] + loop_end + hex_data[0x24:]  # Replace 0x20 with actual offset for loop end

        return hex_data

if __name__ == "__main__":
    root = tk.Tk()
    app = STQReaderWriter(root)
    root.mainloop()
