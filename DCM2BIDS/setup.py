#This will setup the environmet for the analysis pipeline
import os
import sys
from pathlib import Path
sys.path.append("..")
from shutil import copyfile

#Simulates Chmod -R
def change_permission_recursively(path, permission):
    for root, dirs, files in os.walk(path):
        for dir in dirs:
            os.chmod(os.path.join(root, dir), permission)
        for file in files:
            os.chmod(os.path.join(root, file), permission)

#Setup env
def setup_environment():
    #move the afnirc to home location
    home = str(Path.home())
    copyfile(os.path.join('/home', '.afnirc'), os.path.join(home, '.afnirc'))

    #chmod on atlases #saves time in upload. When you
    #change_permission_recursively(ConfigGLMs.Atlas_Dir, 0o777)
