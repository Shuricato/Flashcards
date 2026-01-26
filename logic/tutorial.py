import sys
import variables
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

class tutorialWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("What is this program?")
        self.setGeometry(350, 350, 600, 400)

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        #TODO: Tutorial
        tutorial_label = QTextBrowser()
        tutorial_label.setPlainText("Lorem ipsum dolor sit amet.")
        main_layout.addWidget(tutorial_label)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        main_layout.addWidget(close_btn)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)