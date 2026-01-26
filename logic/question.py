import sys
import variables
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

class questionsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flashcards")
        self.setGeometry(350, 350, 600, 400)

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        picked_rank = variables.pick_rank()
        picked_item = variables.pick_item(picked_rank)

        #TODO: Question Display
        tutorial_label = QTextBrowser("Placeholder question")
        main_layout.addWidget(tutorial_label)

        self.populate_answers()

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def populate_answers(self):
        
        pass

class tutorialAnswer():
    def __init__(self, text, on_delete = None, on_stat = None, parent = None):
        super().__init__(parent)
        self.text = text
        layout = QHBoxLayout()
        layout.setContentsMargins(5,2,5,2)

        self.checkbox = QCheckBox()
        self.checkbox.toggled.connect(self.on_checkbox_toggled)
        layout.addWidget(self.checkbox)

        layout.addStretch()

        self.label = QLabel(text)
        self.label.setMinimumWidth(200)
        layout.addWidget(self.label)