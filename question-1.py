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
        self.answer_checkboxes = []
        self.max_selections = 1
        self.radio_group = QButtonGroup(self) 
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)
        
        # === TOP BAR ===
        top_bar = QHBoxLayout()
        
        self.back_btn = QPushButton("← Back to Menu")
        self.back_btn.setStyleSheet(
            "QPushButton { background: none; border: none; color: #f0f0f0; font-size: 13px; "
            "padding: 8px 12px; text-align: left; } "
            "QPushButton:hover { color: #000; background-color: #f5f5f5; border-radius: 6px; }"
        )
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.return_to_menu)
        top_bar.addWidget(self.back_btn)
        
        top_bar.addStretch()
        
        self.tutorial_btn = QPushButton("?")
        self.tutorial_btn.setFixedSize(32, 32)
        self.tutorial_btn.setStyleSheet(
            "QPushButton { border: none; border-radius: 16px; color: #666; "
            "font-size: 16px; font-weight: bold; } "
            "QPushButton:hover { background-color: #e0e0e0; }"
        )
        self.tutorial_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tutorial_btn.clicked.connect(self.call_tutorial)
        top_bar.addWidget(self.tutorial_btn)
        
        main_layout.addLayout(top_bar)
        
        # === QUESTION CARD ===
        question_card = QWidget()
        question_card.setStyleSheet("QWidget { border-radius: 12px; }")
        
        question_layout = QVBoxLayout()
        question_layout.setContentsMargins(30, 30, 30, 30)
        question_layout.setSpacing(15)
        
        self.question_label = QLabel()
        self.question_label.setWordWrap(True)
        self.question_label.setStyleSheet(
            "QLabel { font-size: 18px; font-weight: 500; line-height: 1.5; color: #1a1a1a; }"
        )
        question_layout.addWidget(self.question_label)
        
        # Instruction text
        self.instruction_label = QLabel()
        self.instruction_label.setStyleSheet(
            "QLabel { font-size: 13px; color: #000; margin-top: 8px; }"
        )
        question_layout.addWidget(self.instruction_label)
        
        question_card.setLayout(question_layout)
        main_layout.addWidget(question_card)

        # === RANK INDICATOR WITH CHANGE DISPLAY ===
        rank_container = QHBoxLayout()
        rank_container.addStretch()
        
        self.rank_display = QLabel()
        self.rank_display.setStyleSheet(
            "QLabel { background-color: transparent; color: #FFB800; "
            "font-size: 20px; letter-spacing: 2px; }"
        )
        rank_container.addWidget(self.rank_display)
        
        # Add rank change indicator (starts hidden)
        self.rank_change_label = QLabel()
        self.rank_change_label.setStyleSheet(
            "QLabel { background-color: transparent; "
            "font-size: 18px; font-weight: bold; margin-left: 10px; }"
        )
        self.rank_change_label.setVisible(False)
        rank_container.addWidget(self.rank_change_label)
        
        rank_container.addStretch()
        main_layout.addLayout(rank_container)
        
        # Animation for rank change
        self.rank_change_animation = QPropertyAnimation(self.rank_change_label, b"opacity")
        self.rank_change_animation.setDuration(2000)
        self.rank_change_animation.setStartValue(1.0)
        self.rank_change_animation.setEndValue(0.0)
        self.rank_change_animation.finished.connect(self.on_rank_animation_finished)
        
        # Timer for updating rank after animation
        self.rank_update_timer = QTimer()
        self.rank_update_timer.setSingleShot(True)
        self.rank_update_timer.timeout.connect(self.update_rank_display)
        
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
        self.feedback_label.setStyleSheet(
            "QLabel { font-size: 14px; font-weight: 500; }"
        )
        feedback_layout.addWidget(self.feedback_label)
        
        self.source_label = QLabel()
        self.source_label.setStyleSheet(
            "QLabel { font-size: 12px; color: #666; margin-top: 5px; font-style: italic; }"
        )
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
    
    def show_rank_change(self, old_rank, new_rank):
        """Show rank change beside the rank display with animation"""
        change = new_rank - old_rank
        if change == 0:
            return
        
        # Set the change text and color
        if change > 0:
            stars = "★" * abs(change)
            self.rank_change_label.setText(f"+{stars}")
            self.rank_change_label.setStyleSheet(
                "QLabel { background-color: transparent; color: #10b981; "
                "font-size: 18px; font-weight: bold; margin-left: 10px; }"
            )
        else:
            stars = "★" * abs(change)
            self.rank_change_label.setText(f"-{stars}")
            self.rank_change_label.setStyleSheet(
                "QLabel { background-color: transparent; color: #ef4444; "
                "font-size: 18px; font-weight: bold; margin-left: 10px; }"
            )
        
        # Show the change label
        self.rank_change_label.setVisible(True)
        
        # Start fade out animation after a brief display
        QTimer.singleShot(800, lambda: self.start_rank_fade())
        
        # Update the actual rank display after animation
        self.rank_update_timer.start(2800)
    
    def start_rank_fade(self):
        """Start the fade out animation for rank change"""
        # Create a fade effect
        effect = QGraphicsOpacityEffect()
        self.rank_change_label.setGraphicsEffect(effect)
        
        animation = QPropertyAnimation(effect, b"opacity")
        animation.setDuration(2000)
        animation.setStartValue(1.0)
        animation.setEndValue(0.0)
        animation.start()
        
        # Store animation to prevent garbage collection
        self.rank_fade_animation = animation
        self.rank_fade_animation.finished.connect(self.on_rank_animation_finished)
    
    def on_rank_animation_finished(self):
        """Hide the rank change label after animation"""
        self.rank_change_label.setVisible(False)
        self.rank_change_label.setGraphicsEffect(None)
    
    def update_rank_display(self):
        """Update the rank display to show new rank"""
        stars = "★" * self.current_question.rank + "☆" * (5 - self.current_question.rank)
        self.rank_display.setText(stars)
    
    def load_next_question(self):
        """Load the next question"""
        self.current_question = self.manager.get_random_question()
        
        if not self.current_question:
            QMessageBox.information(self, "No Questions", "No questions available!")
            return
        
        # Reset state
        self.selected_answers = []
        self.answer_checkboxes = []
        self.radio_group = QButtonGroup(self)
        
        # Clear previous answers
        for widget in self.answer_widgets:
            widget.deleteLater()
        self.answer_widgets.clear()
        
        # Set question text
        self.question_label.setText(self.current_question.question)
        
        # Set instruction based on question type
        if self.current_question.type == "single":
            self.instruction_label.setText("Select one answer:")
            self.max_selections = 1
        else:
            num_correct = sum(1 for ans in self.current_question.answers if ans['is_correct'])
            self.instruction_label.setText(f"Select {num_correct} answers:")
            self.max_selections = num_correct
        
        # Display rank
        stars = "★" * self.current_question.rank + "☆" * (5 - self.current_question.rank)
        self.rank_display.setText(stars)
        
        # Create answer widgets
        for i, answer in enumerate(self.current_question.answers):
            answer_widget = self.create_answer_widget(answer, i)
            self.answers_layout.addWidget(answer_widget)
            self.answer_widgets.append(answer_widget)
        
        # Reset feedback
        self.feedback_container.setVisible(False)
        self.check_btn.setVisible(True)
        self.next_btn.setVisible(False)
    
    def create_answer_widget(self, answer, index):
        """Create a styled answer widget with either checkbox or radio button"""
        answer_container = QWidget()
        answer_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border-radius: 10px;
                padding: 4px;
            }
            QWidget:hover {
                border-color: #2563eb;
                background-color: #f8faff;
            }
        """)
        
        answer_layout = QHBoxLayout()
        answer_layout.setContentsMargins(12, 12, 12, 12)
        answer_layout.setSpacing(12)
        
        # Create checkbox or radio button based on question type
        if self.current_question.type == "single":
            selector = QRadioButton()
            self.radio_group.addButton(selector, index)
            selector.toggled.connect(lambda checked, i=index: self.on_radio_selected(i, checked))
        else:
            selector = QCheckBox()
            selector.toggled.connect(lambda checked, i=index: self.on_checkbox_toggled(i, checked))
            self.answer_checkboxes.append(selector)
        
        selector.setStyleSheet("""
            QCheckBox, QRadioButton {
                spacing: 8px;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 22px;
                height: 22px;
                border: 2px solid #d1d5db;
                background-color: white;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                background-color: #2563eb;
                border-color: #2563eb;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTMuMzMzMyA0TDYgMTEuMzMzMyAyLjY2NjY3IDgiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+);
            }
            QCheckBox::indicator {
                border-radius: 4px;
            }
            QRadioButton::indicator {
                border-radius: 11px;
            }
            QCheckBox::indicator:hover, QRadioButton::indicator:hover {
                border-color: #1d4ed8;
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
        
        # Store references for later access
        answer_container.selector = selector
        answer_container.answer_text = answer_text
        answer_container.index = index
        
        # Make entire container clickable
        def toggle_selector(event, sel=selector):
            if sel.isEnabled():
                sel.setChecked(not sel.isChecked())
        
        answer_container.mousePressEvent = toggle_selector
        
        return answer_container
    
    def on_radio_selected(self, index, checked):
        """Handle radio button selection (single choice)"""
        if checked:
            self.selected_answers = [index]
    
    def on_checkbox_toggled(self, index, checked):
        """Handle checkbox toggle with selection limiting"""
        if checked:
            # Add to selected answers
            if index not in self.selected_answers:
                self.selected_answers.append(index)
            
            # If we've reached the max, disable other checkboxes
            if len(self.selected_answers) >= self.max_selections:
                for i, checkbox in enumerate(self.answer_checkboxes):
                    if i not in self.selected_answers:
                        checkbox.setEnabled(False)
                        # Also update container styling to show it's disabled
                        self.answer_widgets[i].setStyleSheet("""
                            QWidget {
                                background-color: #f5f5f5;
                                border-radius: 10px;
                                padding: 4px;
                                opacity: 0.6;
                            }
                        """)
        else:
            # Remove from selected answers
            if index in self.selected_answers:
                self.selected_answers.remove(index)
            
            # Re-enable all checkboxes when below limit
            if len(self.selected_answers) < self.max_selections:
                for i, checkbox in enumerate(self.answer_checkboxes):
                    checkbox.setEnabled(True)
                    # Reset container styling
                    self.answer_widgets[i].setStyleSheet("""
                        QWidget {
                            background-color: transparent;
                            border-radius: 10px;
                            padding: 4px;
                        }
                        QWidget:hover {
                            border-color: #2563eb;
                            background-color: #f8faff;
                        }
                    """)
    
    def check_answer(self):
        """Check if the selected answer(s) are correct"""
        if not self.selected_answers:
            QMessageBox.warning(self, "No Selection", "Please select an answer first!")
            return
        
        correct_indices = [
            i for i, ans in enumerate(self.current_question.answers) 
            if ans['is_correct']
        ]
        is_correct = set(self.selected_answers) == set(correct_indices)
        old_rank = self.current_question.rank
        
        # Update answer styling to show correct/incorrect
        for i, container in enumerate(self.answer_widgets):
            if i in correct_indices:
                # Correct answer - show in green
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
                # Wrong selection - show in red
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
            
            # Disable all selectors
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
                self.show_rank_change(old_rank, self.current_question.rank)
        else:
            correct_answers = [
                self.current_question.answers[i]['text'] 
                for i in correct_indices
            ]
            self.feedback_label.setText(
                f"✗ Incorrect\nCorrect: {', '.join(correct_answers)}"
            )
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
                self.show_rank_change(old_rank, self.current_question.rank)
        
        # Show source
        self.source_label.setText(f"Source: {self.current_question.source}")
        
        # Don't update rank display immediately - let animation handle it
        if self.current_question.rank == old_rank:
            # Only update immediately if rank didn't change
            stars = "★" * self.current_question.rank + "☆" * (5 - self.current_question.rank)
            self.rank_display.setText(stars)
        
        self.feedback_container.setVisible(True)
        self.check_btn.setVisible(False)
        self.next_btn.setVisible(True)
    
    def return_to_menu(self):
        """Return to the main menu"""
        if self.return_callback:
            self.return_callback()
    
    def call_tutorial(self):
        """Open the tutorial window"""
        import tutorial
        self.tutorial_window = tutorial.tutorialWindow()
        self.tutorial_window.show()
