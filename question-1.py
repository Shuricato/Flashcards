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
        self.back_btn.setStyleSheet("QPushButton { background: none;border: none;color: #f0f0f0;font-size: 13px;padding: 8px 12px;text-align: left;} " \
        "QPushButton:hover { color: #000; background-color: #f5f5f5;border-radius: 6px;}")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.return_to_menu)
        top_bar.addWidget(self.back_btn)
        
        top_bar.addStretch()
        
        self.tutorial_btn = QPushButton("?")
        self.tutorial_btn.setFixedSize(32, 32)
        self.tutorial_btn.setStyleSheet("QPushButton { border: none; border-radius: 16px; color: #666; font-size: 16px; font-weight: bold; } QPushButton:hover { background-color: #e0e0e0; }")
        self.tutorial_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tutorial_btn.clicked.connect(self.call_tutorial)
        top_bar.addWidget(self.tutorial_btn)
        
        main_layout.addLayout(top_bar)
        
        # === QUESTION CARD ===
        question_card = QWidget()
        question_card.setStyleSheet(" QWidget {border-radius: 12px;}")
        
        question_layout = QVBoxLayout()
        question_layout.setContentsMargins(30, 30, 30, 30)
        question_layout.setSpacing(15)
        
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet("QLabel {font-size: 18px;font-weight: 500;line-height: 1.5;color: #1a1a1a;}")
        question_layout.addWidget(self.question_label)
        
        # Instruction text
        self.instruction_label = QLabel()
        self.instruction_label.setStyleSheet("QLabel {font-size: 13px;color: #000;margin-top: 8px;}")
        question_layout.addWidget(self.instruction_label)
        
        question_card.setLayout(question_layout)
        main_layout.addWidget(question_card)

        # === RANK INDICATOR (with animation support) ===
        rank_container = QHBoxLayout()
        rank_container.addStretch()
        
        # Create a stacked widget to switch between rank display and notification
        self.rank_stack = QStackedWidget()
        self.rank_stack.setStyleSheet("QStackedWidget { background-color: transparent; }")
        
        # Page 0: Normal rank display
        rank_page = QWidget()
        rank_page.setStyleSheet("QWidget { background-color: transparent; }")
        rank_layout = QVBoxLayout()
        rank_layout.setContentsMargins(0, 0, 0, 0)
        self.rank_display = QLabel()
        self.rank_display.setStyleSheet("QLabel { background-color: transparent; color: #FFB800;font-size: 20px;letter-spacing: 2px;}")
        self.rank_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rank_layout.addWidget(self.rank_display)
        rank_page.setLayout(rank_layout)
        
        # Page 1: Rank change notification
        notif_page = QWidget()
        notif_page.setStyleSheet("QWidget { background-color: transparent; }")
        notif_layout = QVBoxLayout()
        notif_layout.setContentsMargins(0, 0, 0, 0)
        self.rank_notification = QLabel()
        self.rank_notification.setStyleSheet("""
            QLabel {
                background-color: rgba(26, 26, 26, 0.95);
                color: white;
                font-size: 15px;
                font-weight: 600;
                padding: 12px 20px;
                border-radius: 10px;
            }
        """)
        self.rank_notification.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notif_layout.addWidget(self.rank_notification)
        notif_page.setLayout(notif_layout)
        
        self.rank_stack.addWidget(rank_page)  # Index 0
        self.rank_stack.addWidget(notif_page)  # Index 1
        
        rank_container.addWidget(self.rank_stack)
        rank_container.addStretch()
        main_layout.addLayout(rank_container)
        
        # Animation for rank notification
        self.rank_animation = QPropertyAnimation(self.rank_stack, b"currentIndex")
        self.rank_animation.setDuration(300)
        self.rank_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.notification_timer = QTimer()
        self.notification_timer.timeout.connect(self.hide_rank_notification)
        
        # === ANSWERS AREA ===
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: #f0f0f0; }")
        
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
        self.feedback_label.setStyleSheet("QLabel {font-size: 14px;font-weight: 500;}")
        feedback_layout.addWidget(self.feedback_label)
        
        self.source_label = QLabel()
        self.source_label.setStyleSheet("QLabel {font-size: 12px;color: #666;margin-top: 5px;font-style: italic;}")
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
        
        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #fafafa;")
        
        # Load first question
        self.load_next_question()
    
    def show_rank_notification(self, old_rank, new_rank, is_up):
        """Show animated rank change notification"""
        # Create the notification text with star transition
        old_stars = "★" * old_rank + "☆" * (5 - old_rank)
        new_stars = "★" * new_rank + "☆" * (5 - new_rank)
        
        if is_up:
            message = f"🎉 Rank Up!\n{old_stars} → {new_stars}"
            self.rank_notification.setStyleSheet("""
                QLabel {
                    background-color: rgba(16, 185, 129, 0.95);
                    color: white;
                    font-size: 15px;
                    font-weight: 600;
                    padding: 12px 20px;
                    border-radius: 10px;
                }
            """)
        else:
            message = f"Rank Down\n{old_stars} → {new_stars}"
            self.rank_notification.setStyleSheet("""
                QLabel {
                    background-color: rgba(239, 68, 68, 0.95);
                    color: white;
                    font-size: 15px;
                    font-weight: 600;
                    padding: 12px 20px;
                    border-radius: 10px;
                }
            """)
        
        self.rank_notification.setText(message)
        
        # Animate to notification
        self.rank_stack.setCurrentIndex(1)
        
        # Set timer to return to rank display
        self.notification_timer.start(2500)
    
    def hide_rank_notification(self):
        """Return to normal rank display"""
        self.rank_stack.setCurrentIndex(0)
        self.notification_timer.stop()
    
    def load_next_question(self):
        self.current_question = self.manager.get_weighted_random_question()
        
        if not self.current_question:
            QMessageBox.warning(self, "No Questions", "No questions available. Please select files from the main menu.")
            self.return_to_menu()
            return
        
        # Reset UI state
        self.selected_answers = []
        self.check_btn.setVisible(True)
        self.next_btn.setVisible(False)
        self.feedback_container.setVisible(False)
        self.rank_stack.setCurrentIndex(0)  # Ensure we're on rank display
        
        # Display question
        self.question_label.setText(self.current_question.text)
        
        # Update rank display
        stars = "★" * self.current_question.rank + "☆" * (5 - self.current_question.rank)
        self.rank_display.setText(stars)
        
        # Update instruction
        if self.current_question.question_type == "multiple_choice":
            correct_count = sum(1 for ans in self.current_question.answers if ans['is_correct'])
            self.instruction_label.setText(f"Select all correct answers ({correct_count} correct)")
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
                    background-color: #eff6ff;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
                    width: 22px;
                    height: 22px;
                    border-radius: 4px;
                    border: 2px solid #d1d5db;
                    background-color: white;
                }
                QCheckBox::indicator:hover, QRadioButton::indicator:hover {
                    border-color: #2563eb;
                }
                QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                    background-color: #2563eb;
                    border-color: #2563eb;
                }
                QRadioButton::indicator {
                    border-radius: 11px;
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
        
        # FIXED: Removed addStretch() to prevent scrollbar spacing issue
    
    def on_answer_selected(self, index, checked):
        if checked:
            self.selected_answers = [index]
    
    def on_answer_toggled(self, index, checked):
        # Limit selection to number of correct answers
        correct_count = sum(1 for ans in self.current_question.answers if ans['is_correct'])
        
        if checked:
            if index not in self.selected_answers:
                # Check if we've reached the limit
                if len(self.selected_answers) >= correct_count:
                    # Uncheck the checkbox - we're at the limit
                    QTimer.singleShot(0, lambda: self.answer_widgets[index].selector.setChecked(False))
                    QMessageBox.information(self, "Selection Limit", 
                                          f"You can only select up to {correct_count} answer(s).")
                else:
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
                self.show_rank_notification(old_rank, self.current_question.rank, is_up=True)
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
                self.show_rank_notification(old_rank, self.current_question.rank, is_up=False)
        
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
