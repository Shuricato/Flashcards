import sys
import subprocess
import variables
import question
import tutorial
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

# Subclass QMainWindow to customize your application's main window
class ListWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flashcards")
        self.setGeometry(300, 300, 1000, 500)

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()

        title = QLabel("Welcome to Flashcards!")
        title.setStyleSheet("QLabel{font-size: 32pt;}")
        top_layout.addWidget(title)
        top_layout.addStretch()

        tutorial_btn = QPushButton()
        tutorial_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion))
        tutorial_btn.setToolTip("What is this program?")
        tutorial_btn.clicked.connect(self.call_tutorial)
        top_layout.addWidget(tutorial_btn)

        main_layout.insertLayout(0, top_layout)

        self.label = QLabel("Select question files")
        self.label.setStyleSheet("QLabel{font-size: 24pt;}")
        main_layout.addWidget(self.label)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(0)
        self.scroll_layout.setContentsMargins(0,0,0,0)

        self.row_widgets = []

        self.populate_list()

        self.scroll_layout.addStretch()
        self.scroll_content.setLayout(self.scroll_layout)
        scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(scroll_area)

        control_layout = QHBoxLayout()

        self.start_btn = QPushButton("Start!")
        self.start_btn.clicked.connect(lambda: self.start(self))
        control_layout.addWidget(self.start_btn)
        
        self.add_btn = QPushButton("Open Questions Folder")
        self.add_btn.clicked.connect(self.add_item)
        control_layout.addWidget(self.add_btn)

        self.stat_btn = QPushButton("Open Stats for Checked")
        self.stat_btn.clicked.connect(self.call_stats_grouped)
        control_layout.addWidget(self.stat_btn)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        main_layout.addWidget(self.status_label)

        self.checkAll = QPushButton("Check all")
        self.checkAll.clicked.connect(self.check_all)
        control_layout.addWidget(self.checkAll)

        self.uncheckAll = QPushButton("Uncheck all")
        self.uncheckAll.clicked.connect(self.uncheck_all)
        control_layout.addWidget(self.uncheckAll)

        self.deleteChecked = QPushButton("Reset checked")
        self.deleteChecked.clicked.connect(self.reset_stats_grouped)
        control_layout.addWidget(self.deleteChecked)

        main_layout.addLayout(control_layout)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def populate_list(self):
        for row in self.row_widgets:
            self.scroll_layout.removeWidget(row)
        self.row_widgets.clear()

        for item in variables.get_filebank():
            self.create_row(item)
    
    def create_row(self, text):
        row = ListItemRow(text, on_delete=self.reset_stats, on_stat=self.call_stats)
        index = len(self.row_widgets)
        self.scroll_layout.insertWidget(index, row)
        self.row_widgets.append(row)
        return row
    
    def add_item(self):
        path = variables.get_directory()
        if sys.platform == 'win32':
            subprocess.run(['explorer', str(path)])
        elif sys.platform == 'darwin':
            subprocess.run(['open', str(path)])
        else:
            subprocess.run(['xdg-open', str(path)])
        #TODO: pause the process until the files are done.

    def check_all(self):
        for row in self.row_widgets:
            row.set_checked(True)
        self.status_label.setText("Checked all")

    def uncheck_all(self):
        for row in self.row_widgets:
            row.set_checked(False)
        self.status_label.setText("Unchecked all")
    
    #TODO: call stat reset with a list of items
    def reset_stats_grouped(self):
        pass

    def reset_stats(self):
        pass

    def get_checked_items(self):
        return[row.get_text() for row in self.row_widgets if row.is_checked]
    
    def call_tutorial(self):
        self.tutorial_window = tutorial.tutorialWindow()
        self.tutorial_window.show()

    #TODO: call stat screen for a group of items and solo
    def call_stats_grouped(self):
        pass

    def call_stats(self):
        pass

    def start(self):
        questions = self.get_checked_items()
        variables.update_questions(questions)
        self.question_window = question.questionsWindow()
        self.question_window.show()

#A combined widget that allows to check items, reset individual progress, and call the stat screen by ID
class ListItemRow(QWidget):
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

        #TODO: Figure out the on_stat and on_delete(reset) logic
        self.stat_btn = QPushButton("Stats")
        self.stat_btn.setMaximumWidth(60)
        if on_stat:
            self.stat_btn.clicked.connect(lambda: on_stat(self))
        layout.addWidget(self.stat_btn)

        self.dlt_btn = QPushButton()
        self.dlt_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.dlt_btn.setToolTip("Reset Progress")
        self.dlt_btn.setMaximumWidth(60)
        if on_delete:
            self.dlt_btn.clicked.connect(lambda: on_delete(self))
        layout.addWidget(self.dlt_btn)

        self.setStyleSheet("ListItemRow { border-bottom: 1px solid #ccc; }")
        self.setLayout(layout)

    def on_checkbox_toggled(self, checked):
        print(f"'{self.text}' checkbox is now: {checked}")
    
    def is_checked(self):
        return self.checkbox.isChecked()
    
    def set_checked(self, checked):
        self.checkbox.setChecked(checked)
    
    def get_item(self):
        return self.label.text
    
    def set_text(self, text):
        self.text = text
        self.label.setText(text)

app = QApplication(sys.argv)
window = ListWindow()
window.show()
sys.exit(app.exec())