import os
import sys
import subprocess

def launch_app():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_script = os.path.join(current_dir, 'manager.py')
    
    pythonw = os.path.join(sys.prefix, 'pythonw.exe')
    subprocess.Popen([pythonw, app_script])

if __name__ == '__main__':
    launch_app()