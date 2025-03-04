# Dragon Voice Project

A voice-controlled multi-browser query system designed to enhance research efficiency with Dragon Medical One.

## Overview

The Dragon Voice Project lets medical professionals voice-control multiple browser windows simultaneously, sending the same search query to different medical research sites, databases, or EHRs across multiple screens. This dramatically speeds up medical information retrieval by replacing manual typing and window switching.

## Features

- **Voice-Activated Searches**: Using voice commands to trigger searches across multiple browsers
- **Multi-Browser Control**: Simultaneously query different medical resources
- **Flexible Integration**: Works with either text file or clipboard monitoring methods
- **Customizable Configuration**: Easy-to-edit configuration file for system preferences
- **Visual Feedback**: Optional notifications when searches are detected and processed
- **Automatic Startup**: Optional system startup integration

## Requirements

- Windows 10/11
- Python 3.6 or higher
- Dragon Medical One 2025
- Google Chrome browser
- Required Python packages (installed automatically by setup.py):
  - pygetwindow
  - pyautogui
  - pyperclip
  - win10toast

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Run the setup script:

```
python src/setup.py
```

The setup script will:
- Check and install required dependencies
- Create and configure the necessary files
- Test the system components
- Set up autostart (optional)

## Configuration

The system can be configured through the setup process or by directly editing the `config.json` file, which includes settings for:

### Integration Settings
- `mode`: Input monitoring method ("file" or "clipboard")
- `file_path`: Path to the Dragon output file (when in "file" mode)
- `polling_interval`: How often to check for new content (in seconds)
- `command_prefix`: Text prefix that triggers a search (e.g., "search for")

### Browser Settings
- `window_title_pattern`: Browser window title pattern to identify target windows
- `typing_delay`: Delay between keystrokes when typing (in seconds)
- `window_switch_delay`: Delay between switching windows (in seconds)

### Feedback Settings
- `audio_enabled`: Enable/disable audio feedback
- `popup_enabled`: Enable/disable popup notifications
- `log_queries`: Enable/disable query logging
- `log_file`: Path to the log file for queries

## Usage

### Setting Up Dragon Medical One

#### File Output Method (Recommended)
1. In Dragon Medical One, configure it to output dictation to a text file:
   - The default path is `C:/dragon_query.txt`, but this can be changed in the configuration
   - You may need to consult Dragon Medical One's documentation for specific instructions

#### Clipboard Method (Alternative)
1. Configure Dragon Medical One to copy dictation to clipboard
2. Set the monitoring mode to "clipboard" in the configuration

### Running the System

After setup, you can start the system by:

1. Running the script directly:
   ```
   python src/dragon_monitor.py
   ```
2. Using the batch file or shortcut created during setup

### Using Voice Commands

Once the system is running:

1. Open multiple Chrome browser windows (one per resource you want to search)
2. Say your command prefix followed by your search query:
   ```
   "search for hypertension treatment guidelines"
   ```
3. The system will automatically:
   - Detect your query
   - Type it into all open Chrome windows
   - Press Enter to execute the search in each window

## Testing

You can test the basic functionality without Dragon Medical One by:

1. Running the quick test script:
   ```
   python src/quick_test.py
   ```
2. Following the on-screen instructions

## Troubleshooting

### Common Issues

- **No searches being triggered**:
  - Check that Dragon Medical One is correctly outputting to the text file or clipboard
  - Verify that you're using the correct command prefix
  - Check the configuration settings in `config.json`

- **Searches triggered but not executing in browsers**:
  - Ensure Chrome windows are open and visible
  - Check that the window title pattern in configuration matches your Chrome windows
  - Try increasing the typing delay if characters are being missed

- **System crashes or freezes**:
  - Check the error log for details
  - Ensure all required packages are installed
  - Try running with default configuration settings

### Support

For additional help, please refer to the documentation or contact the support team.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Dragon Medical One by Nuance Communications
- Python community for the excellent libraries used in this project