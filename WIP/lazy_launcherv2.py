import subprocess
import psutil
import tkinter as tk
from tkinter import filedialog, Button
import os
import datetime

root = tk.Tk()
root.title("Lazy Launcher")

programs = {}

# starts the checked program(s)
def start_selected_programs():
    for program, path in programs.items():
        if checkbox_vars[program].get() == 1:
            if is_program_running(path):
                log_box.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M')}] {program} is already running\n")
            else:
                log_box.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M')}] Starting {program}...\n")
                subprocess.Popen(path)
    for checkbox in checkboxes:
        checkbox.deselect()

# checks if the program is already running
def is_program_running(path):
    for process in psutil.process_iter(['name']):
        if process.info['name'] == os.path.basename(path):
            return True
    return False

# force quit
def quit_selected_programs():
    for program, path in programs.items():
        if is_program_running(path):
            log_box.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M')}] Terminating {program}...\n")
            try:
                process = subprocess.Popen(['taskkill', '/F', '/IM', os.path.basename(path)], stdout=subprocess.PIPE)
                output, error = process.communicate()
                log_box.insert(tk.END, output.decode())
            except subprocess.CalledProcessError as e:
                log_box.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M')}] Error terminating process {e}\n")
    for checkbox in checkboxes:
        checkbox.deselect()

# add program
def add_program():
    program_path = filedialog.askopenfilename()
    if program_path:
        program_name = os.path.basename(program_path)
        programs[program_name] = program_path
        var = tk.IntVar()
        checkbox = tk.Checkbutton(root, text=program_name, variable=var)
        checkbox.pack(anchor='w')
        checkbox_vars[program_name] = var
        checkboxes.append(checkbox)

# remove program
def remove_program():
    selected_programs = [program for program, var in checkbox_vars.items() if var.get() == 1]
    for program in selected_programs:
        checkboxes[program].destroy()
        del checkbox_vars[program]
        del programs[program]

# checkbox frame
checkbox_vars = {}
checkboxes = []

# buttons frame
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# add program button
add_button = tk.Button(button_frame, text="Add Program", borderwidth=2, relief="groove", command=add_program)
add_button.pack(side="left", padx=5)

# remove program button
remove_button = tk.Button(button_frame, text="Remove Program", borderwidth=2, relief="groove", command=remove_program)
remove_button.pack(side="left", padx=5)

# start button
start_button = tk.Button(button_frame, text="Start", borderwidth=2, relief="groove", bg="green", fg="white", command=start_selected_programs)
start_button.pack(side="left", padx=5)

# quit button
quit_button = tk.Button(button_frame, text="Quit", borderwidth=2, relief="groove", bg="red", fg="white", command=quit_selected_programs)
quit_button.pack(side="left", padx=5)

# create the log textbox
log_box = tk.Text(root, height=10, width=50)
log_box.pack(pady=10)

# run the main event loop
root.mainloop()