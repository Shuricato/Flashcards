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
        
        # Section 1: Star Ranks
        section1 = self.create_section(
            "⭐ Star Ranks (Leitner System)",
            [
                "Each question starts at rank 1 (☆☆☆☆☆)",
                "Answer correctly → rank up (max 5 stars: ★★★★★)",
                "Answer incorrectly → rank down (min 1 star)",
                "Higher ranked questions appear less frequently"
            ]
        )
        content_layout.addWidget(section1)
        
        # Section 2: Question Selection
        section2 = self.create_section(
            "🎯 Smart Question Selection",
            [
                "Lower ranked questions appear more often",
                "This focuses your practice on difficult material",
                "Well-mastered questions (5 stars) appear rarely"
            ]
        )
        content_layout.addWidget(section2)
        
        # Section 3: Quiz Flow
        section3 = self.create_section(
            "📝 Quiz Flow",
            [
                "Read the question and instruction line",
                "Select your answer(s) - single or multiple choice",
                "Click 'Check Answer' to see if you're correct",
                "Green = correct answers, Red = wrong selections",
                "Watch your rank change appear beside the stars",
                "Click 'Next Question' to continue"
            ]
        )
        content_layout.addWidget(section3)
        
        # Section 4: File Formats
        section4 = self.create_section(
            "📁 Supported Formats",
            [
                "Markdown (.md) - flexible, text-based format",
                "CSV (.csv) - spreadsheet-friendly format",
                "See FORMATTING_GUIDE.txt for full details",
                "Place files in the questions/ directory"
            ]
        )
        content_layout.addWidget(section4)
        
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


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = tutorialWindow()
    window.show()
    sys.exit(app.exec())
