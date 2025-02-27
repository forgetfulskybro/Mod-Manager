import os
import re
import json
import time
import zipfile
import requests
import tkinter as tk
from tkinter import filedialog

LINE_CLEAR = '\x1b[2K'
root = tk.Tk()
root.withdraw()

def listMods(p = False):
    with open('mods.json', 'r') as openfile:
        json_object = json.load(openfile)

    for x, item in enumerate(json_object):
        if item != "game":
           if (p): print(f"{x}. {item}")

    return json_object

def installMods(modsDirs):
    modNames = filedialog.askopenfilenames(title="Select mods to install.", filetypes=[('zip files', '*.zip')], initialdir="F:\\Misc\\Cyberpunk Mods")
    for fileName in modNames:
        time.sleep(2)
        name = os.path.basename(fileName).replace(".zip","")
        if json.load(open('mods.json', 'r')).get(name) != None:
            print(f"[ERR] {name} is already installed.")
            continue
        newEntry = {fileName:[]}
        
        with zipfile.ZipFile(fileName, 'r') as zip_ref:
            for item in zip_ref.namelist():
                if "." in item:
                    newEntry[fileName] = newEntry[fileName] + [item]
                    break

            if (newEntry[fileName])[0].split("/")[0] not in modsDirs and (newEntry[fileName])[0].split("/")[1] in modsDirs:
                for item in zip_ref.infolist():
                    if item.is_dir():
                        continue
                    item.filename = (item.filename).replace((newEntry[fileName])[0].split("/")[0], "")
                    zip_ref.extract(item, json.load(open('mods.json', 'r')).get("game"))

            elif (newEntry[fileName])[0].split("/")[0] in modsDirs:
                zip_ref.extractall(path=json.load(open('mods.json', 'r')).get("game"))

            else:
                print("[ERR] Bad zip hierarchy, mod not installed.")
                return 1

            newEntry = {name:[]}
            for item in zip_ref.infolist():
                if item.is_dir():
                    continue
                newEntry[name] = newEntry[name] + [item.filename]
        
        write2JsonFile(newEntry)
        print(f"[OK] {name} installed.")

def uninstallMods():
    jsonMods = listMods(True)
    lstMods = [""]
    for item in jsonMods:
        if item != "game":
            lstMods.append(item)

    print("Select a mod or mods separated by a comma, to uninstall.")
    option = input("> ")
    toUninstall = option.split(",")
    for index in toUninstall:
        if index.isdigit() and index != "0" and int(index) < len(lstMods):
            for file in jsonMods.get(lstMods[int(index)]):
                if file[0] != "/":
                    file = "/" + file
                try:
                    os.remove(json.load(open('mods.json', 'r')).get("game") + file)
                except:
                    pass
            
            pattern = re.compile(r"\((\d+)\)")
            m = pattern.findall(str(lstMods[int(index)]))
            m = "".join(m)

            removeFromJsonFile(lstMods[int(index)])
            print(lstMods[int(index)] + " files removed.")

def write2JsonFile(new_data, filename='mods.json'):
    with open(filename,'r+') as file:
        file_data = json.load(file)
        file_data[list(new_data.keys())[0]] = new_data.get(list(new_data.keys())[0])
        file.seek(0)
        json.dump(file_data, file, indent = 4)

def removeAllJsonData(filename):
    with open(filename,'r') as file:
        file_data = json.load(file)
        for x in file:
            file_data.pop(x)
            print(x)
        with open(filename,'w') as file2:
            json.dump({ }, file2, indent = 4)

def removeFromJsonFile(bye, filename='mods.json'):
    try:
        with open(filename,'r') as file:
            file_data = json.load(file)
            if bye in file_data:
                file_data.pop(bye)
                with open(filename,'w') as file2:
                    json.dump(file_data, file2, indent = 4)
            else:
                print(f"Mod '{bye}' not found in {filename}") 
    except FileNotFoundError:
        print(f"File '{filename}' not found.") 
    except json.JSONDecodeError:
        print(f"Error decoding JSON in '{filename}'.  Is it valid JSON?")

def startJsonFile():
    if not os.path.exists("mods.json"):
        game_path = filedialog.askdirectory(title="Select game installation folder.")
        toWrite = '{"game":"' + game_path + '"}'
        with open("mods.json", "w") as outfile:
            outfile.write(toWrite)
    elif json.load(open('mods.json', 'r')).get("game") == None:
        exit("Game directory not found inside mods.json")

if __name__ == '__main__':
    startJsonFile()
    # adjust root directories depending of the game
    modsDirs = ["archive", "bin", "engine", "mods", "r6", "red4ext", "tools"]
    running = True

    while running:
        if len(getReminder()) > 0:
            print(f"Reminder to update your mods! Mods needing updated:\n")
            mods = getReminder()
            for mod in mods:
                m = mods[str(mod)]
                print(f"{m["name"]}: {m["version"]}\nNew Version: {m["updated_version"]}\nLink: https://www.nexusmods.com/cyberpunk2077/mods/{str(mod)}\n")
            print("To turn off this reminder, input \"stop\"\n------------------------------------------")

        # DISPLAY MENU
        print("Installing mods under: "+ json.load(open('mods.json', 'r')).get("game"))
        print("1. List installed mods in installation order")
        print("2. Install mod(s)")
        print("3. Uninstall mod(s)")

        # PROCESS USER INPUT
        userInput = input("> ")
        match userInput:
            case "1": # list mods
                listMods(True)
            case "2": # install mods
                installMods(modsDirs)
            case "3": # uninstall mods
                uninstallMods()
        input("Press enter to continue...\n")
        os.system('cls')