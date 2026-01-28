import sys
import json
from pathlib import Path
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

class statWindow(QMainWindow):
    def __init__(self, filenames, manager):
        super().__init__()
        self.manager = manager
        self.filenames = filenames
        
        self.setWindowTitle("Statistics")
        self.setGeometry(400, 400, 600, 400)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Question Statistics")
        title.setStyleSheet("QLabel { font-size: 24pt; font-weight: bold; }")
        main_layout.addWidget(title)
        
        # File list
        files_label = QLabel(f"Files: {', '.join(filenames)}")
        files_label.setWordWrap(True)
        files_label.setStyleSheet("QLabel { font-size: 10pt; color: #666; margin-bottom: 10px; }")
        main_layout.addWidget(files_label)
        
        # Get stats from metadata
        rank_counts = self.get_stats_from_metadata()
        total_questions = sum(rank_counts.values())
        
        # Total questions display
        total_label = QLabel(f"Total Questions: {total_questions}")
        total_label.setStyleSheet("QLabel { font-size: 14pt; margin: 10px 0; }")
        main_layout.addWidget(total_label)
        
        # Rank breakdown
        for rank in range(5, 0, -1):  # 5 to 1
            rank_layout = QHBoxLayout()
            
            # Stars
            stars = "★" * rank + "☆" * (5 - rank)
            star_label = QLabel(stars)
            star_label.setStyleSheet("QLabel { font-size: 16pt; color: gold; }")
            star_label.setFixedWidth(150)
            rank_layout.addWidget(star_label)
            
            # Count
            count = rank_counts[rank]
            percentage = (count / total_questions * 100) if total_questions > 0 else 0
            count_label = QLabel(f"{count} questions ({percentage:.1f}%)")
            count_label.setStyleSheet("QLabel { font-size: 12pt; }")
            rank_layout.addWidget(count_label)
            
            rank_layout.addStretch()
            main_layout.addLayout(rank_layout)
        
        main_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def get_stats_from_metadata(self):
        """Read rank statistics directly from .meta.json files"""
        rank_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for filename in self.filenames:
            # Find the file object in manager's available files
            for file_obj in self.manager.available.values():
                if file_obj.filename == filename:
                    # Get path to metadata file
                    meta_path = file_obj.filepath.with_suffix('.meta.json')
                    
                    if meta_path.exists():
                        try:
                            with open(meta_path, 'r') as f:
                                metadata = json.load(f)
                            
                            # Count each rank
                            for rank in metadata['rankings'].values():
                                if rank in rank_counts:
                                    rank_counts[rank] += 1
                        except Exception as e:
                            print(f"Error reading metadata for {filename}: {e}")
                    break
        
        return rank_counts