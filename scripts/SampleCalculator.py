import tkinter as tk
from decimal import Decimal, getcontext
import webbrowser

# Set precision high enough to handle all operations accurately
getcontext().prec = 20

# Constants
SAMPLE_RATE = Decimal('48000')

class AudioCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Duration and Samples Calculator")

        self.mode = tk.StringVar(value="samples_to_duration")

        # Display Entry
        self.display = tk.Entry(root, font=("Arial", 18), bd=10, insertwidth=4, width=25, borderwidth=4)
        self.display.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # Mode Selection
        tk.Radiobutton(root, text="Samples to Duration", variable=self.mode, value="samples_to_duration").grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        tk.Radiobutton(root, text="Duration to Samples", variable=self.mode, value="duration_to_samples").grid(row=1, column=2, columnspan=2, padx=10, pady=5, sticky="w")

        # Create Number Buttons
        buttons = [
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2),
            ('0', 5, 0), ('.', 5, 1)
        ]

        for (text, row, col) in buttons:
            self.create_button(text, row, col)

        # Function Buttons
        self.create_button("C", 5, 2, self.clear_display)
        self.create_button("Calculate", 6, 0, self.calculate, colspan=4, width=20)

        # Adding Menu Bar
        menu_bar = tk.Menu(root)
        root.config(menu=menu_bar)

        # Add About Me Menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About Me", command=self.show_about)

    def create_button(self, text, row, col, command=None, colspan=1, width=4):
        if command is None:
            command = lambda t=text: self.append_to_display(t)
        tk.Button(self.root, text=text, padx=10, pady=10, font=("Arial", 14), command=command,
                  width=width, height=2, borderwidth=2, relief="solid").grid(row=row, column=col, columnspan=colspan, padx=5, pady=5)

    def append_to_display(self, value):
        self.display.insert(tk.END, value)

    def clear_display(self):
        self.display.delete(0, tk.END)

    def calculate(self):
        input_value = self.display.get()
        if not input_value:
            tk.messagebox.showerror("Input Error", "Please enter a value.")
            return

        try:
            if self.mode.get() == "samples_to_duration":
                samples = Decimal(input_value)
                result = self.samples_to_duration(samples)
            elif self.mode.get() == "duration_to_samples":
                minutes, seconds = map(Decimal, input_value.split(":"))
                result = self.duration_to_samples(minutes, seconds)
            else:
                raise ValueError("Invalid mode selected.")
            self.display.delete(0, tk.END)
            self.display.insert(tk.END, result)
        except ValueError as e:
            tk.messagebox.showerror("Input Error", f"Invalid input: {e}")

    def samples_to_duration(self, samples):
        total_seconds = samples / SAMPLE_RATE
        minutes = int(total_seconds // Decimal(60))
        seconds = total_seconds - Decimal(minutes) * Decimal(60)
        return f"{minutes:02d}:{seconds:09.6f}"

    def duration_to_samples(self, minutes, seconds):
        total_seconds = minutes * Decimal(60) + seconds
        samples = total_seconds * SAMPLE_RATE
        return int(samples)

    def show_about(self):
        about_window = tk.Toplevel(self.root)
        about_window.title("About Me")
        about_window.geometry("400x200")

        about_text = tk.Text(about_window, wrap="word", font=("Arial", 12), padx=10, pady=10)
        about_text.insert(tk.END, "Audio Duration and Samples Calculator\n\n"
                                  "Created by Handburger\n\n"
                                  "GitHub: https://github.com/RTHKKona\n"
                                  "Ko-fi: https://ko-fi.com/handburger\n\n"
                                  "Click on the links to visit.")
        about_text.config(state="disabled")

        # Make the links clickable
        about_text.tag_config("link", foreground="blue", underline=1)
        about_text.tag_bind("link", "<Button-1>", self.open_link)

        # Apply the tag to the URLs
        start_idx = about_text.search("https://github.com/RTHKKona", "1.0", tk.END)
        end_idx = f"{start_idx}+{len('https://github.com/RTHKKona')}c"
        about_text.tag_add("link", start_idx, end_idx)

        start_idx = about_text.search("https://ko-fi.com/handburger", "1.0", tk.END)
        end_idx = f"{start_idx}+{len('https://ko-fi.com/handburger')}c"
        about_text.tag_add("link", start_idx, end_idx)

        about_text.pack(fill=tk.BOTH, expand=True)

    def open_link(self, event):
        webbrowser.open(event.widget.get("sel.first", "sel.last"))

if __name__ == "__main__":
    root = tk.Tk()
    calculator = AudioCalculator(root)
    root.mainloop()
