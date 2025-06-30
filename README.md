# Enhanced Video Tagger

A comprehensive video tagging application built with PyQt6 that allows you to tag videos with structured metadata including people, key moments, locations, actions, camera movements, and shot types.

## Features

### 🎯 Structured Tagging Categories

1. **People Present** - List all people appearing in the video

   - Enter names separated by commas (e.g., "John, Jane, Mike")

2. **Key Moments** - Timestamp important events in the video

   - Use the "Add Current Time" button to automatically insert timestamps
   - Format: "00:15 - Introduction, 01:30 - Main event"

3. **Location Classes** - Categorize the video location

   - Predefined options: Indoor, Outdoor, Office, Home, Street, Park, etc.
   - Editable dropdown with custom location support

4. **Actions** - Describe what's happening in the video

   - Text input for custom actions
   - Quick checkboxes for common actions: Walking, Running, Sitting, Talking, etc.

5. **Camera Movement** - Specify camera motion

   - Options: Static, Pan Left/Right, Tilt Up/Down/Left/Right, Zoom In/Out, etc.
   - "Other" option with description field for custom movements

6. **Content Movement** - Describe movement of subjects/content in the video

   - Options: Static, Walking, Running, Sitting, Standing, Dancing, etc.
   - "Other" option with description field for custom content movements

7. **Shot Types** - Define the camera shot composition

   - Options: Close-Up, Medium Shot, Long Shot, Two Shot, etc.

8. **General Tags** - Additional free-form tags
   - For any other relevant information

### 🎬 Video Playback Features

- **Video Preview** - Thumbnail generation for quick preview
- **Playback Controls** - Play, pause, seek with progress slider
- **Navigation** - Previous/Next video buttons
- **Progress Tracking** - Visual progress bar for batch processing

### 💾 Data Management

- **Auto-Save** - Tags are automatically saved when navigating between videos
- **Visual Feedback** - Status indicator shows when tags are auto-saved
- **Unsaved Changes Indicator** - Save button changes color and shows asterisk (\*) when there are unsaved changes
- **Structured Export** - CSV export with separate columns for each category
- **Backward Compatibility** - Supports legacy tag format
- **Auto-save on Close** - Final changes are saved when closing the application
- **Batch Processing** - Process multiple videos in sequence

## Installation

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python video_tagger.py
   ```

## Usage

1. **Select Video Directory**

   - Click "Select Video Directory" to choose a folder containing video files
   - Supported formats: .mp4, .mov, .avi, .mkv, .wmv, .flv

2. **Tag Videos**

   - Navigate through videos using Previous/Next buttons
   - **Auto-save**: Tags are automatically saved when moving between videos
   - **Visual feedback**: Green status message appears when tags are auto-saved
   - **Unsaved indicator**: Save button turns orange with asterisk (\*) when there are unsaved changes
   - Fill in the structured tagging fields:
     - **People**: Enter names separated by commas
     - **Key Moments**: Use "Add Current Time" button while playing, then describe the moment
     - **Location**: Select from dropdown or type custom location
     - **Actions**: Check common actions or type custom ones
     - **Movement**: Select camera movement type (with "Other" option for custom descriptions)
     - **Content Movement**: Select movement of subjects/content (with "Other" option for custom descriptions)
     - **Shot Type**: Choose the shot composition
     - **General Tags**: Add any additional tags

3. **Save and Export**
   - Tags are auto-saved when navigating between videos
   - Click "Save Tags" to manually save current video's tags (optional)
   - Click "Export to CSV" to export all tags to a structured CSV file

## CSV Export Format

The exported CSV contains the following columns:

- `file_path` - Path to the video file
- `people` - List of people present
- `key_moments` - Timestamped key moments
- `location` - Location classification
- `actions` - Actions occurring in the video
- `movement` - Camera movement type
- `movement_description` - Description for custom camera movements
- `content_movement` - Movement of subjects/content in the video
- `content_movement_description` - Description for custom content movements
- `shot_type` - Shot composition type
- `general_tags` - Additional free-form tags

## UI Features

- **Resizable Panels** - Adjust video and tagging panel sizes
- **Scrollable Interface** - All tagging options accessible via scrolling
- **Visual Feedback** - Styled buttons and organized sections
- **Keyboard Navigation** - Tab through fields for efficient tagging

## Technical Details

- **Framework**: PyQt6 for the GUI
- **Video Processing**: OpenCV for thumbnail generation
- **Media Playback**: Qt Multimedia for video playback
- **Data Export**: Pandas for CSV generation
- **File Formats**: Supports multiple video formats

## Tips for Efficient Tagging

1. **Use the timestamp button** while watching videos to mark key moments
2. **Leverage checkboxes** for common actions to speed up tagging
3. **Be consistent** with location and shot type classifications
4. **Use the general tags** for any specific details not covered by structured fields
5. **Save frequently** to avoid losing work

## Requirements

- Python 3.7+
- PyQt6
- OpenCV
- Pandas
- Qt Multimedia support

## License

This project is open source and available under the MIT License.
