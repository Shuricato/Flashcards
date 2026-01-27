from dataclasses import dataclass, field
import datetime
import sys
import random
import os
import json
from pathlib import Path
import hashlib
from typing import Dict, List, Optional, Tuple

# Rank 1 is the lowest, Rank 5 is the highest
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
    is_selected: bool = False

@dataclass
class metaQuestion:
    id: str
    text: str
    source: str
    rank: int
    answers: List[Dict] = field(default_factory=list) 
    question_type: str = "single_choice"

class metaManager:
    def __init__(self, questions_dir: str = "./questions"):
        self.questions_dir = Path(questions_dir)
        print(self.questions_dir)
        self.available: Dict[str, metaFile] = {}
        self.loaded: Dict[str, List[metaQuestion]] = {}

    def scan_files(self) -> List[metaFile]:
        """
        Looks for .md and .csv files in the questions directory, and parses them into the appropriate file objects
        """
        files = []
        
        try:
            for file in self.questions_dir.glob("*"):
                if file.suffix in [".md", ".csv"]:
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
        except Exception as e:
            print(f"Error during scanning: {e}")

        return files
    
    def get_hashes(self, filenames: List[str]) -> List[str]:
        hashes = []
        for filename in filenames:
            for hash_val, file_obj in self.available.items():
                if file_obj.filename == filename:
                    hashes.append(hash_val)
                    break
        return hashes

    def select_files(self, filenames: List[str]):
        """
        Takes a list of filenames (ideally from main.py) and either enables them and/or loads the questions 
        """
        hashes = self.get_hashes(filenames)
        for hash_val in hashes:
            if hash_val in self.available:
                file_obj = self.available[hash_val]
                file_obj.is_selected = True
                
                if hash_val not in self.loaded:
                    self.loaded[hash_val] = self._parse_questions(file_obj)

    def deselect_files(self, filenames: List[str]):
        """
        Disables question files and deloads their questions
        """
        hashes = self.get_hashes(filenames)
        for hash_val in hashes:
            if hash_val in self.available:
                self.available[hash_val].is_selected = False

                if hash_val in self.loaded:
                    del self.loaded[hash_val]

    def update_rank(self, file_hash: str, question_number: int, new_rank: int):
        """Update ranking for a specific question"""
        meta_path = self._get_meta(file_hash)
        
        if meta_path.exists():
            with open(meta_path, 'r') as f:
                metadata = json.load(f)
        else:
            file_obj = self.available[file_hash]
            metadata = self._load_or_create_meta(
                file_obj.filepath, 
                meta_path, 
                file_hash
            )

        question_id = f"{question_number:03d}"
        metadata['rankings'][question_id] = new_rank
        metadata['last_updated'] = datetime.datetime.now().isoformat()

        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        if file_hash in self.loaded:
            for question in self.loaded[file_hash]:
                if question.question_number == question_number:
                    question.rank = new_rank
                    break

    def get_question_by_id(self, question_id: str) -> Optional[metaQuestion]:
        """Retrieve a specific question by its full ID"""
        parts = question_id.split('-')
        if len(parts) != 2:
            return None
        
        file_hash = parts[0]
        question_num = int(parts[1])
        
        if file_hash in self.loaded:
            for question in self.loaded[file_hash]:
                if question.question_number == question_num:
                    return question
        
        return None

    def get_all_loaded_questions(self) -> List[metaQuestion]:
        """Get all questions from all loaded files"""
        all_questions = []
        for questions_list in self.loaded.values():
            all_questions.extend(questions_list)
        return all_questions

    def query_questions(self, 
                       min_rank: Optional[int] = None,
                       max_rank: Optional[int] = None,
                       file_hashes: Optional[List[str]] = None,
                       sources: Optional[List[str]] = None) -> List[metaQuestion]:
        """Query loaded questions with filters"""
        results = []
        
        # Determine which files to search
        target_hashes = file_hashes if file_hashes else list(self.loaded.keys())
        
        for hash_val in target_hashes:
            if hash_val not in self.loaded:
                continue
            
            for question in self.loaded[hash_val]:
                # Apply filters
                if min_rank and question.rank < min_rank:
                    continue
                if max_rank and question.rank > max_rank:
                    continue
                if sources and question.source not in sources:
                    continue
                
                results.append(question)
        
        return results

    def get_weighted_random_question(self) -> Optional[metaQuestion]:
        """
        Get a random question weighted by rank.
        Lower ranks (1) appear more often than higher ranks (5)
        """
        all_questions = self.get_all_loaded_questions()
        if not all_questions:
            return None
        
        # Create weighted list
        weighted_questions = []
        for question in all_questions:
            weight = rank_weights.get(question.rank, 1)
            weighted_questions.extend([question] * weight)
        
        return random.choice(weighted_questions)

    def _get_file_hash(self, file: Path, meta: Path) -> str:
        """Generate or retrieve file hash"""
        if meta.exists():
            with open(meta, 'r') as f:
                return json.load(f)['file_hash']
        
        hash_obj = hashlib.md5(file.name.encode('utf-8'))
        return hash_obj.hexdigest()[:8]
    
    def _get_meta(self, file_hash: str) -> Path:
        """Get metadata file path from hash"""
        file_obj = self.available[file_hash]
        return file_obj.filepath.with_suffix('.meta.json')

    def _load_ranks(self, meta: Path) -> Dict[str, int]:
        """Load rankings from metadata file"""
        with open(meta, 'r') as f:
            return json.load(f)['rankings']

    def _load_or_create_meta(self, file: Path, meta: Path, file_hash: str) -> Dict:
        """Load existing metadata or create new"""
        if meta.exists():
            with open(meta, 'r') as f:
                return json.load(f)
        
        qcount = self._parse_question_count(file)

        metadata = {
            "file_hash": file_hash,
            "source_file": file.name,
            "last_updated": datetime.datetime.now().isoformat(),
            "total_questions": qcount,
            "rankings": {f"{i+1:03d}": 2 for i in range(qcount)}
        }

        with open(meta, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return metadata

    def _parse_question_count(self, file: Path) -> int:
        """Count questions in file without full parsing"""
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if file.suffix == '.md':
            separator_count = content.count('| ------- |')
            return max(0, separator_count - 1)
        elif file.suffix == '.csv':
            lines = content.strip().split('\n')
            return max(0, len(lines) - 1)
        
        return 0

    def _parse_questions(self, file_obj: metaFile) -> List[metaQuestion]:
        """
        Parse file into metaQuestion objects. Returns a list of metaQuestion instances.
        """
        questions = []
        file_path = file_obj.filepath
        
        meta_path = file_path.with_suffix('.meta.json')
        rankings = self._load_ranks(meta_path)
        
        if file_path.suffix == '.md':
            questions = self._parse_markdown(file_path, file_obj.hash, rankings)
        elif file_path.suffix == '.csv':
            questions = self._parse_csv(file_path, file_obj.hash, rankings)
        
        return questions

    def _parse_markdown(self, file_path: Path, file_hash: str, 
                       rankings: Dict[str, int]) -> List[metaQuestion]:
        """Parse markdown file format into metaQuestion objects"""
        questions = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = content.split('| ------- |')
        
        question_num = 1
        for section in sections[1:]: 
            lines = [line.strip() for line in section.strip().split('\n') if line.strip()]
            
            if not lines:
                continue
            
            question_text = lines[0]
            
            answers = []
            source = ""
            question_type = "single_choice"
            
            for line in lines[1:]:
                if line.startswith('Source:'):
                    source = line.replace('Source:', '').strip()
                elif line.startswith('| |'):
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 2:
                        answer_text = parts[1]
                        is_correct = len(parts) > 2 and parts[2].lower() == 'true'
                        answers.append({
                            'text': answer_text,
                            'is_correct': is_correct
                        })
                elif 'correct answers' in line.lower() or '3 correct' in line.lower():
                    question_type = "multiple_choice"
            
            question_id_key = f"{question_num:03d}"
            rank = rankings.get(question_id_key, 1)
            
            question_obj = metaQuestion(
                id=f"{file_hash}-{question_num:03d}",
                file_hash=file_hash,
                question_number=question_num,
                text=question_text,
                source=source,
                rank=rank,
                answers=answers,
                question_type=question_type
            )
            
            questions.append(question_obj)
            question_num += 1
        
        return questions

    def _parse_csv(self, file_path: Path, file_hash: str, 
                   rankings: Dict[str, int]) -> List[metaQuestion]:
        """Parse CSV file format into metaQuestion objects"""
        import csv
        questions = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            question_num = 1
            
            for row in reader:
                # Assuming CSV columns: question, answer1, answer2, answer3, answer4, correct, source
                answers = []
                for i in range(1, 5):
                    answer_key = f'answer{i}'
                    if answer_key in row and row[answer_key]:
                        answers.append({
                            'text': row[answer_key],
                            'is_correct': row.get('correct', '') == str(i)
                        })
                
                question_id_key = f"{question_num:03d}"
                rank = rankings.get(question_id_key, 1)
                
                question_obj = metaQuestion(
                    id=f"{file_hash}-{question_num:03d}",
                    file_hash=file_hash,
                    question_number=question_num,
                    text=row.get('question', ''),
                    source=row.get('source', ''),
                    rank=rank,
                    answers=answers,
                    question_type='single_choice'
                )
                
                questions.append(question_obj)
                question_num += 1
        
        return questions
    
    def quick_rank_up(self, question: metaQuestion):
        """Increase rank by 1"""
        new_rank = min(5, question.rank +1)
        self.update_rank(question.file_hash, question.question_number, new_rank)
    
    def quick_rank_down(self, question: metaQuestion):
        """Decrease rank by 1"""
        new_rank = max(1, question.rank -1)
        self.update_rank(question.file_hash, question.question_number, new_rank)

    def get_all_files(self):
        return [file_obj for file_obj in self.available.values()]

    def delete_metadata(self, filename: str):
        file_hash = None
        for hash_val, file_obj in self.available.items():
            if file_obj.filename == filename:
                file_hash = hash_val
            
        if not file_hash:
            raise ValueError(f"File {filename} not found")
        
        meta_path = self._get_meta(file_hash)

        if meta_path.exists():
            meta_path.unlink()
        
        if file_hash in self.loaded:
            del self.loaded[file_hash]
