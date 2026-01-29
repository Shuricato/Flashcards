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
        
        # Create stacked widget to hold multiple screens
        self.stacked_widget = QStackedWidget()
        
        self.menu_screen = self.create_menu_screen()
        self.stacked_widget.addWidget(self.menu_screen)
        self.refresh_list()
        
        self.setCentralWidget(self.stacked_widget)
        
        manager.scan_files()
    
    def create_menu_screen(self):
        """Creates the main menu widget"""
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()

        title = QLabel("Welcome to Flashcards!")
        title.setStyleSheet("QLabel{font-size: 32pt;}")
        top_layout.addWidget(title)
        top_layout.addStretch()

        self.tutorial_btn = QPushButton("?")
        self.tutorial_btn.setFixedSize(32, 32)
        self.tutorial_btn.setStyleSheet("QPushButton { background-color: #f0f0f0; border: none; border-radius: 16px; color: #666; font-size: 16px; font-weight: bold; } QPushButton:hover { background-color: #e0e0e0; }")
        self.tutorial_btn.setToolTip("What is this program?")
        self.tutorial_btn.clicked.connect(self.call_tutorial)
        top_layout.addWidget(self.tutorial_btn)

        main_layout.insertLayout(0, top_layout)

        self.label = QLabel("Select question files")
        self.label.setStyleSheet("QLabel{font-size: 24pt;}")
        main_layout.addWidget(self.label)
        
        self.refresh = QPushButton("Refresh list")
        self.refresh.clicked.connect(self.refresh_list)
        main_layout.addWidget(self.refresh)

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
        self.start_btn.clicked.connect(lambda: self.start())
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
        
        main_widget.setLayout(main_layout)
        return main_widget
    
    def start(self):
        checked = self.get_checked_items()
        print(checked)
        if not checked:
            self.status_label.setText("No files selected")
            return
        else: 
            manager.select_files(checked)
            
            # Remove old screen if exists
            if hasattr(self, 'question_screen'):
                self.stacked_widget.removeWidget(self.question_screen)
                self.question_screen.deleteLater()
            
            # Create fresh screen
            self.question_screen = question.questionsWindow(manager, return_callback=self.return_to_menu)
            self.stacked_widget.addWidget(self.question_screen)
            self.stacked_widget.setCurrentWidget(self.question_screen)

    def return_to_menu(self):
        self.stacked_widget.setCurrentWidget(self.menu_screen)

    def populate_list(self):
        for row in self.row_widgets:
            self.scroll_layout.removeWidget(row)
        self.row_widgets.clear()

        for item in manager.get_all_files():
            self.create_row(item.filename)

    def refresh_list(self):
        manager.scan_files()
        self.populate_list()
    
    def create_row(self, text):
        row = ListItemRow(text, on_delete=self.reset_stats, on_stat=self.call_stats)
        index = len(self.row_widgets)
        self.scroll_layout.insertWidget(index, row)
        self.row_widgets.append(row)
        return row
    
    def add_item(self):
        path = manager.questions_dir
        if sys.platform == 'win32':
            subprocess.run(['explorer', str(path)])
        elif sys.platform == 'darwin':
            subprocess.run(['open', str(path)])
        else:
            subprocess.run(['xdg-open', str(path)])

    def check_all(self):
        for row in self.row_widgets:
            row.set_checked(True)
        self.status_label.setText("Checked all")

    def uncheck_all(self):
        for row in self.row_widgets:
            row.set_checked(False)
        self.status_label.setText("Unchecked all")
    
    def reset_stats_grouped(self):
        for file in self.get_checked_items():
            manager.reset_metadata(file)

    def reset_stats(self, file):
        manager.reset_metadata(file)

    def get_checked_items(self):
        return[row.text for row in self.row_widgets if row.is_checked]
    
    def call_tutorial(self):
        self.tutorial_window = tutorial.tutorialWindow()
        self.tutorial_window.show()

    def call_stats_grouped(self):
        self.stat_window = stats.statWindow(self.get_checked_items(), manager)
        self.stat_window.show()

    def call_stats(self, file):
        self.stat_window = stats.statWindow([file], manager)
        self.stat_window.show()


#A combined widget that allows to check items, reset individual progress, and call the stat screen by ID
class ListItemRow(QWidget):
    def __init__(self, text: str, on_delete = None, on_stat = None, parent = None):
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

        self.stat_btn = QPushButton("Stats")
        self.stat_btn.setMaximumWidth(60)
        if on_stat:
            self.stat_btn.clicked.connect(lambda: on_stat(self.text))
        layout.addWidget(self.stat_btn)

        self.dlt_btn = QPushButton()
        self.dlt_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.dlt_btn.setToolTip("Reset Progress")
        self.dlt_btn.setMaximumWidth(60)
        if on_delete:
            self.dlt_btn.clicked.connect(lambda: on_delete(self.text))
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