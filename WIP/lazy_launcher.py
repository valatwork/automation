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
    "Little Nav Map": "C:\\Users\\Val\\OneDrive\\Desktop\\Little Navmap\\LittleNavmap-win64-2.8.10\\littlenavmap.exe",
    "FlyByWire": "C:\\Users\\Val\\AppData\\Local\\Programs\\fbw-installer\\FlyByWire Installer.exe",
    "FSUIPC7": "C:\\FSUIPC7\\FSUIPC7.exe",
    "Landing Rate Monitor": "C:\\Program Files (x86)\\Landing Rate Monitor\\LRM.exe",
    "SimToolkitPro": "C:\\Users\\Val\\AppData\\Local\\Programs\\simtoolkitpro\\SimToolkitPro.exe"
}

def start_selected_programs():
    log_box.delete(1.0, tk.END)  # clear log box
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

def is_program_running(path):
    for process in psutil.process_iter(['name']):
        if process.info['name'] == path.split("\\")[-1]:
            return True
    return False

def quit_selected_programs():
    log_box.delete(1.0, tk.END)  # clear log box
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

checkbox_vars = {}
checkboxes = []

for program in programs:
    var = tk.IntVar()
    checkbox = tk.Checkbutton(root, text=program, variable=var)
    checkbox.pack(anchor='w')
    checkbox_vars[program] = var
    checkboxes.append(checkbox)

# create the start and quit buttons
button_frame = tk.Frame(root)

start_button = tk.Button(button_frame, text="Start", borderwidth=2, relief="groove", bg="green", fg="white", command=start_selected_programs)
start_button.pack(side="left", padx=5)

quit_button = tk.Button(button_frame, text="Quit", borderwidth=2, relief="groove", bg="red", fg="white", command=quit_selected_programs)
quit_button.pack(side="left", padx=5)

button_frame.pack(pady=10)

# create the log textbox
log_box = tk.Text(root, height=10, width=50)
log_box.pack(pady=10)

# create scrollbar for the log textbox
scrollbar = tk.Scrollbar(root, command=log_box.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_box.config(yscrollcommand=scrollbar.set)

# set focus on the log textbox so that the user can start typing right away
log_box.focus_set()

# run the main event loop
root.mainloop()

