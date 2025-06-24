# Video Tagger

A simple application for tagging video files with text descriptions. The application allows you to:

- Browse through video files in a directory
- View video previews in low resolution for better performance
- Add text tags to videos
- Export tags to CSV format

## Features

- Safe file handling (read-only, no modifications to original files)
- Low-resolution video preview for better performance
- Simple and intuitive interface
- Support for common video formats (mp4, mov, avi, mkv)
- Export tags to CSV with file paths
- Progress tracking
- Play/pause video preview

## Installation

1. Make sure you have Python 3.8 or later installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:

   ```bash
   python video_tagger.py
   ```

2. When the application starts, it will prompt you to select a directory containing video files
3. Use the interface to:
   - Navigate between videos using Previous/Next buttons
   - Play/Pause the video preview
   - Enter tags in the text box
   - Save tags for the current video
   - Export all tags to CSV when finished

## Interface

- **Left Panel**: Video preview and navigation controls

  - Video preview window
  - Previous/Next buttons
  - Play/Pause button
  - Progress bar

- **Right Panel**: Tagging interface
  - Current file information
  - Tag input text box
  - Save Tags button
  - Export to CSV button

## Notes

- The application only reads video files and never modifies them
- Video previews are shown in low resolution (640x480) for better performance
- Tags are stored in memory until exported to CSV
- Make sure to save tags for each video before moving to the next one
- The CSV export includes both file paths and their associated tags
