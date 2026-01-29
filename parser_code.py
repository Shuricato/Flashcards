# Question File Parser Code
# Add these methods to the metaManager class in variables.py

import csv
import re
from pathlib import Path
from typing import Dict, List

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


# Helper method for counting questions (used when creating metadata)
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


# ==============================================================================
# USAGE NOTES
# ==============================================================================

"""
These methods should be added to the metaManager class in your variables.py file.

Required imports at the top of the file:
    import csv
    import re
    from pathlib import Path
    from typing import Dict, List

The methods work together as follows:

1. _parse_question_count() - Called when scanning files to get total count
   - Fast operation, doesn't parse full content
   - Used to create metadata files

2. _parse_markdown() - Called when loading a .md file
   - Parses question text, answers, source
   - Detects single vs multiple choice
   - Returns list of metaQuestion objects

3. _parse_csv() - Called when loading a .csv file  
   - Parses CSV rows into questions
   - Supports both single and multiple choice
   - Returns list of metaQuestion objects

All three methods are called automatically by the existing _parse_questions() 
method in the metaManager class.

Error Handling:
- All methods print warnings for invalid/skipped questions
- Continue processing valid questions even if some fail
- Return empty list if file is completely invalid

Performance:
- _parse_question_count() is optimized for speed (regex/line counting)
- Full parsers only run when files are selected
- Results are cached in manager.loaded dictionary
"""
