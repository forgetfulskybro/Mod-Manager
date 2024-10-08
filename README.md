# Mod-Manager
Cyberpunk 2077 terminal based Mod Manager
- Main files are from [Mod Manager from Nexus Mods](https://www.nexusmods.com/cyberpunk2077/mods/10826)
- Adds functionality to the process to check for mod updates and reminder to update mods.

## Files ##
**[manager.py]**
This is the script that manages mods installation/uninstallation, it also creates mods.json that keeps track of which mods are
installed and all of their files.

**[start.bat]**
Double click to launch `manager.py`

**[mods.json]**
This file will be created when the script is launched. Keep this file with `manager.py`

**[reminder.json]**
This file holds all the data for when mods need to be updated. Keep this file with `manager.py`

**[updates.json]**
The file that holds all mods' IDs and versions to check for updates when the command is ran. Keep this file with `manager.py`


## Instructions ##
**[1st step]**
Drag and drop the script wherever you want, I recommend keeping this script on the game folder or its own folder under the game path.

**[2nd step]**
When launching the script for the first time, a window will prompt asking you to select the game installation path. i.e. C:/SteamLibrary/steamapps/common/Cyberpunk 2077

**[3rd step]**
After selecting your game installation, you will be prompted to input your Nexus Mods API key. To get your api key, go to https://next.nexusmods.com/settings/api-keys and copy your personal API key.

**[4th step]**
Install requests so the script can check for mod updates. Run the following command in your terminal: `pip install requests`.

**[5th step]**
When installing mods, multiple zips can be selected.

**[6th step]**
When uninstalling mods, multiple mods can be uninstalled.

**[7th step]**
Updater can only be used when mods are currently added to Cyberpunk 2077. Make sure to run this file before removing any mods to make sure they are up to date.


## Dependencies ##
**[Requests]**
This is a python library that allows the script to check for mod updates. This library is not included in the script, so it must be installed manually. To install it, run the following command in your terminal: `pip install requests`

**[Python3+]**
In order for this small script to work, Python3 must be installed.

**[.zip]**
Mods to be installed must be in a .zip and have the file structure defined i.e.

bin
  - x64
     - CrashReporter
     - d3d12on7
     - plugins
        - cyber_engine_tweaks
            - mods
                - modToInstall

**or**

modName
   - bin
    - x64
        - CrashReporter
        - d3d12on7
        - plugins
        - cyber_engine_tweaks
            - mods
                - modToInstall

Same goes for "archive", "bin", "engine", "mods", "r6", "red4ext" and "tools". 
If a mod comes in a .7z just right click, extract to folder > Then right click the folder and send to zip.
