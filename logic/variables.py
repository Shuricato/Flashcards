import sys
import os
import json
from pathlib import Path

_data = None
_filebank = []

def init(filename= "userdata.json"):
    #Initialising both global variables
    global _data
    global _filebank

    #All the logic of the program will execute locally to avoid clashing with the OneDrive storage
    filepath = getDirectory()/filename

    try:
        with open(filepath, 'r') as f:
            _data = json.load(f)
        print("Loading successful")
    except FileNotFoundError:
        print("File not found")
        _data = makeFile(filepath)
    except json.JSONDecodeError:
        print(f"Invalid Json")
        _data = {}

    try:
        for file in os.listdir("testfiles"):
            if file.endswith(".md") or file.endswith(".csv"):
                _filebank.append(file)
    except all:
        print("Error reading directory")

def getDirectory():
    if getattr(sys, 'frozen', False):
        localPath = Path(sys.executable).parent
    else:
        localPath = Path(__file__).parent
    return localPath

def makeFile(filepath):
    try:
        with open(filepath, 'w') as f:
            pass
    except FileExistsError:
        print("File already exists while trying to create {filepath}")

def getData():
    if _data is None:
        init()
    return _data

def getFilebank():
    if _filebank.count == 0:
        print("calling Init")
        init()
    return _filebank

def save(filename= "userdata.json"):
    filepath = getDirectory()/filename
    with open(filepath, 'w') as f:
        json.dump(_data, f, indent=2)

init()