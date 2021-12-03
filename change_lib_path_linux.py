"""
    File name: move_exec.py
    Author: Jeremie Meurisse and Federico Semeraro
    Date created: 11/15/2021
    Date last modified: 12/02/2021
    Python Version: 3.9
"""

import os
from os import listdir
from os.path import isfile, join
import subprocess
import sys

### Functions
def get_files(path):
    """ Store all the file names in a list
    :param path: Path of the directory
    :return: return the list of file names
    """
    filelist = []
    for root, dirs, files in os.walk(path):
        for file in files:
            filelist.append(os.path.join(root,file)) #append the file name to the list
    return filelist

def get_folders(list):
    """ Get the folders of the executbles and libraries
    :param list: list of the executables/libraries
    :return: list of the folders
    """
    folders_list=[]
    for list_i in list:
        cmd="find $SRC_DIR -name "+list_i+" -type f | head -n 1"
        folder=subprocess.Popen([cmd],shell=True, stdout=subprocess.PIPE).communicate()[0].decode("utf-8")
        folder=os.path.dirname(os.path.dirname(folder))
        folders_list.append(folder)
    return folders_list
    
def env_var_exists(env_var):
    """ Check if the environment variable exists
    :param env_var: environment variable name
    :return: environment variable value
    """
    env_value=os.environ.get(env_var)
    if env_value is None:
        print("Error: "+env_var+" does not exist.",file=sys.stderr)
        sys.exit()
    if not os.path.exists(env_value):
        print("Error: "+env_var+"=\""+env_value+"\" not found.",file=sys.stderr)
        sys.exit()
    return env_value

### Check if the SRC_DIR environment variable exists
src_dir=env_var_exists('SRC_DIR')

### Get folders of executables and libraries
list_exec=["blockMesh","mppequil","PATOx"] # OpenFOAM, Mutation++, and PATO executables
dirs=get_folders(list_exec) # OpenFOAM, Mutation++, and PATO  prefixes
sub_dirs=["bin","lib"]
of_index=list_exec.index("blockMesh")
mpp_index=list_exec.index("mppequil")
pato_index=list_exec.index("PATOx")
of_platform_name=os.path.basename(dirs[of_index])
of_sub_dirs=next(os.walk(dirs[of_index]+"/lib"))[1]
of_sub_dirs.remove("dummy")

### Verify dirs
for i,dir_i in enumerate(dirs):
    if src_dir not in dir_i:
        print("Error: "+list_exec[i]+" not found.",file=sys.stderr)
        sys.exit()

### Change the path of the libraries
print("Running the loop...")
for i,dir_i in enumerate(dirs):
    for sub_dir_i in sub_dirs:
        my_path=dir_i+"/"+sub_dir_i
        files=get_files(my_path)
        my_path=my_path.replace(src_dir,"$SRC_DIR")
        print("Modify the rpath of the libraries in "+my_path)
        for file_i in files:
            if ".o" not in os.path.basename(file_i):
                file_i=file_i.replace(src_dir,"$SRC_DIR")
                # Change rpath
                cmd="patchelf --set-rpath \"\\$ORIGIN/../lib\" "+file_i
                os.system(cmd)
                if i == pato_index:
                    new_rpath="\\$ORIGIN/../../../../OpenFOAM/OpenFOAM-7/platforms/"+of_platform_name+"/lib:"+\
                              "\\$ORIGIN/../../src/thirdParty/mutation++/install/lib"
                    for of_sub_dir_i in of_sub_dirs:
                        new_rpath+=":\\$ORIGIN/../../../../OpenFOAM/OpenFOAM-7/platforms/"+of_platform_name+"/lib/"+of_sub_dir_i
                    cmd="patchelf --add-rpath \""+new_rpath+"\" "+file_i
                    os.system(cmd)

print("End of the change_lib_path_linux.py script.")
