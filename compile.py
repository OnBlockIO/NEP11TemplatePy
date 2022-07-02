#!/usr/bin/env python3

import os

from boa3.boa3 import Boa3

from contextlib import contextmanager
import sys, os

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

def cleanup(cleaned=False):
    if not cleaned:
        if os.path.exists(CONTRACT_PATH_NEF):
            os.remove(CONTRACT_PATH_NEF)
        if os.path.exists(CONTRACT_PATH_NEFDBG):
            os.remove(CONTRACT_PATH_NEFDBG)
        if os.path.exists(CONTRACT_PATH_JSON):
            os.remove(CONTRACT_PATH_JSON)
    else: 
        if os.path.exists(CONTRACT_PATH_PY_CLEANED):
            os.remove(CONTRACT_PATH_PY_CLEANED)

def preprocess_contract(to_remove, path, path_cleaned, base_path):
    with open(path) as oldfile, open(path_cleaned, 'w') as newfile:
        debug_block = False
        for line in oldfile:

            if any(dbg_block in line for dbg_block in list(debug_block_start)):
                print("found start")
                debug_block = True

            if any(dbg_block in line for dbg_block in list(debug_block_end)):
                print("found end")
                debug_block = False
                continue

            if debug_block:
                continue

            if not any(to_remove in line for to_remove in to_remove):
                newfile.write(line)
    os.rename(path, base_path + "/temp.py")
    os.rename(path_cleaned, path)

def build_contract(path):
    Boa3.compile_and_save(path)

GHOST_ROOT = str(os.getcwd())
to_remove = ['debug(']
debug_block_start = ['# DEBUG_START']
debug_block_end = ['# DEBUG_END']

CONTRACT_DIR = GHOST_ROOT + '/contracts/NEP11/'
CONTRACT_PATH_PY = GHOST_ROOT + '/contracts/NEP11/NEP11-Template.py'
CONTRACT_PATH_JSON = GHOST_ROOT + '/contracts/NEP11/NEP11-Template.manifest.json'
CONTRACT_PATH_NEFDBG = GHOST_ROOT + '/contracts/NEP11/NEP11-Template.nefdbgnfo'
CONTRACT_PATH_NEF = GHOST_ROOT + '/contracts/NEP11/NEP11-Template.nef'
 
CONTRACT_PATH_PY_CLEANED = GHOST_ROOT + '/contracts/NEP11/NEP11-Template_cleaned.py'
 
cleanup()
preprocess_contract(to_remove, CONTRACT_PATH_PY, CONTRACT_PATH_PY_CLEANED, CONTRACT_DIR)
with suppress_stdout():
    build_contract(CONTRACT_PATH_PY)
    os.rename(CONTRACT_DIR + "/temp.py", CONTRACT_PATH_PY)

cleanup(True)
