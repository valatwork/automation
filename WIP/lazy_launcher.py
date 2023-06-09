import subprocess
import psutil
import tkinter as tk
import os
import datetime

root = tk.Tk()
root.title("Lazy Launcher")
# root.geometry("400x250")
# root.resizable(False, False)

programs = {
    "Program1": "[path]",
    "Program2": "[path]",
    "Program3": "[path]",
    "Program4": "[path]",
    "Program5": "[path]"
}

# starts the checked program(s)
def start_selected_programs():
    # log_box.delete(1.0, tk.END)  # clear log box
    for program, path in programs.items():
        if checkbox_vars[program].get() == 1:
            if is_program_running(path):
                log_box.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M')}] {program} is already running\n")
            else:
                log_box.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M')}] Starting {program}...\n")
                subprocess.Popen(path)
    # uncheck all checkboxes
    for checkbox in checkboxes:
        checkbox.deselect()
        
# checks if the program is already running
def is_program_running(path):
    for process in psutil.process_iter(['name']):
        if process.info['name'] == path.split("\\")[-1]:
            return True
    return False

# force quit
def quit_selected_programs():
    # log_box.delete(1.0, tk.END)  # clear log box
    for program, path in programs.items():
        if is_program_running(path):
            log_box.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M')}] Terminating {program}...\n")
            try:
                process = subprocess.Popen(['taskkill', '/F', '/IM', path.split("\\")[-1]], stdout=subprocess.PIPE)
                output, error = process.communicate()
                log_box.insert(tk.END, output.decode())
            except subprocess.CalledProcessError as e:
                log_box.insert(tk.END, f"[{datetime.datetime.now().strftime('%H:%M')}] Error terminating process {e}\n")
    # uncheck all checkboxes
    for checkbox in checkboxes:
        checkbox.deselect()
        
# checkbox frame
checkbox_vars = {}
checkboxes = []

for program in programs:
    var = tk.IntVar()
    checkbox = tk.Checkbutton(root, text=program, variable=var)
    checkbox.pack(anchor='w')
    checkbox_vars[program] = var
    checkboxes.append(checkbox)

# buttons frame
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# start button
start_button = tk.Button(button_frame, text="Start", borderwidth=2, relief="groove", bg="green", fg="white", command=start_selected_programs)
start_button.pack(side="left", padx=5)

# quit button
quit_button = tk.Button(button_frame, text="Quit", borderwidth=2, relief="groove", bg="red", fg="white", command=quit_selected_programs)
quit_button.pack(side="left", padx=5)

# create the log textbox
log_box = tk.Text(root, height=10, width=50)
log_box.pack(pady=10)

# log scrollbar
# scrollbar = tk.Scrollbar(root, command=log_box.yview)
# scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
# log_box.config(yscrollcommand=scrollbar.set)

# run the main event loop
root.mainloop()

