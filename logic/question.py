import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

class questionsWindow(QWidget):
    def __init__(self, manager, return_callback=None):
        super().__init__()
        self.manager = manager
        self.return_callback = return_callback
        self.current_question = None
        self.selected_answers = []
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        
        # === TOP BAR ===
        top_bar = QHBoxLayout()
        
        self.back_btn = QPushButton("← Back to Menu")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #666;
                font-size: 13px;
                padding: 8px 12px;
                text-align: left;
            }
            QPushButton:hover {
                color: #000;
                background-color: #f5f5f5;
                border-radius: 6px;
            }
        """)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.return_to_menu)
        top_bar.addWidget(self.back_btn)
        
        top_bar.addStretch()
        
        self.tutorial_btn = QPushButton("?")
        self.tutorial_btn.setFixedSize(32, 32)
        self.tutorial_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: none;
                border-radius: 16px;
                color: #666;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.tutorial_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tutorial_btn.clicked.connect(self.call_tutorial)
        top_bar.addWidget(self.tutorial_btn)
        
        main_layout.addLayout(top_bar)
        
        # === RANK INDICATOR ===
        rank_container = QHBoxLayout()
        rank_container.addStretch()
        
        self.rank_display = QLabel()
        self.rank_display.setStyleSheet("""
            QLabel {
                color: #FFB800;
                font-size: 20px;
                letter-spacing: 2px;
            }
        """)
        rank_container.addWidget(self.rank_display)
        
        rank_container.addStretch()
        main_layout.addLayout(rank_container)
        
        # === QUESTION CARD ===
        question_card = QWidget()
        question_card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        question_layout = QVBoxLayout()
        question_layout.setContentsMargins(30, 30, 30, 30)
        question_layout.setSpacing(15)
        
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 500;
                line-height: 1.5;
                color: #1a1a1a;
            }
        """)
        question_layout.addWidget(self.question_label)
        
        # Instruction text
        self.instruction_label = QLabel()
        self.instruction_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #888;
                margin-top: 8px;
            }
        """)
        question_layout.addWidget(self.instruction_label)
        
        question_card.setLayout(question_layout)
        main_layout.addWidget(question_card)
        
        # === ANSWERS AREA ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.answers_widget = QWidget()
        self.answers_widget.setStyleSheet("background: transparent;")
        self.answers_layout = QVBoxLayout()
        self.answers_layout.setSpacing(12)
        self.answers_layout.setContentsMargins(0, 0, 0, 0)
        
        self.answer_widgets = []
        
        self.answers_widget.setLayout(self.answers_layout)
        scroll_area.setWidget(self.answers_widget)
        main_layout.addWidget(scroll_area)
        
        # === FEEDBACK AREA ===
        self.feedback_container = QWidget()
        self.feedback_container.setVisible(False)
        feedback_layout = QVBoxLayout()
        feedback_layout.setContentsMargins(20, 15, 20, 15)
        
        self.feedback_label = QLabel()
        self.feedback_label.setWordWrap(True)
        self.feedback_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 500;
            }
        """)
        feedback_layout.addWidget(self.feedback_label)
        
        self.source_label = QLabel()
        self.source_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
                margin-top: 5px;
                font-style: italic;
            }
        """)
        feedback_layout.addWidget(self.source_label)
        
        self.feedback_container.setLayout(feedback_layout)
        main_layout.addWidget(self.feedback_container)
        
        # === ACTION BUTTONS ===
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.check_btn = QPushButton("Check Answer")
        self.check_btn.setMinimumHeight(48)
        self.check_btn.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_btn.clicked.connect(self.check_answer)
        button_layout.addWidget(self.check_btn)
        
        self.next_btn = QPushButton("Next Question →")
        self.next_btn.setMinimumHeight(48)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: 600;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.next_btn.clicked.connect(self.load_next_question)
        self.next_btn.setVisible(False)
        button_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(button_layout)
        
        # === NOTIFICATION ===
        self.notification = QLabel(self)
        self.notification.setStyleSheet("""
            QLabel {
                background-color: rgba(26, 26, 26, 0.95);
                color: white;
                font-size: 15px;
                font-weight: 600;
                padding: 16px 24px;
                border-radius: 10px;
            }
        """)
        self.notification.setVisible(False)
        self.notification.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(lambda: self.notification.setVisible(False))
        
        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #fafafa;")
        
        # Load first question
        self.load_next_question()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.notification.isVisible():
            self.position_notification()
    
    def position_notification(self):
        notif_width = 220
        notif_height = 70
        x = self.width() - notif_width - 30
        y = 30
        self.notification.setGeometry(x, y, notif_width, notif_height)
    
    def show_notification(self, message, duration=2500):
        self.notification.setText(message)
        self.notification.setVisible(True)
        self.position_notification()
        self.notification_timer.start(duration)
    
    def load_next_question(self):
        self.current_question = self.manager.get_weighted_random_question()
        
        if not self.current_question:
            QMessageBox.warning(self, "No Questions", "No questions available. Please select files from the main menu.")
            self.return_to_menu()
            return
        
        # Reset state
        self.selected_answers = []
        self.feedback_container.setVisible(False)
        self.check_btn.setVisible(True)
        self.next_btn.setVisible(False)
        
        # Display question
        self.question_label.setText(self.current_question.text)
        
        # Update rank display
        stars = "★" * self.current_question.rank + "☆" * (5 - self.current_question.rank)
        self.rank_display.setText(stars)
        
        # Update instruction
        if self.current_question.question_type == "multiple_choice":
            self.instruction_label.setText("Select all correct answers")
        else:
            self.instruction_label.setText("Select one answer")
        
        # Clear previous answers
        for widget in self.answer_widgets:
            self.answers_layout.removeWidget(widget)
            widget.deleteLater()
        self.answer_widgets.clear()
        
        # Create answer options
        for i, answer in enumerate(self.current_question.answers):
            answer_container = QWidget()
            answer_container.setStyleSheet("""
                QWidget {
                    background-color: white;
                    border: 2px solid #e5e7eb;
                    border-radius: 10px;
                    padding: 4px;
                }
                QWidget:hover {
                    border-color: #2563eb;
                    background-color: #f8faff;
                }
            """)
            
            answer_layout = QHBoxLayout()
            answer_layout.setContentsMargins(16, 12, 16, 12)
            
            if self.current_question.question_type == "multiple_choice":
                selector = QCheckBox()
                selector.toggled.connect(lambda checked, idx=i: self.on_answer_toggled(idx, checked))
            else:
                selector = QRadioButton()
                selector.toggled.connect(lambda checked, idx=i: self.on_answer_selected(idx, checked))
            
            selector.setStyleSheet("""
                QCheckBox, QRadioButton {
                    font-size: 15px;
                    spacing: 12px;
                }
                QCheckBox::indicator, QRadioButton::indicator {
                    width: 20px;
                    height: 20px;
                }
            """)
            
            answer_text = QLabel(answer['text'])
            answer_text.setWordWrap(True)
            answer_text.setStyleSheet("""
                QLabel {
                    font-size: 15px;
                    color: #374151;
                    padding: 4px;
                }
            """)
            
            selector.setText("")
            answer_layout.addWidget(selector)
            answer_layout.addWidget(answer_text, 1)
            
            answer_container.setLayout(answer_layout)
            answer_container.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Store both container and selector
            answer_container.selector = selector
            answer_container.answer_text = answer_text
            
            # Make container clickable
            answer_container.mousePressEvent = lambda event, s=selector: s.setChecked(not s.isChecked())
            
            self.answers_layout.addWidget(answer_container)
            self.answer_widgets.append(answer_container)
        
        self.answers_layout.addStretch()
    
    def on_answer_selected(self, index, checked):
        if checked:
            self.selected_answers = [index]
    
    def on_answer_toggled(self, index, checked):
        if checked:
            if index not in self.selected_answers:
                self.selected_answers.append(index)
        else:
            if index in self.selected_answers:
                self.selected_answers.remove(index)
    
    def check_answer(self):
        if not self.selected_answers:
            QMessageBox.warning(self, "No Selection", "Please select an answer first!")
            return
        
        correct_indices = [i for i, ans in enumerate(self.current_question.answers) if ans['is_correct']]
        is_correct = set(self.selected_answers) == set(correct_indices)
        old_rank = self.current_question.rank
        
        # Update answer styling
        for i, container in enumerate(self.answer_widgets):
            if i in correct_indices:
                # Correct answer
                container.setStyleSheet("""
                    QWidget {
                        background-color: #d1fae5;
                        border: 2px solid #10b981;
                        border-radius: 10px;
                        padding: 4px;
                    }
                """)
                container.answer_text.setStyleSheet("""
                    QLabel {
                        font-size: 15px;
                        color: #065f46;
                        font-weight: 600;
                        padding: 4px;
                    }
                """)
            elif i in self.selected_answers:
                # Wrong selection
                container.setStyleSheet("""
                    QWidget {
                        background-color: #fee2e2;
                        border: 2px solid #ef4444;
                        border-radius: 10px;
                        padding: 4px;
                    }
                """)
                container.answer_text.setStyleSheet("""
                    QLabel {
                        font-size: 15px;
                        color: #991b1b;
                        padding: 4px;
                    }
                """)
            
            container.selector.setEnabled(False)
            container.setCursor(Qt.CursorShape.ArrowCursor)
        
        # Show feedback
        if is_correct:
            self.feedback_label.setText("✓ Correct!")
            self.feedback_container.setStyleSheet("""
                QWidget {
                    background-color: #d1fae5;
                    border-left: 4px solid #10b981;
                    border-radius: 8px;
                }
            """)
            self.feedback_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: 600;
                    color: #065f46;
                }
            """)
            
            self.manager.quick_rank_up(self.current_question)
            if self.current_question.rank != old_rank:
                self.show_notification(f"Rank Up!\n{old_rank} → {self.current_question.rank}")
        else:
            correct_answers = [self.current_question.answers[i]['text'] for i in correct_indices]
            self.feedback_label.setText(f"✗ Incorrect\nCorrect: {', '.join(correct_answers)}")
            self.feedback_container.setStyleSheet("""
                QWidget {
                    background-color: #fee2e2;
                    border-left: 4px solid #ef4444;
                    border-radius: 8px;
                }
            """)
            self.feedback_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: 600;
                    color: #991b1b;
                }
            """)
            
            self.manager.quick_rank_down(self.current_question)
            if self.current_question.rank != old_rank:
                self.show_notification(f"Rank Down\n{old_rank} → {self.current_question.rank}")
        
        # Show source
        self.source_label.setText(f"Source: {self.current_question.source}")
        
        # Update rank display
        stars = "★" * self.current_question.rank + "☆" * (5 - self.current_question.rank)
        self.rank_display.setText(stars)
        
        self.feedback_container.setVisible(True)
        self.check_btn.setVisible(False)
        self.next_btn.setVisible(True)
    
    def return_to_menu(self):
        if self.return_callback:
            self.return_callback()
    
    def call_tutorial(self):
        import tutorial
        self.tutorial_window = tutorial.tutorialWindow()
        self.tutorial_window.show()