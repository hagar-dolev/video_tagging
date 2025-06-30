import sys
import os
import cv2
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                            QFileDialog, QMessageBox, QProgressBar, QSlider,
                            QComboBox, QLineEdit, QCheckBox, QGroupBox, QScrollArea,
                            QListWidget, QListWidgetItem, QSplitter, QFrame)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QImage, QPixmap
import csv
import json
from datetime import timedelta

class VideoTagger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Video Tagger")
        self.setGeometry(100, 100, 1400, 900)  # Slightly smaller default width
        
        # Initialize variables
        self.video_files = []
        self.current_index = 0
        self.tags = {}
        self.is_playing = False
        self.thumbnail_label = None
        
        # Predefined tagging options
        self.location_classes = [
            "Indoor", "Outdoor", "Office", "Home", "Street", "Park", "Restaurant", 
            "Gym", "Studio", "Classroom", "Conference Room", "Kitchen", "Bedroom",
            "Bathroom", "Garage", "Garden", "Beach", "Mountain", "Forest", "Urban",
            "Rural", "Suburban", "Industrial", "Commercial", "Residential"
        ]
        
        self.action_types = [
            "Walking", "Running", "Sitting", "Standing", "Talking", "Listening",
            "Cooking", "Eating", "Drinking", "Working", "Reading", "Writing",
            "Typing", "Exercising", "Dancing", "Singing", "Playing", "Teaching",
            "Learning", "Presenting", "Meeting", "Shopping", "Cleaning", "Driving",
            "Cycling", "Swimming", "Lifting", "Carrying", "Opening", "Closing"
        ]
        
        self.movement_types = [
            "Static", "Pan Left", "Pan Right", "Tilt Up", "Tilt Down", "Tilt Left", "Tilt Right", "Zoom In",
            "Zoom Out", "Dolly In", "Dolly Out", "Tracking Left", "Tracking Right", "Crane Up", "Crane Down", 
            "Handheld", "Steadicam", "Drone", "Aerial", "Other"
        ]
        
        self.shot_types = [
            "Extreme Long Shot", "Long Shot", "Full Shot", "Medium Long Shot",
            "Medium Shot", "Medium Close-Up", "Close-Up", "Extreme Close-Up",
            "Two Shot", "Three Shot", "Group Shot", "Over-the-Shoulder",
            "Point of View", "Low Angle", "High Angle", "Eye Level", "Bird's Eye",
            "Worm's Eye", "Dutch Angle", "Profile Shot", "Frontal Shot"
        ]
        
        # Content movement types
        self.content_movement_types = [
            "High", "Medium", "Low", "No movement"
        ]
        
        # Handheld camera options
        self.handheld_options = [
            "Yes", "No", "Partially", "Uncertain"
        ]
        
        # Depth of field options
        self.depth_of_field_options = [
            "Shallow", "Medium", "Deep", "Very Deep", "Variable", "Uncertain"
        ]
        
        # Color scale options
        self.color_scale_options = [
            "Color", "Black & White", "Sepia", "Monochrome", "High Contrast", 
            "Low Saturation", "High Saturation", "Warm Tone", "Cool Tone", 
            "Neutral", "Vintage", "Cinematic", "Other"
        ]
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel for video preview
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Video widget for multimedia playback
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(640, 480)
        left_layout.addWidget(self.video_widget)
        
        # Thumbnail label (initially hidden)
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setMinimumSize(640, 480)
        self.thumbnail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thumbnail_label.setStyleSheet("background-color: black;")
        left_layout.addWidget(self.thumbnail_label)
        self.thumbnail_label.hide()
        
        # Media player and audio output
        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)
        
        # Connect media player signals
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.media_player.playbackStateChanged.connect(self.on_playback_state_changed)
        
        # Video controls
        controls_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.play_button = QPushButton("Play/Pause")
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.next_button)
        left_layout.addLayout(controls_layout)
        
        # Progress slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.sliderMoved.connect(self.set_position)
        left_layout.addWidget(self.progress_slider)
        
        # Progress bar for file navigation
        self.progress_bar = QProgressBar()
        left_layout.addWidget(self.progress_bar)
        
        # Right panel for tagging (scrollable)
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(5)  # Reduced from 10
        right_layout.setContentsMargins(8, 8, 8, 8)  # Reduced from 10, 10, 10, 10
        
        # Select directory button
        self.select_dir_button = QPushButton("Select Video Directory")
        self.select_dir_button.setStyleSheet("QPushButton { padding: 8px; font-weight: bold; }")
        right_layout.addWidget(self.select_dir_button)
        
        # File info
        self.file_info = QLabel("No file selected")
        self.file_info.setStyleSheet("QLabel { padding: 5px; background-color: #f0f0f0; border-radius: 3px; }")
        right_layout.addWidget(self.file_info)
        
        # Status label for auto-save feedback
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("QLabel { padding: 3px; color: #4CAF50; font-size: 10px; }")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(self.status_label)
        
        # Add a separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setFrameShadow(QFrame.Shadow.Sunken)
        right_layout.addWidget(separator1)
        
        # People present section
        people_group = QGroupBox("People Present")
        people_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        people_layout = QVBoxLayout(people_group)
        self.people_input = QLineEdit()
        self.people_input.setPlaceholderText("Enter names separated by commas (e.g., John, Jane, Mike)")
        people_layout.addWidget(self.people_input)
        right_layout.addWidget(people_group)
        
        # Key moments section
        moments_group = QGroupBox("Key Moments (Time Frames)")
        moments_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        moments_layout = QVBoxLayout(moments_group)
        
        # Timestamp button and input layout
        moments_header_layout = QHBoxLayout()
        self.timestamp_button = QPushButton("Add Current Time")
        self.timestamp_button.setStyleSheet("QPushButton { padding: 5px; background-color: #4CAF50; color: white; border-radius: 3px; } QPushButton:hover { background-color: #45a049; }")
        self.timestamp_button.clicked.connect(self.add_current_timestamp)
        moments_header_layout.addWidget(self.timestamp_button)
        moments_header_layout.addStretch()
        moments_layout.addLayout(moments_header_layout)
        
        self.moments_input = QTextEdit()
        self.moments_input.setPlaceholderText("Enter key moments with timestamps (e.g., 00:15 - Introduction, 01:30 - Main event)")
        self.moments_input.setMaximumHeight(60)
        moments_layout.addWidget(self.moments_input)
        right_layout.addWidget(moments_group)
        
        # General caption section
        caption_group = QGroupBox("General Caption")
        caption_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        caption_layout = QVBoxLayout(caption_group)
        self.caption_input = QTextEdit()
        self.caption_input.setPlaceholderText("Describe the overall video content (e.g., 'A cooking tutorial showing how to make pasta from scratch')")
        self.caption_input.setMaximumHeight(60)
        caption_layout.addWidget(self.caption_input)
        right_layout.addWidget(caption_group)
        
        # Location classes section
        location_group = QGroupBox("Location Classes")
        location_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        location_layout = QVBoxLayout(location_group)
        self.location_combo = QComboBox()
        self.location_combo.addItems(self.location_classes)
        self.location_combo.setEditable(True)
        self.location_combo.setPlaceholderText("Select or type location class")
        location_layout.addWidget(self.location_combo)
        right_layout.addWidget(location_group)
        
        # Actions section
        actions_group = QGroupBox("Actions")
        actions_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        actions_layout = QVBoxLayout(actions_group)
        self.actions_input = QTextEdit()
        self.actions_input.setPlaceholderText("Enter actions or select from common ones")
        self.actions_input.setMaximumHeight(60)
        actions_layout.addWidget(self.actions_input)
        
        # Common actions checkboxes
        actions_checkbox_layout = QHBoxLayout()
        self.action_checkboxes = {}
        
        # Create multiple rows of checkboxes for better space usage
        actions_row1_layout = QHBoxLayout()
        actions_row2_layout = QHBoxLayout()
        
        for i, action in enumerate(self.action_types[:8]):  # Show first 8 as checkboxes
            checkbox = QCheckBox(action)
            self.action_checkboxes[action] = checkbox
            if i < 4:
                actions_row1_layout.addWidget(checkbox)
            else:
                actions_row2_layout.addWidget(checkbox)
        
        actions_checkbox_layout.addLayout(actions_row1_layout)
        actions_checkbox_layout.addLayout(actions_row2_layout)
        actions_layout.addLayout(actions_checkbox_layout)
        right_layout.addWidget(actions_group)
        
        # Movement section
        movement_group = QGroupBox("Camera Movement")
        movement_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        movement_layout = QVBoxLayout(movement_group)
        
        # Movement checkboxes for multiple selection
        self.movement_checkboxes = {}
        movement_checkbox_layout = QVBoxLayout()
        
        # Create three columns of checkboxes for better space usage
        movement_col1_layout = QHBoxLayout()
        movement_col2_layout = QHBoxLayout()
        movement_col3_layout = QHBoxLayout()
        
        for i, movement in enumerate(self.movement_types):
            checkbox = QCheckBox(movement)
            checkbox.stateChanged.connect(self.update_movements_from_checkboxes)
            self.movement_checkboxes[movement] = checkbox
            
            # Distribute checkboxes into three columns
            if i < len(self.movement_types) // 3:
                movement_col1_layout.addWidget(checkbox)
            elif i < 2 * len(self.movement_types) // 3:
                movement_col2_layout.addWidget(checkbox)
            else:
                movement_col3_layout.addWidget(checkbox)
        
        movement_checkbox_layout.addLayout(movement_col1_layout)
        movement_checkbox_layout.addLayout(movement_col2_layout)
        movement_checkbox_layout.addLayout(movement_col3_layout)
        movement_layout.addLayout(movement_checkbox_layout)
        
        # Movement display area (read-only)
        self.movement_display = QTextEdit()
        self.movement_display.setPlaceholderText("Selected movements will appear here...")
        self.movement_display.setMaximumHeight(50)
        self.movement_display.setReadOnly(True)
        movement_layout.addWidget(self.movement_display)
        
        # Movement description field (for "Other" option)
        self.movement_description = QLineEdit()
        self.movement_description.setPlaceholderText("Describe custom camera movement (appears when 'Other' is selected)")
        self.movement_description.setVisible(False)
        movement_layout.addWidget(self.movement_description)
        right_layout.addWidget(movement_group)
        
        # Content Movement section
        content_movement_group = QGroupBox("Content Movement")
        content_movement_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        content_movement_layout = QVBoxLayout(content_movement_group)
        self.content_movement_combo = QComboBox()
        self.content_movement_combo.addItems(self.content_movement_types)
        content_movement_layout.addWidget(self.content_movement_combo)
        right_layout.addWidget(content_movement_group)
        
        # Shot types section
        shot_group = QGroupBox("Shot Type")
        shot_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        shot_layout = QVBoxLayout(shot_group)
        self.shot_combo = QComboBox()
        self.shot_combo.addItems(self.shot_types)
        shot_layout.addWidget(self.shot_combo)
        right_layout.addWidget(shot_group)
        
        # Handheld camera section
        handheld_group = QGroupBox("Handheld Camera")
        handheld_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        handheld_layout = QVBoxLayout(handheld_group)
        self.handheld_combo = QComboBox()
        self.handheld_combo.addItems(self.handheld_options)
        handheld_layout.addWidget(self.handheld_combo)
        right_layout.addWidget(handheld_group)
        
        # Depth of field section
        dof_group = QGroupBox("Depth of Field")
        dof_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        dof_layout = QVBoxLayout(dof_group)
        self.dof_combo = QComboBox()
        self.dof_combo.addItems(self.depth_of_field_options)
        dof_layout.addWidget(self.dof_combo)
        right_layout.addWidget(dof_group)
        
        # Color scale section
        color_group = QGroupBox("Color Scale")
        color_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        color_layout = QVBoxLayout(color_group)
        self.color_combo = QComboBox()
        self.color_combo.addItems(self.color_scale_options)
        self.color_combo.currentTextChanged.connect(self.on_color_scale_changed)
        color_layout.addWidget(self.color_combo)
        
        # Color scale description field (for "Other" option)
        self.color_description = QLineEdit()
        self.color_description.setPlaceholderText("Describe color scale (appears when 'Other' is selected)")
        self.color_description.setVisible(False)
        color_layout.addWidget(self.color_description)
        right_layout.addWidget(color_group)
        
        # General tags section
        tags_group = QGroupBox("General Tags")
        tags_group.setStyleSheet("QGroupBox { font-weight: bold; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }")
        tags_layout = QVBoxLayout(tags_group)
        self.tag_input = QTextEdit()
        self.tag_input.setPlaceholderText("Enter additional general tags here...")
        self.tag_input.setMaximumHeight(60)
        tags_layout.addWidget(self.tag_input)
        right_layout.addWidget(tags_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Tags")
        self.save_button.setStyleSheet("QPushButton { padding: 8px; background-color: #2196F3; color: white; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #1976D2; }")
        self.export_button = QPushButton("Export to CSV")
        self.export_button.setStyleSheet("QPushButton { padding: 8px; background-color: #FF9800; color: white; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #F57C00; }")
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.export_button)
        right_layout.addLayout(buttons_layout)
        
        # Add stretch to push everything to the top
        right_layout.addStretch()
        
        # Set up scroll area
        right_scroll.setWidget(right_panel)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_scroll)
        splitter.setSizes([1000, 350])  # More space for video, less for tagging panel
        
        # Connect signals
        self.prev_button.clicked.connect(self.previous_video)
        self.next_button.clicked.connect(self.next_video)
        self.play_button.clicked.connect(self.toggle_play)
        self.save_button.clicked.connect(self.save_tags)
        self.export_button.clicked.connect(self.export_to_csv)
        self.select_dir_button.clicked.connect(self.select_directory)
        
        # Connect action checkboxes
        for checkbox in self.action_checkboxes.values():
            checkbox.stateChanged.connect(self.update_actions_from_checkboxes)
        
        # Connect input field changes to update UI
        self.people_input.textChanged.connect(self.update_ui)
        self.moments_input.textChanged.connect(self.update_ui)
        self.caption_input.textChanged.connect(self.update_ui)
        self.location_combo.currentTextChanged.connect(self.update_ui)
        self.actions_input.textChanged.connect(self.update_ui)
        self.movement_description.textChanged.connect(self.update_ui)
        self.content_movement_combo.currentTextChanged.connect(self.update_ui)
        self.shot_combo.currentTextChanged.connect(self.update_ui)
        self.handheld_combo.currentTextChanged.connect(self.update_ui)
        self.dof_combo.currentTextChanged.connect(self.update_ui)
        self.color_combo.currentTextChanged.connect(self.update_ui)
        self.color_description.textChanged.connect(self.update_ui)
        self.tag_input.textChanged.connect(self.update_ui)
        
        # Timer for updating progress slider
        self.timer = QTimer()
        self.timer.setInterval(1000)  # Update every second
        self.timer.timeout.connect(self.update_progress)
        
        # Initialize UI
        self.update_ui()
    
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Video Directory")
        if directory:
            self.video_files = []
            for file in os.listdir(directory):
                if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv')):
                    self.video_files.append(os.path.join(directory, file))
            
            if not self.video_files:
                QMessageBox.warning(self, "No Videos", "No video files found in the selected directory!\n\nSupported formats: .mp4, .mov, .avi, .mkv, .wmv, .flv")
                self.file_info.setText("No video files found in selected directory")
                self.update_ui()
                return
            
            self.current_index = 0
            self.progress_bar.setMaximum(len(self.video_files))
            self.load_current_video()
            self.update_ui()
    
    def load_current_video(self):
        if not self.video_files:
            return
            
        # Stop current playback
        self.media_player.stop()
        self.timer.stop()
        
        # Show thumbnail first
        self.show_thumbnail()
        
        # Load new video
        video_path = self.video_files[self.current_index]
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        
        self.update_file_info()
        self.progress_bar.setValue(self.current_index + 1)
        
        # Load existing tags if any
        if self.video_files[self.current_index] in self.tags:
            tag_data = self.tags[self.video_files[self.current_index]]
            if isinstance(tag_data, dict):
                # Load structured tags
                self.people_input.setText(tag_data.get('people', ''))
                self.moments_input.setText(tag_data.get('moments', ''))
                self.caption_input.setText(tag_data.get('caption', ''))
                self.location_combo.setCurrentText(tag_data.get('location', ''))
                self.actions_input.setText(tag_data.get('actions', ''))
                
                # Load movement checkboxes
                saved_movements = tag_data.get('movement', '').split(',') if tag_data.get('movement') else []
                for movement, checkbox in self.movement_checkboxes.items():
                    checkbox.setChecked(movement.strip() in [m.strip() for m in saved_movements])
                self.movement_display.setText(tag_data.get('movement', ''))
                self.movement_description.setText(tag_data.get('movement_description', ''))
                
                self.content_movement_combo.setCurrentText(tag_data.get('content_movement', ''))
                self.shot_combo.setCurrentText(tag_data.get('shot_type', ''))
                self.handheld_combo.setCurrentText(tag_data.get('handheld', ''))
                self.dof_combo.setCurrentText(tag_data.get('depth_of_field', ''))
                self.color_combo.setCurrentText(tag_data.get('color_scale', ''))
                self.color_description.setText(tag_data.get('color_scale_description', ''))
                self.tag_input.setText(tag_data.get('general_tags', ''))
                
                # Show/hide description fields based on current selections
                self.movement_description.setVisible(bool(saved_movements) and saved_movements[-1].strip() == 'Other')
                self.color_description.setVisible(tag_data.get('color_scale', '') == 'Other')
                
                # Load action checkboxes
                saved_actions = tag_data.get('actions', '').split(',') if tag_data.get('actions') else []
                for action, checkbox in self.action_checkboxes.items():
                    checkbox.setChecked(action.strip() in [a.strip() for a in saved_actions])
            else:
                # Legacy format - load as general tags
                self.tag_input.setText(tag_data)
                self.clear_structured_tags()
        else:
            self.clear_structured_tags()
    
    def clear_structured_tags(self):
        """Clear all structured tag inputs"""
        self.people_input.clear()
        self.moments_input.clear()
        self.caption_input.clear()
        self.location_combo.setCurrentText('')
        self.actions_input.clear()
        
        # Clear movement checkboxes and display
        for checkbox in self.movement_checkboxes.values():
            checkbox.setChecked(False)
        self.movement_display.clear()
        self.movement_description.clear()
        self.movement_description.setVisible(False)
        
        self.content_movement_combo.setCurrentText('')
        self.shot_combo.setCurrentText('')
        self.handheld_combo.setCurrentText('')
        self.dof_combo.setCurrentText('')
        self.color_combo.setCurrentText('')
        self.color_description.clear()
        self.color_description.setVisible(False)
            self.tag_input.clear()
        
        # Clear checkboxes
        for checkbox in self.action_checkboxes.values():
            checkbox.setChecked(False)
    
    def update_actions_from_checkboxes(self):
        """Update actions input based on checkbox selections"""
        selected_actions = []
        for action, checkbox in self.action_checkboxes.items():
            if checkbox.isChecked():
                selected_actions.append(action)
        
        current_text = self.actions_input.toPlainText()
        if selected_actions:
            # Add checkbox selections to existing text
            checkbox_actions = ', '.join(selected_actions)
            if current_text:
                self.actions_input.setText(f"{current_text}, {checkbox_actions}")
            else:
                self.actions_input.setText(checkbox_actions)
    
    def show_thumbnail(self):
        """Show a thumbnail of the first frame using OpenCV"""
        if not self.video_files:
            return
            
        try:
            # Use OpenCV to get the first frame
            cap = cv2.VideoCapture(self.video_files[self.current_index])
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Resize frame to fit the display
                frame = cv2.resize(frame, (640, 480))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)
                
                # Show thumbnail
                self.thumbnail_label.setPixmap(pixmap)
                self.thumbnail_label.show()
                self.video_widget.hide()
            else:
                # Show placeholder if thumbnail extraction fails
                self.thumbnail_label.setText("Video Preview\n(Click Play to start)")
                self.thumbnail_label.show()
                self.video_widget.hide()
                
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            self.thumbnail_label.setText("Video Preview\n(Click Play to start)")
            self.thumbnail_label.show()
            self.video_widget.hide()
    
    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            # Video loaded successfully, update progress slider
            duration = self.media_player.duration()
            if duration > 0:
                self.progress_slider.setMaximum(duration)
                self.progress_slider.setValue(0)
    
    def on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.is_playing = True
            self.timer.start()
            # Hide thumbnail and show video widget when playing
            self.thumbnail_label.hide()
            self.video_widget.show()
        else:
            self.is_playing = False
            self.timer.stop()
            # Show thumbnail when paused/stopped
            if state == QMediaPlayer.PlaybackState.StoppedState:
                self.show_thumbnail()
        self.update_ui()
    
    def update_progress(self):
        if self.media_player.isPlaying():
            position = self.media_player.position()
            self.progress_slider.setValue(position)
    
    def set_position(self, position):
        self.media_player.setPosition(position)
    
    def update_file_info(self):
        if self.video_files:
            filename = os.path.basename(self.video_files[self.current_index])
            self.file_info.setText(f"File: {filename}\n({self.current_index + 1} of {len(self.video_files)})")
    
    def previous_video(self):
        if self.current_index > 0:
            # Auto-save current tags before moving to previous video
            self.auto_save_current_tags()
            self.current_index -= 1
            self.load_current_video()
    
    def next_video(self):
        if self.current_index < len(self.video_files) - 1:
            # Auto-save current tags before moving to next video
            self.auto_save_current_tags()
            self.current_index += 1
            self.load_current_video()
    
    def auto_save_current_tags(self):
        """Automatically save tags for current video if there are any changes"""
        if not self.video_files:
            return
            
        current_file = self.video_files[self.current_index]
        
        # Collect all tag data
        tag_data = {
            'people': self.people_input.text().strip(),
            'moments': self.moments_input.toPlainText().strip(),
            'caption': self.caption_input.toPlainText().strip(),
            'location': self.location_combo.currentText().strip(),
            'actions': self.actions_input.toPlainText().strip(),
            'movement': self.movement_display.toPlainText().strip(),
            'movement_description': self.movement_description.text().strip(),
            'content_movement': self.content_movement_combo.currentText().strip(),
            'shot_type': self.shot_combo.currentText().strip(),
            'handheld': self.handheld_combo.currentText().strip(),
            'depth_of_field': self.dof_combo.currentText().strip(),
            'color_scale': self.color_combo.currentText().strip(),
            'color_scale_description': self.color_description.text().strip(),
            'general_tags': self.tag_input.toPlainText().strip()
        }
        
        # Check if there's any content to save
        has_content = any(value for value in tag_data.values())
        if has_content:
            self.tags[current_file] = tag_data
            filename = os.path.basename(current_file)
            self.status_label.setText(f"✓ Auto-saved: {filename}")
            self.status_label.setStyleSheet("QLabel { padding: 3px; color: #4CAF50; font-size: 10px; }")
            
            # Clear status after 3 seconds
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))
            
            print(f"Auto-saved tags for: {filename}")
    
    def has_unsaved_changes(self):
        """Check if there are unsaved changes for the current video"""
        if not self.video_files:
            return False
            
        current_file = self.video_files[self.current_index]
        
        # Collect current tag data
        current_tag_data = {
            'people': self.people_input.text().strip(),
            'moments': self.moments_input.toPlainText().strip(),
            'caption': self.caption_input.toPlainText().strip(),
            'location': self.location_combo.currentText().strip(),
            'actions': self.actions_input.toPlainText().strip(),
            'movement': self.movement_display.toPlainText().strip(),
            'movement_description': self.movement_description.text().strip(),
            'content_movement': self.content_movement_combo.currentText().strip(),
            'shot_type': self.shot_combo.currentText().strip(),
            'handheld': self.handheld_combo.currentText().strip(),
            'depth_of_field': self.dof_combo.currentText().strip(),
            'color_scale': self.color_combo.currentText().strip(),
            'color_scale_description': self.color_description.text().strip(),
            'general_tags': self.tag_input.toPlainText().strip()
        }
        
        # Check if there's any content
        has_content = any(value for value in current_tag_data.values())
        if not has_content:
            return False
        
        # Compare with saved data
        if current_file in self.tags:
            saved_data = self.tags[current_file]
            if isinstance(saved_data, dict):
                return current_tag_data != saved_data
            else:
                # Legacy format - compare with general tags
                return current_tag_data['general_tags'] != saved_data
        
        # No saved data but we have content
        return True
    
    def toggle_play(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
    
    def save_tags(self):
        if self.video_files:
            current_file = self.video_files[self.current_index]
            
            # Collect all tag data
            tag_data = {
                'people': self.people_input.text().strip(),
                'moments': self.moments_input.toPlainText().strip(),
                'caption': self.caption_input.toPlainText().strip(),
                'location': self.location_combo.currentText().strip(),
                'actions': self.actions_input.toPlainText().strip(),
                'movement': self.movement_display.toPlainText().strip(),
                'movement_description': self.movement_description.text().strip(),
                'content_movement': self.content_movement_combo.currentText().strip(),
                'shot_type': self.shot_combo.currentText().strip(),
                'handheld': self.handheld_combo.currentText().strip(),
                'depth_of_field': self.dof_combo.currentText().strip(),
                'color_scale': self.color_combo.currentText().strip(),
                'color_scale_description': self.color_description.text().strip(),
                'general_tags': self.tag_input.toPlainText().strip()
            }
            
            # Only save if there's actual content
            has_content = any(value for value in tag_data.values())
            if has_content:
                self.tags[current_file] = tag_data
            QMessageBox.information(self, "Saved", "Tags saved successfully!")
            else:
                QMessageBox.warning(self, "No Tags", "Please enter at least one tag before saving!")
    
    def export_to_csv(self):
        if not self.tags:
            QMessageBox.warning(self, "No Tags", "No tags to export!")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Tags", "", "CSV Files (*.csv)")
        if file_path:
            # Prepare data for export
            data = []
            for file_path_key, tag_data in self.tags.items():
                if isinstance(tag_data, dict):
                    # New structured format
                    row = {
                        'file_path': file_path_key,
                        'people': tag_data.get('people', ''),
                        'key_moments': tag_data.get('moments', ''),
                        'caption': tag_data.get('caption', ''),
                        'location': tag_data.get('location', ''),
                        'actions': tag_data.get('actions', ''),
                        'movement': tag_data.get('movement', ''),
                        'movement_description': tag_data.get('movement_description', ''),
                        'content_movement': tag_data.get('content_movement', ''),
                        'shot_type': tag_data.get('shot_type', ''),
                        'handheld': tag_data.get('handheld', ''),
                        'depth_of_field': tag_data.get('depth_of_field', ''),
                        'color_scale': tag_data.get('color_scale', ''),
                        'color_scale_description': tag_data.get('color_scale_description', ''),
                        'general_tags': tag_data.get('general_tags', '')
                    }
                else:
                    # Legacy format - convert to structured
                    row = {
                        'file_path': file_path_key,
                        'people': '',
                        'key_moments': '',
                        'caption': '',
                        'location': '',
                        'actions': '',
                        'movement': '',
                        'movement_description': '',
                        'content_movement': '',
                        'shot_type': '',
                        'handheld': '',
                        'depth_of_field': '',
                        'color_scale': '',
                        'color_scale_description': '',
                        'general_tags': tag_data
                    }
                data.append(row)
            
            df = pd.DataFrame(data)
            # Use quoting=csv.QUOTE_ALL to ensure all fields are quoted consistently
            df.to_csv(file_path, index=False, quoting=csv.QUOTE_ALL)
            QMessageBox.information(self, "Exported", "Tags exported successfully!")
    
    def update_ui(self):
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.video_files) - 1)
        self.play_button.setEnabled(bool(self.video_files))
        self.save_button.setEnabled(bool(self.video_files))
        self.export_button.setEnabled(bool(self.tags))
        self.select_dir_button.setEnabled(True)  # Always enabled
        self.timestamp_button.setEnabled(bool(self.video_files))
        
        # Update save button text to indicate unsaved changes
        if self.has_unsaved_changes():
            self.save_button.setText("Save Tags*")
            self.save_button.setStyleSheet("QPushButton { padding: 8px; background-color: #FF5722; color: white; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #E64A19; }")
        else:
            self.save_button.setText("Save Tags")
            self.save_button.setStyleSheet("QPushButton { padding: 8px; background-color: #2196F3; color: white; border-radius: 3px; font-weight: bold; } QPushButton:hover { background-color: #1976D2; }")
        
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setText("Pause")
        else:
            self.play_button.setText("Play")
    
    def closeEvent(self, event):
        # Auto-save any unsaved changes before closing
        if self.has_unsaved_changes():
            self.auto_save_current_tags()
            print("Auto-saved final changes before closing")
        
        self.media_player.stop()
        event.accept()

    def add_current_timestamp(self):
        """Add current video timestamp to key moments"""
        if not self.video_files:
            QMessageBox.information(self, "No Video", "Please select a video directory first.")
            return
            
        if self.media_player.isPlaying() or self.media_player.position() > 0:
            current_pos = self.media_player.position()
            timestamp = str(timedelta(seconds=current_pos // 1000))
            current_text = self.moments_input.toPlainText().strip()
            
            # Check if the timestamp already exists at the end to prevent duplicates
            if current_text and current_text.endswith(f"{timestamp} -"):
                return  # Don't add duplicate timestamp
            
            if current_text:
                # Add newline only if there's existing content and it doesn't end with a newline
                if not current_text.endswith('\n'):
                    self.moments_input.setText(f"{current_text}\n{timestamp} - ")
                else:
                    self.moments_input.setText(f"{current_text}{timestamp} - ")
            else:
                self.moments_input.setText(f"{timestamp} - ")
            
            # Focus on the input for easy editing
            self.moments_input.setFocus()
            # Move cursor to end
            cursor = self.moments_input.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.moments_input.setTextCursor(cursor)
        else:
            QMessageBox.information(self, "No Video", "Please play the video first to get a timestamp.")

    def update_movements_from_checkboxes(self):
        """Update movement display based on selected checkboxes"""
        selected_movements = []
        for movement, checkbox in self.movement_checkboxes.items():
            if checkbox.isChecked():
                selected_movements.append(movement)
        
        self.movement_display.setText(', '.join(selected_movements))
        self.movement_description.setVisible(bool(selected_movements) and selected_movements[-1] == "Other")
        self.update_ui()
    
    def on_color_scale_changed(self, text):
        """Show/hide color scale description field based on selection"""
        self.color_description.setVisible(text == "Other")
        self.update_ui()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoTagger()
    window.show()
    window.select_directory()  # Automatically prompt for directory selection
    sys.exit(app.exec()) 