"""
Qt Tutorial Window Markup
Brief explanation of the Leitner-based quiz system
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class tutorialWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("How It Works")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("How the Quiz Works")
        title.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #1a1a1a; margin-bottom: 10px;"
        )
        layout.addWidget(title)
        
        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setSpacing(15)

        
        # Section 1: Quiz Flow
        section1 = self.create_section(
            "Quiz Flow",
            [
                "Read the question and instruction line",
                "Select your answer(s) - single or multiple choice",
                "Click 'Check Answer' to see if you're correct",
                "Green = correct answers, Red = wrong selections",
                "Watch your rank change appear beside the stars",
                "Click 'Next Question' to continue"
            ]
        )
        content_layout.addWidget(section1)
        
        # Section 2: Star Ranks
        section2 = self.create_section(
            "⭐ Star Ranks (Leitner System)",
            [
                "Each question can rank between 1(★☆☆☆☆) and 5(★★★★★) stars"
                "Each question starts at rank 2",
                "Answer correctly → rank up (max 5 stars)",
                "Answer incorrectly → rank down (min 1 star)",
                "Higher ranked questions appear less frequently"
            ]
        )
        content_layout.addWidget(section2)
        
        # Section 3: Star Rarity
        section3 = self.create_section(
            "Rank Selection Probability",
            [
                "★☆☆☆☆ (1 star) - 50% chance to appear",
                "★★☆☆☆ (2 stars) - 25% chance to appear",
                "★★★☆☆ (3 stars) - 13% chance to appear",
                "★★★★☆ (4 stars) - 7% chance to appear",
                "★★★★★ (5 stars) - 5% chance to appear"
            ]
        )
        content_layout.addWidget(section3)
        
        
        # Section 4: Markdown Format
        section4 = self.create_section_with_code(
            "Markdown Question Format (.md)",
            [
                "Questions use pipe separators and True/False flags:"
            ],
            """| ------- |
Question text goes here
| ------- |
| | Answer 1 | True |
| | Answer 2 | False |
| | Answer 3 | False |
Source: Your Source"""
        )
        content_layout.addWidget(section4)
        
        # Section 5: CSV Format
        section5 = self.create_section_with_code(
            "CSV Question Format (.csv)",
            [
                "Spreadsheet format with columns:"
            ],
            """question,answer1,answer2,answer3,answer4,correct,source
What is 2+2?,3,4,5,6,2,Math
Which are prime?,2,3,4,5,"1,2",Numbers"""
        )
        content_layout.addWidget(section5)
        
        content_widget.setLayout(content_layout)
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton("Got it!")
        close_btn.setMinimumHeight(44)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: #fafafa;")
    
    def create_section(self, title, points):
        """Create a section with title and bullet points"""
        section = QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        section_layout = QVBoxLayout()
        section_layout.setSpacing(10)
        
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 5px;"
        )
        section_layout.addWidget(title_label)
        
        # Bullet points
        for point in points:
            point_label = QLabel(f"• {point}")
            point_label.setWordWrap(True)
            point_label.setStyleSheet(
                "font-size: 14px; color: #374151; padding-left: 10px; line-height: 1.5;"
            )
            section_layout.addWidget(point_label)
        
        section.setLayout(section_layout)
        return section
    
    def create_section_with_code(self, title, points, code):
        """Create a section with title, bullet points, and code example"""
        section = QWidget()
        section.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        section_layout = QVBoxLayout()
        section_layout.setSpacing(10)
        
        # Section title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: #1a1a1a; margin-bottom: 5px;"
        )
        section_layout.addWidget(title_label)
        
        # Bullet points
        for point in points:
            point_label = QLabel(f"• {point}")
            point_label.setWordWrap(True)
            point_label.setStyleSheet(
                "font-size: 14px; color: #374151; padding-left: 10px; line-height: 1.5;"
            )
            section_layout.addWidget(point_label)
        
        # Code example
        code_label = QLabel(code)
        code_label.setWordWrap(True)
        code_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        code_label.setStyleSheet("""
            QLabel {
                background-color: #f3f4f6;
                color: #1f2937;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #e5e7eb;
                margin-top: 8px;
            }
        """)
        section_layout.addWidget(code_label)
        
        section.setLayout(section_layout)
        return section


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = tutorialWindow()
    window.show()
    sys.exit(app.exec())
