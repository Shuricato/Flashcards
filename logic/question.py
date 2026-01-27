from pathlib import Path
from variables import metaManager
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

QUESTIONS_DIR = Path(__file__).parent / "questions"
QUESTIONS_DIR.mkdir(exist_ok = True)

manager = metaManager(str(QUESTIONS_DIR))

class questionsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flashcards")
        self.setGeometry(350, 350, 600, 400)

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        question = metaManager.get_weighted_random_question()

        #TODO: Question Display
        question_label = QTextBrowser("Placeholder question")
        question_label.setText(question.text)
        main_layout.addWidget(question_label)

        self.populate_answers(question)
        self.row_widgets = []

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(0)
        self.scroll_layout.setContentsMargins(0,0,0,0)

        self.scroll_layout.addStretch()
        self.scroll_content.setLayout(self.scroll_layout)

        scroll_area.setWidget(self.scroll_content)

        main_layout.addWidget(scroll_area)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def populate_answers(self, question):
        for row in self.row_widgets:
            self.scroll_layout.removeWidget(row)
        self.row_widgets.clear()

        for item in question.answers:
            self.create_row(item)

    def create_row(self, item):
        pass

class questionsAnswer():
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