import sys
import os
import cv2
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QTextEdit, 
                            QFileDialog, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap

class VideoTagger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Tagger")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize variables
        self.video_files = []
        self.current_index = 0
        self.tags = {}
        self.video_capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.is_playing = False  # Track play state
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # Left panel for video preview
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Video preview label
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(self.video_label)
        
        # Video controls
        controls_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.play_button = QPushButton("Play/Pause")
        controls_layout.addWidget(self.prev_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.next_button)
        left_layout.addLayout(controls_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        left_layout.addWidget(self.progress_bar)
        
        # Right panel for tagging
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Select directory button
        self.select_dir_button = QPushButton("Select Video Directory")
        right_layout.addWidget(self.select_dir_button)
        
        # File info
        self.file_info = QLabel("No file selected")
        right_layout.addWidget(self.file_info)
        
        # Tag input
        self.tag_input = QTextEdit()
        self.tag_input.setPlaceholderText("Enter tags here...")
        right_layout.addWidget(QLabel("Tags:"))
        right_layout.addWidget(self.tag_input)
        
        # Save button
        self.save_button = QPushButton("Save Tags")
        right_layout.addWidget(self.save_button)
        
        # Export button
        self.export_button = QPushButton("Export to CSV")
        right_layout.addWidget(self.export_button)
        
        # Add panels to main layout
        layout.addWidget(left_panel, stretch=2)
        layout.addWidget(right_panel, stretch=1)
        
        # Connect signals
        self.prev_button.clicked.connect(self.previous_video)
        self.next_button.clicked.connect(self.next_video)
        self.play_button.clicked.connect(self.toggle_play)
        self.save_button.clicked.connect(self.save_tags)
        self.export_button.clicked.connect(self.export_to_csv)
        self.select_dir_button.clicked.connect(self.select_directory)
        
        # Initialize UI
        self.update_ui()
    
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Video Directory")
        if directory:
            self.video_files = []
            for file in os.listdir(directory):
                if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    self.video_files.append(os.path.join(directory, file))
            
            if not self.video_files:
                QMessageBox.warning(self, "No Videos", "No video files found in the selected directory!\n\nSupported formats: .mp4, .mov, .avi, .mkv")
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
            
        if self.video_capture is not None:
            self.video_capture.release()
        
        self.video_capture = cv2.VideoCapture(self.video_files[self.current_index])
        self.update_file_info()
        self.update_frame()
        self.progress_bar.setValue(self.current_index + 1)
        
        # Load existing tags if any
        if self.video_files[self.current_index] in self.tags:
            self.tag_input.setText(self.tags[self.video_files[self.current_index]])
        else:
            self.tag_input.clear()
    
    def update_frame(self):
        if self.video_capture is None:
            return
            
        ret, frame = self.video_capture.read()
        if ret:
            # Resize frame to a smaller size for better performance
            frame = cv2.resize(frame, (640, 480))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qt_image))
        else:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    def update_file_info(self):
        if self.video_files:
            filename = os.path.basename(self.video_files[self.current_index])
            self.file_info.setText(f"File: {filename}\n({self.current_index + 1} of {len(self.video_files)})")
    
    def previous_video(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_video()
    
    def next_video(self):
        if self.current_index < len(self.video_files) - 1:
            self.current_index += 1
            self.load_current_video()
    
    def toggle_play(self):
        if self.timer.isActive():
            self.timer.stop()
            self.is_playing = False
        else:
            self.timer.start(33)  # ~30 fps
            self.is_playing = True
        self.update_ui()
    
    def save_tags(self):
        if self.video_files:
            current_file = self.video_files[self.current_index]
            self.tags[current_file] = self.tag_input.toPlainText()
            QMessageBox.information(self, "Saved", "Tags saved successfully!")
    
    def export_to_csv(self):
        if not self.tags:
            QMessageBox.warning(self, "No Tags", "No tags to export!")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Tags", "", "CSV Files (*.csv)")
        if file_path:
            data = {
                'file_path': list(self.tags.keys()),
                'tags': list(self.tags.values())
            }
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            QMessageBox.information(self, "Exported", "Tags exported successfully!")
    
    def update_ui(self):
        self.prev_button.setEnabled(self.current_index > 0)
        self.next_button.setEnabled(self.current_index < len(self.video_files) - 1)
        self.play_button.setEnabled(bool(self.video_files))
        self.save_button.setEnabled(bool(self.video_files))
        self.export_button.setEnabled(bool(self.tags))
        self.select_dir_button.setEnabled(True)  # Always enabled
        if self.is_playing:
            self.play_button.setText("Pause")
        else:
            self.play_button.setText("Play")
    
    def closeEvent(self, event):
        if self.video_capture is not None:
            self.video_capture.release()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoTagger()
    window.show()
    window.select_directory()  # Automatically prompt for directory selection
    sys.exit(app.exec()) 