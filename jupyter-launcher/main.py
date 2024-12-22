import os
import json
import subprocess
import PySimpleGUI as sg
from typing import Dict, List, Optional # additional imports


CONFIG_FILE = "jupyter_launcher_config.json"
MAX_RECENTS = 5  # Maximum number of recent folders to track
DEFAULT_PORT = "8888" # added default port
DEFAULT_THEME = "Dark" # added default theme

def load_config() -> Dict:
    """Load settings from a JSON file, if it exists."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Exception:
    except json.JSONDecodeError:
        sg.popup_error("Error reading configuration file. Using default settings.")
        return {}


def save_config(config: Dict) -> None:
    """Save settings to a JSON file."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        sg.popup_error(f"Error saving configuration file: {e}")

def get_pinned_folder_labels(config):
    """Return a list of pinned folder labels for the pinned combo box."""
    return [item["label"] for item in config["pinned_folders"]]


def get_pinned_folder_labels(config: Dict) -> List[str]:
    """Find the pinned folder dict by its label. Returns None if not found."""
    return [item["label"] for item in config.get("pinned_folders", [])]


def find_pinned_by_label(config: Dict, label: str) -> Optional[Dict]:
    """Find the pinned folder dict by its path. Returns None if not found."""
    return next((item for item in config.get("pinned_folders", []) if item["label"] == label), None)


def find_pinned_by_path(config: Dict, path: str) -> Optional[Dict]:
    """Find the pinned folder dict by its path. Returns None if not found."""
    return next((item for item in config.get("pinned_folders", []) if item["path"] == path), None)


def pin_folder(config: Dict, folder: str, label: str) -> None:
    """
    Pin a folder with a given label.
    If the folder is already pinned, update its label.
    Otherwise, create a new pinned entry.
    """
    existing = find_pinned_by_path(config, folder)
    if existing:
        # Update label if path is already pinned
        existing["label"] = label
    else:
        # Create a new pinned item
        config.setdefault("pinned_folders", []).append({"path": folder, "label": label})


def unpin_folder(config: Dict, folder: str) -> None:
    """Unpin the folder that matches the given path."""
    config["pinned_folders"] = [item for item in config.get("pinned_folders", []) if item["path"] != folder]


def add_to_recents(folder: str, config: Dict) -> None:
    """Add the given folder to 'recent_folders', maintaining MAX_RECENTS limit."""
    recents = config.setdefault("recent_folders", [])
    if folder in recents:
        recents.remove(folder)
    recents.insert(0, folder)
    config["recent_folders"] = recents[:MAX_RECENTS]


def delete_recent_folder(config: Dict, folder: str) -> None:
    """Delete the given folder from 'recent_folders'."""
    config["recent_folders"] = [item for item in config.get("recent_folders", []) if item != folder]


def create_window(config: Dict) -> sg.Window:
    """Create the main application window."""
    if config.get("theme") == "Dark":
        sg.theme("DarkBlue3")
    else:
        sg.theme("SystemDefault")

    pinned_labels = get_pinned_folder_labels(config)


    layout = [
        [
            sg.Column([
                [sg.Text("Jupyter Notebook Launcher", font=("Arial", 14, "bold"))],
                [
                    sg.Text("Pinned Folder:", size=(12, 1)),
                    sg.Combo(
                        values=pinned_labels,
                        default_value=pinned_labels[0] if pinned_labels else "",
                        key="pinned_combo",
                        size=(40, 1),
                        enable_events=True
                    )
                ],
                [
                    sg.Text("Browse Folder:", size=(12, 1)),
                    sg.InputText(key="folder_input", size=(38, 1)),
                    sg.FolderBrowse("Browse")
                ],
                [
                    sg.Button("Pin/Unpin", size=(10, 1), key="pin_unpin_button"),
                    sg.Button("Rename Pinned", size=(12, 1), key="rename_pinned_button"),
                ],
                [sg.HorizontalSeparator()],
                [
                    sg.Text("Port:"),
                    sg.InputText(config.get("port", DEFAULT_PORT), size=(6, 1), key="port_input")
                ],
                [
                    sg.Radio("Light", "THEME", default=(config.get("theme", DEFAULT_THEME) == "Light"), key="theme_light"),
                    sg.Radio("Dark", "THEME", default=(config.get("theme", DEFAULT_THEME) == "Dark"), key="theme_dark"),
                    sg.Text("(Theme applies on next launch)"),
                ],

                [sg.Button("Launch", size=(10, 1)), sg.Button("Exit", size=(10, 1))]
            ]),
            sg.VerticalSeparator(),
            sg.Column([
                [
                    sg.Text("Recent Folders:", size=(12, 1)),
                    sg.Listbox(
                        values=config.get("recent_folders", []),
                        key="recent_listbox",
                        size=(40, 15),
                        enable_events=True
                    )],
                [sg.HorizontalSeparator()],
                [

                    sg.Button("Delete Recent", size=(12, 1), key="delete_recent_button"),
                    sg.Button("Clear All Recents", size=(15, 1), key="clear_all_recents_button"),
                ],
                [sg.HorizontalSeparator()],
                [
                    sg.Text("Max Recent Folders:"),
                    sg.InputText(default_text=str(MAX_RECENTS), size=(5, 1), key="max_recents_input")
                ]
            ])
        ]
    ]
    return sg.Window("Jupyter Notebook Launcher", layout)


def main() -> None:
    # --- 1. Load config ---
    config = load_config()

    config.setdefault("theme", DEFAULT_THEME)
    config.setdefault("port", DEFAULT_PORT)
    config.setdefault("recent_folders", [])
    config.setdefault("pinned_folders", [])

    window = create_window(config)

    # --- 2. Event loop ---

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "pinned_combo":
            selected_label = values["pinned_combo"]
            pinned_item = find_pinned_by_label(config, selected_label)
            if pinned_item:
                window["folder_input"].update(pinned_item["path"])

        elif event == "recent_combo":
            recent_path = values["recent_listbox"][0]
            window["folder_input"].update(recent_path)

        elif event == "pin_unpin_button":
            folder = values["folder_input"]
            if not folder:
                sg.popup("Please select or browse a folder first.")
                continue

            pinned_item = find_pinned_by_path(config, folder)
            if pinned_item:
                unpin_folder(config, folder)
                sg.popup(f"Unpinned folder:\n{folder}")
            else:
                label = sg.popup_get_text(
                    "Enter a label for this pinned folder:",
                    default_text=os.path.basename(folder) or folder
                )
                if label:
                    pin_folder(config, folder, label)
                    sg.popup(f"Pinned folder:\n{folder}\nLabel: {label}")

            window["pinned_combo"].update(values=get_pinned_folder_labels(config))
            save_config(config)

        elif event == "rename_pinned_button":
            selected_label = values["pinned_combo"]
            if not selected_label:
                sg.popup("No pinned folder selected to rename.")
                continue

            pinned_item = find_pinned_by_label(config, selected_label)
            if not pinned_item:
                sg.popup("The selected pinned folder could not be found.")
                continue


            new_label = sg.popup_get_text(
                "Enter a new label:",
                default_text=pinned_item["label"]
            )
            if new_label and new_label.strip():
                pinned_item["label"] = new_label.strip()
                sg.popup(f"Renamed pinned folder:\n\n"
                         f"Old label: {selected_label}\n"
                         f"New label: {new_label}")
                window["pinned_combo"].update(values=get_pinned_folder_labels(config))
                window["pinned_combo"].update(value=new_label)
                save_config(config)

        elif event == "delete_recent_button":
            recent_path = values["recent_listbox"][0]
            if not recent_path:
                sg.popup("No recent folder selected to delete.")
                continue

            delete_recent_folder(config, recent_path)
            sg.popup(f"Deleted recent folder:\n{recent_path}")
            window["recent_listbox"].update(values=config["recent_folders"])
            save_config(config)


        elif event == "clear_all_recents_button":
            config["recent_folders"] = []
            sg.popup("Cleared all recent folders.")
            window["recent_listbox"].update(values=config["recent_folders"])
            save_config(config)



        elif event == "Launch":
            folder = values["folder_input"]
            port = values["port_input"]
            max_recents_input = values["max_recents_input"]

            try:
                _port_num = int(port)
            except ValueError:
                sg.popup_error("Port must be an integer.")
                continue

            try:
                max_recents = int(max_recents_input)
                if not (1 <= max_recents <= 10):
                    raise ValueError
            except ValueError:
                sg.popup_error("Max Recent Folders must be an integer between 1 and 10.")
                continue

            if folder:
                if not os.path.isdir(folder):
                    sg.popup_error(f"The folder does not exist:\n{folder}")
                    continue
                add_to_recents(folder, config)
            else:
                folder = None

            config["port"] = port

            if values["theme_light"]:
                config["theme"] = "Light"
            else:
                config["theme"] = "Dark"

            global MAX_RECENTS
            MAX_RECENTS = max_recents

            save_config(config)

            cmd = ["jupyter-notebook"]
            if folder:
                cmd.append(f"--notebook-dir={folder}")
            cmd.append(f"--port={port}")

            try:
                subprocess.Popen(cmd)
                sg.popup("Jupyter Notebook launched!\n\n(You can close this window or launch again.)")
            except FileNotFoundError:
                sg.popup_error(
                    "Could not find 'jupyter-notebook' on PATH.\n"
                    "Please ensure Jupyter is installed and on your PATH."
                )

            window["recent_listbox"].update(values=config["recent_folders"])

    window.close()


if __name__ == "__main__":
    main()
