from pathlib import Path
import sys
import subprocess
from variables import metaManager
import stats
import question
import tutorial
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

QUESTIONS_DIR = Path(__file__).parent / "questions"
QUESTIONS_DIR.mkdir(exist_ok = True)

manager = metaManager(str(QUESTIONS_DIR))

class statWindow(QMainWindow):
    def __init__(self, filenames):
        super().__init__()
        
        # Ensure files are loaded
        manager.select_files(filenames)
        
        self.display_stats()
    
    def display_stats(self):

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        for rank in range(1, 6):
            row_layout = QHBoxLayout()

            stars = "★" * rank + "☆" * (5 - rank)
            star_label = QLabel(stars)
            star_label.setStyleSheet("QLabel { font-size: 14pt; color: gold; }")
            star_label.setFixedWidth(120)
            row_layout.addWidget(star_label)
            
            ranked_questions = manager.query_questions(min_rank=rank, max_rank=rank)
            total_questions = manager.get_all_loaded_questions()

            text_label = QLabel(f"{len(ranked_questions)}/{len(total_questions)} questions,")
            row_layout.addWidget(text_label)
            
            main_layout.addLayout(row_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        


