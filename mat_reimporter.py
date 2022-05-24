# Created by Crt Vavros.
# Script tries to reimport all loaded MAT files from `mat_folder` directory
import bpy
from pathlib import Path
from sith.material import ColorMap, importMat
from sith.utils import getDefaultCmpFilePath, getFilePathInDir
from typing import Optional

############################################################
# Adjust vars below
mat_folder = '' # Path to directory containing .mat files
cmp_file   = '' # Path to .cmp file (JKDF2 & MOTS)
############################################################

def import_colormap(cmp_file: str) -> Optional[ColorMap]:
    try:
        return ColorMap.load(cmp_file)
    except Exception as e:
        print(f"Warning: Failed to load ColorMap '{cmp_file}': {e}")
        
if len(cmp_file) == 0:
    print('\nInfo: ColorMap path not set, loading default...')
    cmp_file = getDefaultCmpFilePath(mat_folder)
if cmp_file:
    cmp = import_colormap(cmp_file)
else:
    print("Warning: No ColorMap was found!")
        
for mat in bpy.data.materials:
    if Path(mat.name).suffix == '.mat':
        mat_path = getFilePathInDir(mat.name, mat_folder)
        if mat_path is not None:
            try:
                importMat(mat_path, cmp)
            except Exception as e:
                print("Warning: Couldn't load material: ", mat_path)
                print("  Error: {}".format(e))
        else:
            print("Warning: Couldn't find material: ", mat.name)