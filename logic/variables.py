import sys
import random
import os
import json
from pathlib import Path

_data = None
_filebank = []
_active_papers = []

#Rank 1 is the lowest, Rank 5 is the highest
rank_weights = {
    1: 50,
    2: 25,
    3: 13,
    4: 7,
    5: 5
}

class Question:
    def __init__(self, text, answers, correct_answers, source, num_correct, question_id):
        self.id = question_id  # Composite ID
        self.text = text
        self.answers = answers
        self.correct_answers = correct_answers
        self.source = source
        self.num_correct = num_correct
    
    def __repr__(self):
        return f"Question(id='{self.id}', text='{self.text[:50]}...', source='{self.source}')"

def generate_file_code(file_path):
    """Generate a short unique code for the file"""
    # Option 1: Use first letters of filename
    import os
    filename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(filename)[0]

    # Create abbreviation from filename
    # e.g., "test-questions.md" -> "TQ"
    words = re.split(r'[-_\s]', name_without_ext)
    abbrev = ''.join(word[0].upper() for word in words if word)[:4]

    # Option 2: Add short hash for uniqueness
    file_hash = hashlib.md5(filename.encode()).hexdigest()[:4]

    return f"{abbrev}{file_hash}"

#TODO: parsers

def init(filename= "userdata.json"):
    #Initialising both global variables
    global _data
    global _filebank

    #All the logic of the program will execute locally to avoid clashing with the OneDrive storage
    filepath = get_directory()/filename

    try:
        with open(filepath, 'r') as f:
            _data = json.load(f)
        print("Loading successful")
    except FileNotFoundError:
        print("File not found")
        _data = make_file(filepath)
    except json.JSONDecodeError:
        print(f"Invalid Json")
        _data = {}

    try:
        for file in os.listdir("testfiles"):
            if file.endswith(".md") or file.endswith(".csv"):
                _filebank.append(file)
    except all:
        print("Error reading directory")

def update_questions(items):
     _active_papers = items

def get_questions():
     return _active_papers

def get_directory():
    if getattr(sys, 'frozen', False):
        localPath = Path(sys.executable).parent
    else:
        localPath = Path(__file__).parent
    return localPath

def make_file(filepath):
    try:
        with open(filepath, 'w') as f:
            pass
    except FileExistsError:
        print("File already exists while trying to create {filepath}")

def get_data():
    if _data is None:
        init()
    return _data

def get_filebank():
    if _filebank.count == 0:
        print("calling Init")
        init()
    return _filebank

def save(filename= "userdata.json"):
    filepath = get_directory()/filename
    with open(filepath, 'w') as f:
        json.dump(_data, f, indent=2)

#TODO: find the question doc id in the user data, return the questions in a readable format
def read_stats(item_ids):
    for item_id in item_ids:
        data = get_data()
        
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