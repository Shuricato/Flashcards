import sys
import variables
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

# Subclass QMainWindow to customize your application's main window
class ListWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IDK what i'm doing")
        self.setGeometry(300, 300, 1000, 500)

        self.items = variables.getFilebank()

        main_widget = QWidget()
        main_layout = QVBoxLayout()

        self.label = QLabel("Select")
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
        
        self.add_btn = QPushButton("Push me!")
        self.add_btn.clicked.connect(self.add_item)
        control_layout.addWidget(self.add_btn)

        main_layout.addLayout(control_layout)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        main_layout.addWidget(self.status_label)

        self.checkAll = QPushButton("Check all")
        self.checkAll.clicked.connect(self.check_all)
        control_layout.addWidget(self.checkAll)

        self.uncheckAll = QPushButton("Uncheck all")
        self.uncheckAll.clicked.connect(self.uncheck_all)
        control_layout.addWidget(self.uncheckAll)

        self.deleteChecked = QPushButton("Delete checked")
        self.deleteChecked.clicked.connect(self.delete_checked)
        control_layout.addWidget(self.deleteChecked)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def populate_list(self):
        for item in variables.getFilebank():
            self.create_row(item)
    
    def create_row(self, text):
        row = ListItemRow(text, on_delete=self.delete_row, on_edit=self.edit_row)
        index = len(self.row_widgets)
        self.scroll_layout.insertWidget(index, row)
        self.row_widgets.append(row)
        return row
    
    def add_item(self):
        new_text = f"New Item {len(self.row_widgets) + 1}"
        self.create_row(new_text)
        self.status_label.setText(f"Added: {new_text}")
    
    def delete_row(self, row_widget):
        pass

    def edit_row(self, row_widget):
        current_text = row_widget.get_text()
        new_text, ok = QInputDialog.getText(self, "Edit item", "Enter new text:", text = current_text)

        if ok and new_text:
            row_widget.set_text(new_text)
            self.status_label.setText(f"Edited {current_text}")

    def check_all(self):
        for row in self.row_widgets:
            row.set_checked(True)
        self.status_label.setText("Checked all")

    def uncheck_all(self):
        for row in self.row_widgets:
            row.set_checked(False)
        self.status_label.setText("Unchecked all")
    
    def delete_checked(self):
        pass

    def get_checked_items(self):
        return[row.get_text() for row in self.row_widgets if row.is_checked]
    

class ListItemRow(QWidget):
    def __init__(self, text, on_delete = None, on_edit = None, parent = None):
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

        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setMaximumWidth(60)
        if on_edit:
            self.edit_btn.clicked.connect(lambda: on_edit(self))
        layout.addWidget(self.edit_btn)

        self.dlt_btn = QPushButton("Delete")
        self.dlt_btn.setMaximumWidth(60)
        if on_delete:
            self.dlt_btn.clicked.connect(lambda: on_delete(self))
        layout.addWidget(self.dlt_btn)

        self.setStyleSheet("ListItemRow { border-bottom: 1px solid #ccc; }")


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