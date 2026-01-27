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

class ListWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Flashcards")
        self.setGeometry(300, 300, 1000, 500)

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        rank_1 = QHBoxLayout()
        
        #TODO: see if the ranks can be looped


