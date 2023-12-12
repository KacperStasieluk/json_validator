import os

import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.x = self.y = 0

    def showtip(self, text, x, y):
        if self.tipwindow or not text:
            return
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f'+{x}+{y}')
        label = tk.Label(tw, text=text, justify=tk.LEFT,
                         background='#ffffe0', relief=tk.SOLID, borderwidth=1,
                         font=('tahoma', '8', 'normal'))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def createToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

class JsonValidatorApp:
    def __init__(self, root):
        self.root = root
        root.title('JSON Validator')

        self.tooltip = None

        self.tree_frame = tk.Frame(root)
        self.tree_frame.grid(row=0, column=0, sticky='nsew')

        self.tree = ttk.Treeview(self.tree_frame, columns=('Name', 'Path', 'Status', 'Error', 'Error Line', 'Edit'), show='headings')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Path', text='Path')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Error', text='Error Description')
        self.tree.heading('Error Line', text='Error Line')
        self.tree.heading('Edit', text='Edit')
        self.tree.column('Error Line', width=60)
        self.tree.column('Path', width=50)
        self.tree.column('Status', width=50)
        self.tree.column('Edit', width=100)

        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient='vertical', command=self.tree.yview)
        self.scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        self.tree.bind('<Motion>', self.on_motion)
        self.tree.bind('<ButtonRelease-1>', self.on_item_click)

        self.load_button = tk.Button(root, text='Load JSON', command=self.load_json)
        self.load_button.grid(row=1, column=0, sticky='ew')

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

    def load_json(self):
        file_paths = filedialog.askopenfilenames(filetypes=[('JSON Files', '*.json')])
        for file_path in file_paths:
            file_name = file_path.split("/")[-1]
            try:
                with open(file_path, 'r') as file:
                    json.load(file)
                    status = 'Valid'
                    error = ''
                    error_line = None
            except json.JSONDecodeError as e:
                status = 'Invalid'
                error_line = e.lineno
                error = f'{e.msg} at line {e.lineno}, column {e.colno}'

            self.tree.insert('', 'end', values=(file_name, file_path, status, error, error_line if error_line else '', '[Click to edit]'))

    def on_item_click(self, event):
        region = self.tree.identify('region', event.x, event.y)
        row_id = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if region == 'cell' and column == '#6':
            item = self.tree.item(row_id)
            file_path = item['values'][1]
            self.edit_file(file_path)

    def edit_file(self, file_path):
        try:
            if os.name == 'nt':
                os.startfile(file_path)
            else:
                opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
                subprocess.call([opener, file_path])
        except Exception as e:
            messagebox.showerror('Error', f'Nie można otworzyć pliku: {e}')

    def get_file_snippet(self, file_path, error_line):
        if error_line is None:
            return 'No error'
        lines = []
        with open(file_path, 'r') as file:
            for i, line in enumerate(file, 1):
                if error_line - 2 <= i <= error_line + 2:
                    lines.append(f'{i}: {line.strip()}')
        return '\n'.join(lines)

    def on_motion(self, event):
        row_id = self.tree.identify_row(event.y)
        column_id = self.tree.identify_column(event.x)
        if row_id and (column_id == '#4' or column_id == '#5'):
            row = self.tree.item(row_id)
            file_path, error_line = row['values'][1], row['values'][4]
            if error_line:
                snippet = self.get_file_snippet(file_path, error_line)
                self.show_tooltip(event, snippet)
        else:
            self.show_tooltip(event, None)

    def show_tooltip(self, event, text):
        if self.tooltip:
            self.tooltip.hidetip()
        if text:
            self.tooltip = ToolTip(self.tree)
            self.tooltip.showtip(text, event.x_root, event.y_root)

root = tk.Tk()
app = JsonValidatorApp(root)
root.mainloop()
