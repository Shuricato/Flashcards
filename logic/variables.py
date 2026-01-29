from dataclasses import dataclass, field
import datetime
import csv
import random
import re
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
    hash: str
    question_number: int
    text: str
    source: str
    rank: int
    answers: List[Dict] = field(default_factory=list) 
    question_type: str = "single_choice"

class metaManager:
    def __init__(self, questions_dir: str = "./questions"):
        self.questions_dir = Path(questions_dir)
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
        Enables question files and loads their questions
        """
        for file_obj in self.available.values():
            file_obj.is_selected = False

        self.loaded.clear()

        # Load only selected files
        hashes = self.get_hashes(filenames)
        for hash_val in hashes:
            if hash_val in self.available:
                file_obj = self.available[hash_val]
                file_obj.is_selected = True
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

    def reset_metadata(self, filename: str):
        """Reset the .meta.json file"""

        file_hash = None
        for hash_val, file_obj in self.available.items():
            if file_obj.filename == filename:
                file_hash = hash_val
        
        if file_hash not in self.available:
            raise ValueError(f"File with hash {file_hash} not found")
        
        file_obj = self.available[file_hash]
        meta_path = self._get_meta(file_hash)
        
        metadata = {
            "file_hash": file_hash,
            "source_file": file_obj.filename,
            "last_updated": datetime.datetime.now().isoformat(),
            "total_questions": file_obj.total_questions,
            "rankings": {f"{i+1:03d}": 2 for i in range(file_obj.total_questions)}
        }
        
        # Write the reset metadata
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Reset metadata for {file_obj.filename}")
        
        # Also update in-memory questions if loaded
        if file_hash in self.loaded:
            for question in self.loaded[file_hash]:
                question.rank = 2

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
        """
        Parse markdown with format:
        | ------- |
        Question text
        | | Optional instruction line
        | ------- |
        | | Answer | True/False |
        | | Answer | True/False |
        Source: Author
        
        Args:
            file_path: Path to the .md file
            file_hash: Hash identifier for the file
            rankings: Dictionary mapping question IDs to rank values (1-5)
        
        Returns:
            List of metaQuestion objects
        """
        questions = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by separator to get question blocks
        # Each block alternates: Question text | ------- | Answers
        blocks = re.split(r'\|\s*-+\s*\|', content)
        
        question_num = 1
        i = 1  # Skip first block (header/README)
        
        while i < len(blocks):
            # blocks[i] = question text area
            # blocks[i+1] = answers area
            
            if i + 1 >= len(blocks):
                break
            
            question_block = blocks[i].strip()
            answer_block = blocks[i + 1].strip()
            
            if not question_block or not answer_block:
                i += 2
                continue
            
            # Parse question text (first non-empty, non-instruction line)
            question_text = None
            question_type = "single_choice"
            
            for line in question_block.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Skip instruction lines but check for multiple choice indicator
                if any(phrase in line.lower() for phrase in [
                    'please choose',
                    'there are',
                    'correct answers to this question'
                ]):
                    # Detect multiple choice
                    if 'correct answers' in line.lower() or \
                    any(f'{num} correct' in line.lower() for num in ['2', '3', '4', '5']):
                        question_type = "multiple_choice"
                    continue
                
                # First real line is the question
                if not question_text:
                    question_text = line
            
            # Parse answers and source
            answers = []
            source = ""
            
            for line in answer_block.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                # Answer line: | | Text | True/False |
                if line.startswith('| |'):
                    # Remove leading '| |'
                    remainder = line[3:].strip()
                    # Split by remaining pipes
                    parts = [p.strip() for p in remainder.split('|')]
                    
                    if len(parts) >= 2:
                        answer_text = parts[0]
                        is_correct = parts[1].lower() == 'true'
                        
                        answers.append({
                            'text': answer_text,
                            'is_correct': is_correct
                        })
                
                # Source line
                elif line.startswith('Source:'):
                    source = line.replace('Source:', '').strip()
            
            # Create question if valid
            if question_text and answers:
                question_id_key = f"{question_num:03d}"
                rank = rankings.get(question_id_key, 2)
                
                question_obj = metaQuestion(
                    id=f"{file_hash}-{question_num:03d}",
                    hash=file_hash,
                    question_number=question_num,
                    text=question_text,
                    source=source,
                    rank=rank,
                    answers=answers,
                    question_type=question_type
                )
                
                questions.append(question_obj)
                question_num += 1
            else:
                print(f"Warning: Skipped invalid question block (no text or answers)")
            
            # Move to next question block (skip 2 blocks - we just processed them)
            i += 2
        
        return questions


    def _parse_csv(self, file_path: Path, file_hash: str, 
                rankings: Dict[str, int]) -> List[metaQuestion]:
        """
        Parse CSV file with format:
        question,answer1,answer2,answer3,answer4,correct,source
        
        Args:
            file_path: Path to the .csv file
            file_hash: Hash identifier for the file
            rankings: Dictionary mapping question IDs to rank values (1-5)
        
        Returns:
            List of metaQuestion objects
        """
        questions = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            question_num = 1
            
            for row in reader:
                # Skip empty rows
                if not row.get('question', '').strip():
                    continue
                
                answers = []
                
                # Parse correct answer(s)
                correct_str = row.get('correct', '').strip()
                
                if not correct_str:
                    print(f"Warning: Question {question_num} has no correct answer specified")
                    continue
                
                # Determine if multiple choice
                if ',' in correct_str:
                    # Multiple correct answers: "1,3,4"
                    try:
                        correct_nums = [int(x.strip()) for x in correct_str.split(',')]
                        question_type = "multiple_choice"
                    except ValueError:
                        print(f"Warning: Invalid correct format in question {question_num}: {correct_str}")
                        continue
                else:
                    # Single correct answer: "2"
                    try:
                        correct_nums = [int(correct_str)]
                        question_type = "single_choice"
                    except ValueError:
                        print(f"Warning: Invalid correct format in question {question_num}: {correct_str}")
                        continue
                
                # Build answer list from answer1-answer4 columns
                for i in range(1, 5):
                    answer_key = f'answer{i}'
                    answer_text = row.get(answer_key, '').strip()
                    
                    if answer_text:  # Only add non-empty answers
                        answers.append({
                            'text': answer_text,
                            'is_correct': i in correct_nums
                        })
                
                # Validate we have at least 2 answers
                if len(answers) < 2:
                    print(f"Warning: Question {question_num} has fewer than 2 answers")
                    continue
                
                # Get ranking
                question_id_key = f"{question_num:03d}"
                rank = rankings.get(question_id_key, 2)
                
                # Create question object
                question_obj = metaQuestion(
                    id=f"{file_hash}-{question_num:03d}",
                    file_hash=file_hash,
                    question_number=question_num,
                    text=row.get('question', ''),
                    source=row.get('source', ''),
                    rank=rank,
                    answers=answers,
                    question_type=question_type
                )
                
                questions.append(question_obj)
                question_num += 1
        
        return questions

    def _parse_question_count(self, file: Path) -> int:
        """
        Count questions in file without full parsing.
        
        Args:
            file: Path to the question file
        
        Returns:
            Number of questions in the file
        """
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if file.suffix == '.md':
            # Count separators and divide by 2 (each question has 2 separators)
            import re
            separators = re.findall(r'\|\s*-+\s*\|', content)
            # Subtract 1 for potential header, then divide by 2
            count = max(0, (len(separators) - 1) // 2)
            return count
        
        elif file.suffix == '.csv':
            # Count non-header, non-empty lines
            lines = [line.strip() for line in content.strip().split('\n') if line.strip()]
            # Subtract 1 for header row
            return max(0, len(lines) - 1)
        
        return 0
    
    def quick_rank_up(self, question: metaQuestion):
        """Increase rank by 1"""
        new_rank = min(5, question.rank +1)
        self.update_rank(question.hash, question.question_number, new_rank)
    
    def quick_rank_down(self, question: metaQuestion):
        """Decrease rank by 1"""
        new_rank = max(1, question.rank -1)
        self.update_rank(question.hash, question.question_number, new_rank)

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
