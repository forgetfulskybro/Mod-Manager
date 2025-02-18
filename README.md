A new version of the Mod Manager has been released. This new version uses Tkinker which is a UI toolkit for Python.
Can be found in the [Tkinker Manager folder](https://github.com/forgetfulskybro/Mod-Manager/tree/main/Tkinker%20Manager).




# Mod-Manager
Cyberpunk 2077 terminal based Mod Manager
- Main files are from [Mod Manager from Nexus Mods](https://www.nexusmods.com/cyberpunk2077/mods/10826)
- Adds functionality to the process to check for mod updates and reminder to update mods.

## Files ##
**[manager.py]**
This is the script that controls the entire process by letting you install, uninstall, check mods, and update mods.

**[start.bat]**
Double click to launch `manager.py`

**[mods.json]**
This file will be created when the script is launched. Keep this file with `manager.py`

**[reminder.json]**
This file holds all the data for when mods need to be updated. Keep this file with `manager.py`

**[updates.json]**
The file that holds all mods' IDs and versions to check for updates when the command is ran. Keep this file with `manager.py`

**[env.json]**
This file holds your Nexus Mods API key. Keep this file with `manager.py`.

## Instructions ##
**[1st step]**
Drag and drop the script wherever you want, I recommend keeping this script on the game folder or its own folder under the game path.

**[2nd step]**
When launching the script for the first time, a window will prompt asking you to select the game installation path. i.e. C:/SteamLibrary/steamapps/common/Cyberpunk 2077

**[3rd step]**
After selecting your game installation, you will be prompted to input your Nexus Mods API key. To get your api key, go to https://next.nexusmods.com/settings/api-keys and copy your personal API key.

**[4th step]**
When installing mods, multiple zips can be selected. When uninstalling mods, multiple mods can be uninstalled.

**[5th step]**
Updater can only be used when mods are currently added to Cyberpunk 2077. Make sure to run this file before removing any mods to make sure they are up to date.


## Dependencies ##
**[Requests]**
This is a python library that allows the script to check for mod updates. This library is not included in the script, so it must be installed manually. To install it, run the following command in your terminal: `pip install requests`

**[Python3+]**
In order for this small script to work, Python3 must be installed. Go to this website: http://www.python.org/download/ and download the latest version of Python 3 for your operating system.

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
