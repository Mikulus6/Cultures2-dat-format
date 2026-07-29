from datetime import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from map_data import MapData

map_data = MapData()

window_size            = (90, 172)
button_size            = (10, 1)
button_vertical_margin = 1

file_types = (("data files",      "*.dat"),
              ("cultures 2 maps", "*.c2m"),
              ("all Files",       "*.*"))

def update_button_states():
    state = tk.NORMAL if map_data._is_loaded else tk.DISABLED  # noqa
    button_save.config(state=state)
    button_extract.config(state=state)
    button_uptade.config(state=state)

def new():
    global map_data
    try:
        map_data = MapData()
        update_button_states()
    except Exception as e:
        messagebox.showerror("Error", str(e))

def load():
    global map_data
    filename = filedialog.askopenfilename(filetypes=file_types)
    if filename:
        try:
            map_data.load(filename)
            update_button_states()
        except Exception as e:
            messagebox.showerror("Error", str(e))

def save():
    global map_data
    filename = filedialog.asksaveasfilename(filetypes=file_types, defaultextension=".dat")
    if filename:
        try:
            map_data.save(filename)
            update_button_states()
        except Exception as e:
            messagebox.showerror("Error", str(e))

def extract():
    global map_data
    base_directory = filedialog.askdirectory()
    if base_directory:
        try:
            timestamp_folder = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            target_directory = os.path.join(base_directory, timestamp_folder)
            os.makedirs(target_directory, exist_ok=True)
            map_data.extract(target_directory)
            update_button_states()
        except Exception as e:
            messagebox.showerror("Error", str(e))

def pack():
    global map_data
    directory = filedialog.askdirectory()
    if directory:
        try:
            map_data.pack(directory)
            update_button_states()
        except Exception as e:
            messagebox.showerror("Error", str(e))

def update():
    global map_data
    try:
        map_data.update()
        update_button_states()
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title(MapData.__name__)
root.geometry(f"{window_size[0]}x{window_size[1]}")
root.attributes("-toolwindow", True)
root.resizable(False, False)

button_new     = tk.Button(root, text="new"    , width=button_size[0], height=button_size[1], command=new)
button_load    = tk.Button(root, text="load"   , width=button_size[0], height=button_size[1], command=load)
button_save    = tk.Button(root, text="save"   , width=button_size[0], height=button_size[1], command=save)
button_extract = tk.Button(root, text="extract", width=button_size[0], height=button_size[1], command=extract)
button_pack    = tk.Button(root, text="pack"   , width=button_size[0], height=button_size[1], command=pack)
button_uptade  = tk.Button(root, text="update" , width=button_size[0], height=button_size[1], command=pack)

button_new.pack    (pady=button_vertical_margin)
button_load.pack   (pady=button_vertical_margin)
button_save.pack   (pady=button_vertical_margin)
button_extract.pack(pady=button_vertical_margin)
button_pack.pack   (pady=button_vertical_margin)
button_uptade.pack (pady=button_vertical_margin)

update_button_states()

if __name__ == "__main__":
    root.mainloop()
