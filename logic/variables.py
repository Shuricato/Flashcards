from dataclasses import dataclass
import datetime
import sys
import random
import os
import json
from pathlib import Path
import hashlib
from typing import Dict, List

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

@dataclass
class metaFile:
    filepath: Path
    hash: str
    filename: str
    total_questions: int
    last_updated: str
    is_selected: bool

@dataclass
class metaQuestion:
    id: str
    text: str
    source: str
    rank: int
    #Array for storing (question, value) tuples
    questions = []

class metaManager:
    def __init__(self, questions_dir: str = "./questions"):
        self.questions_dir = Path(questions_dir)
        self.available: Dict[str, metaFile] = {}
        self.loaded: Dict[str, List] = {}

    #
    def scan_files(self) -> List[metaFile]:
        """
        Looks for .md and .csv files in the questions directory, and parses them into the appropriate file objects
        """

        files = []
        try:
            for file in self.questions_dir:
                if file.endswith(".md") or file.endswith(".csv"):
                    file_meta = file.with_suffix('.meta.json')
                    file_hash = self._get_file_hash(file, file_meta)
                    metadata = self._load_or_create_meta(file, file_meta, file_hash)

                    file_obj = metaFile(
                        filepath = file,
                        hash = file_hash,
                        filename = file.name,
                        total_questions = metadata['total_questions'],
                        last_updated = metadata['last_updated']
                    )
                    files.append(file_obj)
                    self.available[file_hash] = file_obj
        except all:
            print("Error during scanning")

        return files
    
    def get_hashes(filenames):
        hashes = []
        for file in filenames:
            hashes.append(generate_file_hash(file.name))
        return hashes

    def select_files(self, filenames: List[str]):
        """
        Takes a list of filenames (ideally from main.py) and either enables them and/or loads the questions 
        """

        hashes = self.get_hashes(filenames)
        for hash in hashes:
            if hash in self.available:
                file_obj = self.available[hash]
                file_obj.is_selected = True
                
                if hash not in self.loaded:
                    self.loaded[hash] = self._parse_questions(file_obj)

    def deselect_files(self, filenames: List[str]):
        """
        Disables question files and deloads their questions
        """
        hashes = self.get_hashes(filenames)
        for hash in hashes:
            if hash in self.available:
                self.available[hash].is_selected = False

                if hash in self.loaded:
                    del self.loaded[hash]

    def update_rank(self, hash: str, question_id: str, new_rank: int):
        meta = self._get_meta(hash)
        
        if meta.exists():
            with open(meta, 'r') as f:
                metadata = json.load(f)
        #TODO: Else create file

        metadata['rankings'][question_id] = new_rank
        metadata['last_updated'] = datetime.now().isoformat

        with open(meta, 'w') as f:
            json.dump(metadata, f, indent = 2)

    def _get_file_hash(self, file:Path, meta:Path):
        if meta.exists():
            with open(file, 'r') as f:
                return json.load(f)['hash']
        hash = hashlib.md5(file.name.encode('utf-8'))
        return hash.hexdigest()[:8]
    
    def _get_meta(self, hash: str):
        file = self.available[hash]
        return file.path.with_suffix('.meta.json')

    def _load_ranks(self, meta: Path):
        with open(meta, 'r') as f:
            return json.load(f)['rankings']

    def _load_or_create_meta(self, file: Path, meta: Path, hash: str):
        if meta.exists():
            with open(meta, 'r') as f:
                return json.load(f)
        
        qcount = self._parse_question_count(file)

        #All ranks in a new file are initiated as box 4 (id 1) so their odds are not the highest
        metadata = {
            "file_hash": hash,
            "source_file": file.name,
            "last_updated": datetime.now().isoformat(),
            "total_questions": qcount,
            "rankings": {f"{i+1:03d}": 1 for i in range(qcount)}
        }

        with open(meta, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata

    def _parse_question_count(file):
        pass

    def _parse_questions(file: metaFile):
        pass
