import os
import re
import json
import time
import random
import zipfile
import requests, webbrowser
import tkinter as tk
from tkinter import filedialog, Text, Scrollbar, Frame, ttk, simpledialog
import asyncio
import aiohttp
import threading

LINE_CLEAR = '\x1b[2K'
root = tk.Tk()
root.title("Cyberpunk Mod Manager")
root.geometry("900x600")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - 900) // 2
y = (screen_height - 600) // 2
root.geometry(f"900x600+{x}+{y}")

COLORS = {
    'bg_dark': '#1a1b26',
    'bg_medium': '#24283b',
    'bg_light': '#414868',
    'text': '#c0caf5',
    'accent': '#7aa2f7',
    'success': '#9ece6a',
    'error': '#f7768e',
    'warning': '#e0af68'
}

root.configure(bg=COLORS['bg_dark'])

style = ttk.Style()
style.theme_use('clam')

style.configure(
    "TButton",
    background=COLORS['bg_light'],
    foreground=COLORS['text'],
    padding=(20, 10),
    font=('Segoe UI', 10),
    borderwidth=0
)
style.map(
    "TButton",
    background=[("active", COLORS['accent'])],
    foreground=[("active", COLORS['bg_dark'])]
)

style.configure(
    "TLabel",
    background=COLORS['bg_dark'],
    foreground=COLORS['text'],
    font=('Segoe UI', 10)
)

style.configure(
    "TCheckbutton",
    background=COLORS['bg_dark'],
    foreground=COLORS['text'],
    font=('Segoe UI', 10)
)

main_container = Frame(root, bg=COLORS['bg_dark'])
main_container.pack(fill="both", expand=True, padx=20, pady=20)

log_frame_container = Frame(main_container, bg=COLORS['bg_dark'])
log_frame_container.pack(side="bottom", fill="both", expand=True)

log_title = ttk.Label(log_frame_container, text="Activity Log", style="TLabel", font=('Segoe UI', 12, 'bold'))
log_title.pack(pady=(0, 10), anchor="w")

log_frame = Frame(log_frame_container, bg=COLORS['bg_medium'], bd=1, relief="solid")
log_frame.pack(fill="both", expand=True)

log_text = Text(
    log_frame,
    height=20,
    width=80,
    wrap="char",
    bg=COLORS['bg_medium'],
    fg=COLORS['text'],
    insertbackground=COLORS['text'],
    selectbackground=COLORS['accent'],
    selectforeground=COLORS['bg_dark'],
    font=('Consolas', 10),
    padx=10,
    pady=10,
    undo=True
)
log_text.pack(side="left", fill="both", expand=True)

scrollbar = Scrollbar(log_frame, command=log_text.yview)
scrollbar.pack(side="right", fill="y")
log_text.config(yscrollcommand=scrollbar.set)

def callback(url):
    webbrowser.open_new(url)

def log(message: str, fatal: bool = False, ok: bool = False, delete: bool = False, remind: bool = False, remindColor: str = "#D8BE42", url: str = None) -> None:
    if fatal:
        log_text.insert("end", "FATAL ", "fatal")
    elif delete:
        log_text.insert("end", "DELETED ", "deleted")
    elif ok:
        log_text.insert("end", "OK ", "ok")
    elif remind:
        #if (url):
            #log_text.insert("end", "BUTTON ", "button")
        ran = f"remind-{ random.randint(1, 1000) }"
        if url:
            lbl = tk.Label(log_text, cursor="hand2", text="Open", fg="#00F484", bg="#3E4451")
            log_text.window_create('end', window=lbl, pady=3)
            lbl.bind("<Button-1>", lambda event, u=url: callback(u))
            log_text.tag_bind(ran, "<Button-1>", lambda event, u=url: callback(u))
        log_text.insert("end", f" {message}\n", ran)
        #log_text.tag_config("button", foreground="#00F484")
        log_text.tag_config(ran, foreground=remindColor)
        return
    else:
        log_text.insert("end", "INFO ", "info")
    log_text.insert("end", f"{message}\n")
    log_text.tag_config("fatal", foreground="red")
    log_text.tag_config("info", foreground="#ffa500")
    log_text.tag_config("ok", foreground="#00ff00")
    log_text.tag_config("deleted", foreground="#ff0000")
    log_text.see("end")


def ENV():
    try:
        with open('env.json', 'r') as f:
            env = json.load(f)
            return env['NEXUS_API_KEY']
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None

def listMods(p = False):
    with open('mods.json', 'r') as openfile:
        json_object = json.load(openfile)

    for x, item in enumerate(json_object):
        if item != "game" and item != "mods":
           if (p): log(f"{x-1}. {item}")

    return json_object

def write2JsonFile(new_data, filename='mods.json'):
    try:
        with open(filename, 'r') as f:
            file_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        file_data = {}

    file_data.update(new_data)

    with open(filename, 'w') as f:
        json.dump(file_data, f, indent=4)

def removeAllJsonData(filename):
    try:
        with open(filename, 'r') as file:
            file_data = json.load(file)
            file_data = {}  
            with open(filename, 'w') as file2:
                json.dump(file_data, file2, indent=4)
    except FileNotFoundError:
        log(f"File '{filename}' not found.", fatal=True)
    except json.JSONDecodeError:
        log(f"Error decoding JSON in '{filename}'.", fatal=True)

def installMods(modsDirs):
    modNames = filedialog.askopenfilenames(title="Select mods to install.", filetypes=[('zip files', '*.zip')], initialdir=json.load(open('mods.json', 'r')).get("mods"))
    if not modNames:
        return

    progress_window = tk.Toplevel(root)
    progress_window.title("Installing Mods")
    progress_window.configure(bg=COLORS['bg_dark'])

    window_width = 400
    window_height = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    progress_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    container = Frame(progress_window, bg=COLORS['bg_dark'])
    container.pack(fill="both", expand=True, padx=50, pady=30)
    container.grid_columnconfigure(0, weight=1)
    container.grid_rowconfigure(1, weight=1)

    progress_label = ttk.Label(
        container,
        text="Installing mods...",
        style="TLabel",
        font=('Segoe UI', 11)
    )
    progress_label.pack(pady=(0, 15), anchor="center")

    style.configure(
        "Installation.Horizontal.TProgressbar",
        troughcolor=COLORS['bg_medium'],
        background=COLORS['accent'],
        darkcolor=COLORS['accent'],
        lightcolor=COLORS['accent'],
        bordercolor=COLORS['bg_medium']
    )

    progress_bar = ttk.Progressbar(
        container,
        length=300,
        mode='determinate',
        style="Installation.Horizontal.TProgressbar"
    )
    progress_bar.pack(pady=(0, 15), anchor="center")

    def updateProgress(current, total, message):
        progress_bar['value'] = (current / total) * 100
        progress_label.config(text=message)
        progress_window.update()

    async def install_mod(fileName, current, total):
        try:
            name = os.path.basename(fileName).replace(".zip","")
            updateProgress(current, total, f"Installing {name}...")

            if json.load(open('mods.json', 'r')).get(name) is not None:
                log(f"{name} is already installed.", fatal=True)
                return

            newEntry = {name: []}
            with zipfile.ZipFile(fileName, 'r') as zip_ref:
                fileList = zip_ref.namelist()
                if not fileList:
                    log(f"Empty zip file: {fileName}", fatal=True)
                    return

                firstFileWithDot = next((f for f in fileList if '.' in f), None)
                if firstFileWithDot is None:
                    log(f"No files found in zip: {fileName}", fatal=True)
                    return

                topLevelDir = firstFileWithDot.split('/')[0]
                if topLevelDir not in modsDirs and len(firstFileWithDot.split('/')) > 1 and firstFileWithDot.split('/')[1] in modsDirs:
                    for item in zip_ref.infolist():
                        if item.is_dir():
                            continue
                        item.filename = item.filename.replace(topLevelDir, "")
                        zip_ref.extract(item, json.load(open('mods.json', 'r')).get("game"))
                elif topLevelDir in modsDirs:
                    zip_ref.extractall(path=json.load(open('mods.json', 'r')).get("game"))
                else:
                    log(f"Bad zip hierarchy or unsupported directory structure: {fileName}", fatal=True)
                    return

                for item in zip_ref.infolist():
                    if item.is_dir():
                        continue
                    newEntry[name].append(item.filename)

            write2JsonFile(newEntry)
            log(f"{name} installed.", ok=True)

        except FileNotFoundError:
            log(f"File '{fileName}' not found.", fatal=True)
        except zipfile.BadZipFile:
            log(f"'{fileName}' is not a valid zip file.", fatal=True)
        except Exception as e:
            log(f"An unexpected error occurred during installation: {e}", fatal=True)

    async def process_mods():
        total_mods = len(modNames)
        tasks = []
        for i, fileName in enumerate(modNames, 1):
            task = asyncio.create_task(install_mod(fileName, i, total_mods))
            tasks.append(task)
            await asyncio.sleep(0.2) 
        await asyncio.gather(*tasks)
        progress_window.destroy()

    def run_async_installation():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_mods())
        loop.close()

    threading.Thread(target=run_async_installation).start()

def uninstallMods():
    jsonMods = listMods()
    if not jsonMods:
        log("No mods installed.", fatal=False)
        return

    lstMods = [item for item in jsonMods if item != "game" and item != "mods"]

    if not lstMods:
        log("No mods installed.", fatal=False)
        return

    uninstall_window = tk.Toplevel(root)
    uninstall_window.title("Uninstall Mods")
    uninstall_window.configure(bg=COLORS['bg_dark'])

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 500) // 2
    y = (screen_height - 400) // 2
    uninstall_window.geometry(f"500x500+{x}+{y}")

    container = Frame(uninstall_window, bg=COLORS['bg_dark'])
    container.pack(fill="both", expand=True, padx=20, pady=20)

    title_label = ttk.Label(
        container,
        text="Select Mods to Uninstall",
        style="TLabel",
        font=('Segoe UI', 12, 'bold')
    )
    title_label.pack(pady=(0, 15))

    mod_frame = Frame(container, bg=COLORS['bg_medium'], bd=1, relief="solid")
    mod_frame.pack(fill="both", expand=True)

    mod_listbox = tk.Listbox(
        mod_frame,
        selectmode="multiple",
        bg=COLORS['bg_medium'],
        fg=COLORS['text'],
        selectbackground=COLORS['accent'],
        selectforeground=COLORS['bg_dark'],
        font=('Segoe UI', 10),
        width=40,
        height=15
    )
    for i, mod_name in enumerate(lstMods):
        mod_listbox.insert(i, mod_name)
    mod_listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)


    scrollbar = Scrollbar(mod_frame, orient="vertical", command=mod_listbox.yview)
    scrollbar.pack(side="right", fill="y")
    mod_listbox.config(yscrollcommand=scrollbar.set)


    def doUninstall():
        selected_indices = mod_listbox.curselection()
        if not selected_indices:
            log("No mods selected for uninstallation.", fatal=False)
            return

        for index in selected_indices:
            mod_to_remove = lstMods[index]
            for file in jsonMods.get(mod_to_remove, []):
                file_path = json.load(open('mods.json', 'r')).get("game") + (file if file.startswith("/") else "/" + file)
                try:
                    os.remove(file_path)
                    log(f"{file_path}", delete=True)
                except FileNotFoundError:
                    log(f"File not found: {file_path}", fatal=True)
                except OSError as e:
                    log(f"Error removing file {file_path}: {e}", fatal=True)

            pattern = re.compile(r"\((\d+)\)")
            mod_id = "".join(pattern.findall(str(mod_to_remove)))
            removeFromJsonFile(mod_to_remove)
            log(f"{mod_to_remove} uninstalled successfully.", ok=True)
        uninstall_window.destroy()

    uninstall_button = ttk.Button(uninstall_window, text="Uninstall Selected", command=doUninstall, style="TButton", width=20)
    uninstall_button.pack(pady=10)


    uninstall_window.transient(root)
    uninstall_window.focus_force()


def removeFromJsonFile(bye, filename='mods.json'):
    try:
        with open(filename,'r') as file:
            file_data = json.load(file)
            if bye in file_data:
                file_data.pop(bye)
                with open(filename,'w') as file2:
                    json.dump(file_data, file2, indent = 4)
            else:
                log(f"Mod '{bye}' not found in {filename}")
    except FileNotFoundError:
        log(f"File '{filename}' not found.", fatal=True)
    except json.JSONDecodeError:
        log(f"Error decoding JSON in '{filename}'.  Is it valid JSON?", fatal=True)

def startJsonFile():
    if not os.path.exists("mods.json"):
        log("Select game installation folder.")
        game_path = filedialog.askdirectory(title="Select game installation folder.")
        if not game_path:
            log("Game directory not selected. Exiting.", fatal=True)
            root.quit()
            return
        
        log("Select a folder where you store your Cyberpunk mods.")
        mods_path = filedialog.askdirectory(title="Select a folder where you store your Cyberpunk mods.")

        if mods_path is not None:
            toWrite = f'{{"game":"{game_path}", "mods":"{mods_path}"}}'
        else:
            toWrite = '{"game":"' + game_path + '"}'

        with open("mods.json", "w") as outfile:
            outfile.write(toWrite)
            log("Created mods.json to store all mod data.", ok=True)
    elif json.load(open('mods.json', 'r')).get("game") is None:
        log("Game directory not found inside mods.json", fatal=True)
        root.quit()
        return

button_frame = Frame(root, bg="#282c34")
button_frame.pack(pady=10)

button1 = ttk.Button(button_frame, text="List Installed Mods", command=lambda: listMods(True), width=20, style="TButton")
button1.grid(row=0, column=0, padx=10, pady=5)

button2 = ttk.Button(button_frame, text="Install Mod(s)", command=lambda: installMods(modsDirs), width=20, style="TButton")
button2.grid(row=0, column=1, padx=10, pady=5)

button3 = ttk.Button(button_frame, text="Uninstall Mod(s)", command=uninstallMods, width=20, style="TButton")
button3.grid(row=1, column=0, padx=10, pady=5)

if __name__ == '__main__':
    startJsonFile()
    modsDirs = ["archive", "bin", "engine", "mods", "r6", "red4ext", "tools"]
    root.mainloop()
