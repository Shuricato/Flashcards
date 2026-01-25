import sys
import random
import os
import json
from pathlib import Path

_data = None
_filebank = []

#Rank 1 is the lowest, Rank 5 is the highest
rank_weights = {
    1: 50,
    2: 25,
    3: 13,
    4: 7,
    5: 5
}

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

#TODO: find the question doc id in the user data, return the questions in a readable format
def read_stats(item_ids):
    for item_id in item_ids:
        data = getData()
        
#TODO: increment/decrement item id's associated rank by 1
def up_rank(item_id):
    pass

def down_rank(item_id):
    pass

def pick_rank():
    # Calculate total weights (100%)
	total_weight = 0
	for weight in rank_weights.values():
		total_weight += weight
	
	# Pick a random value within the total weight
    # random picks between 0.0 and 1.0, making it a % of 100
	random_value = random.random() * total_weight
	
	# Use the accumulated value to determine the rank
	cumulative_weight = 0
	for rank in rank_weights.keys():
		cumulative_weight += rank_weights.get(rank)
		if random_value <= cumulative_weight:
			return rank

#TODO: fetch player data
def pick_item(rank):
    pass

init()