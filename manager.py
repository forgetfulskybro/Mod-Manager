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

def ENV():
    env = json.load(open('env.json', 'r'))
    return env['NEXUS_API_KEY']

def listMods(p = False):
    with open('mods.json', 'r') as openfile:
        json_object = json.load(openfile)

    for x, item in enumerate(json_object):
        if item != "game":
           if (p): print(x, ".", item)

    return json_object

def listVersions():
    with open('updates.json', 'r') as openfile:
        json_object = json.load(openfile)

    return json_object

def updater():
    jsonMods = listMods()
    mods = [""]
    lstMods = [""]

    for item in jsonMods:
        if item != "game":
            lstMods.append(item)

    for mod in jsonMods: 
        pattern = re.compile(r"\((\d+)\)")
        m = pattern.findall(str(mod))
        m = "".join(m)
        mods.append(m)

    mods = [x for x in mods if x]
    mods = getUpdates(mods)
    return

def getUpdates(data):
    needUpdate = []
    version = listVersions()
    for mod in data:
        print(f"Loading mod #{mod}...", end='\r')
        time.sleep(3.5)
        r = requests.get(f'https://api.nexusmods.com/v1/games/cyberpunk2077/mods/{mod}.json', headers={ "Content-Type": "application/json", "apikey": ENV() })
        r = r.json()
        print(end=LINE_CLEAR)
        print(f"{r["name"]}[{str(r["mod_id"])}]: v{str(r["version"])}")
    
        ch = version[str(r["mod_id"])]
        if ch["id"] != r["version"]:
            needUpdate.append({ "version": ch["id"], "updated_version": r["version"], "name": r["name"], "mod_id": r["mod_id"]})
            print("Update? ✅")
        else:
            print("Update? ❌")
    
    updates_count = len([update for update in needUpdate if update])
    if updates_count > 0:
        removeAllJsonData("reminder.json")
        for update in needUpdate:
            if update:
                write2JsonFile({ update["mod_id"]: { "name": update["name"], "version": update["version"], "updated_version": update["updated_version"] } }, "reminder.json")

    return print(f"Mods needing updated: {updates_count}")

def updateName(name):
    pattern = re.compile(r"\-(\d+)\-")
    m = pattern.findall(str(name))
    m = next(iter(m or []), "None")
    
    if m == "None":
        pattern = re.compile(r"\((\d+)\)")
        m = pattern.findall(str(name))
        m = next(iter(m or []), "None")

    if m == "None":
        return print(f"[ERR] Unknown mod number for '{name}'")
    
    r = requests.get(f'https://api.nexusmods.com/v1/games/cyberpunk2077/mods/{m}.json', headers={ "Content-Type": "application/json", "apikey": ENV() })
    r = r.json()
    m = name.replace(f"-{m}", f"-({m})")

    newEntry = {str(r["mod_id"]): {
        "id": str(r["version"])
    }}

    write2JsonFile(newEntry, "updates.json")
    return m

def getReminder():
    with open('reminder.json', 'r') as openfile:
        json_object = json.load(openfile)

    return json_object

def installMods(modsDirs):
    modNames = filedialog.askopenfilenames(title="Select mods to install.", filetypes=[('zip files', '*.zip')], initialdir="F:\\Misc\\Cyberpunk Mods")
    for fileName in modNames:
        time.sleep(2)
        name = updateName(os.path.basename(fileName).replace(".zip",""))
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

            removeFromJsonFile(m, "updates.json")
            removeFromJsonFile(lstMods[int(index)])
            print(lstMods[int(index)] + " files removed.")

def write2JsonFile(new_data, filename='mods.json'):
    with open(filename,'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data
        file_data[list(new_data.keys())[0]] = new_data.get(list(new_data.keys())[0])
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
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
    with open(filename,'r') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # pop bye
        file_data.pop(bye)
        with open(filename,'w') as file2:
            # convert back to json.
            json.dump(file_data, file2, indent = 4)

def startJsonFile():
    if not os.path.exists("mods.json"):
        game_path = filedialog.askdirectory(title="Select game installation folder.")
        toWrite = '{"game":"' + game_path + '"}'
        with open("mods.json", "w") as outfile:
            outfile.write(toWrite)

        with open("updates.json", "w") as outfile:
            outfile.write("{}")

        with open("reminder.json", "w") as outfile:
            outfile.write("{}")       

        with open("env.json", "w") as outfile:
            print("Enter your Nexus Mods Personal API key. Can be found here: https://next.nexusmods.com/settings/api-keys")
            userInput = input("> ")
            outfile.write('{"NEXUS_API_KEY":"' + userInput + '"}')
            os.system('cls')
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
                print(f"{m["name"]}: {m["version"]}\nNew Version: {m["updated_version"]}\n")
            print("To turn off this reminder, input \"stop\"\n------------------------------------------")

        # DISPLAY MENU
        print("Installing mods under: "+ json.load(open('mods.json', 'r')).get("game"))
        print("1. List installed mods in installation order")
        print("2. Install mod(s)")
        print("3. Uninstall mod(s)")
        print("4. Update Checker")

        # PROCESS USER INPUT
        userInput = input("> ")
        match userInput:
            case "1": # list mods
                listMods(True)
            case "2": # install mods
                installMods(modsDirs)
            case "3": # uninstall mods
                uninstallMods()
            case "4": # checks for updates
                updater()          
            case "stop":
                if len(getReminder()) > 0:
                    removeAllJsonData("reminder.json")
        input("Press enter to continue...\n")
        os.system('cls')