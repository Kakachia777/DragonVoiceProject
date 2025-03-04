# Dragon Voice Project - User Guide

This comprehensive user guide provides detailed instructions for installing, configuring, and using the Dragon Voice Project with Dragon Medical One.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Dragon Medical One Integration](#dragon-medical-one-integration)
5. [Daily Usage](#daily-usage)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

## Introduction

The Dragon Voice Project is designed to enhance research efficiency for medical professionals by enabling voice-controlled multi-browser searching. This solution allows you to dictate a search query once and have it automatically typed into multiple browser windows, each potentially displaying different medical resources.

### Key Benefits

- **Time Efficiency**: Reduce the time needed to research medical information across multiple sources
- **Reduced Manual Typing**: Minimize repetitive typing of the same queries in different browser windows
- **Enhanced Workflow**: Maintain focus on patient care rather than technical interactions
- **Multiple Search Sources**: Query multiple medical databases and resources simultaneously
- **Voice Control**: Leverage your existing Dragon Medical One investment

## Installation

### System Requirements

- **Operating System**: Windows 10 or 11
- **Software**:
  - Python 3.6 or higher
  - Dragon Medical One 2025
  - Google Chrome browser
- **Hardware**:
  - Computer with sufficient RAM (minimum 8GB recommended)
  - Multiple monitors recommended (but not required)

### Installation Steps

1. **Set up Python** (if not already installed):
   - Download Python from [python.org](https://www.python.org/downloads/)
   - During installation, ensure "Add Python to PATH" is checked

2. **Get the Dragon Voice Project**:
   - Download or clone the repository to your local machine
   - Extract the files to a location of your choice (e.g., `C:\DragonVoiceProject`)

3. **Run the Setup Script**:
   - Open Command Prompt (CMD) or PowerShell
   - Navigate to the project directory:
     ```
     cd C:\path\to\DragonVoiceProject
     ```
   - Run the setup script:
     ```
     python src/setup.py
     ```
   - Follow the on-screen instructions to complete the installation

4. **Verify Installation**:
   - The setup script will perform basic functionality tests
   - Confirm that all components are working properly before proceeding

## Configuration

The Dragon Voice Project's behavior can be customized through the configuration file (`config.json`). This section explains all available settings.

### Using the Configuration Wizard

The easiest way to configure the system is through the setup script, which provides a guided wizard:

1. Run the setup script:
   ```
   python src/setup.py
   ```
2. When prompted, select "Yes" to modify the configuration
3. Follow the on-screen prompts to set your preferences

### Manual Configuration

For advanced users who prefer to edit the configuration file directly:

1. Open `src/config.json` in any text editor
2. Modify the settings as needed (see below for details)
3. Save the file

### Configuration Settings Explained

#### Integration Settings

```json
"integration": {
    "mode": "file",
    "file_path": "C:/dragon_query.txt",
    "polling_interval": 1.0,
    "command_prefix": "search for"
}
```

- **mode**: How Dragon output is monitored
  - `file`: Monitors a text file (recommended)
  - `clipboard`: Monitors clipboard content
- **file_path**: Path to the Dragon output file (only used in "file" mode)
- **polling_interval**: How often to check for new content (in seconds)
- **command_prefix**: Text prefix that triggers a search (e.g., "search for")

#### Browser Settings

```json
"browser": {
    "window_title_pattern": "Chrome",
    "typing_delay": 0.05,
    "window_switch_delay": 0.5
}
```

- **window_title_pattern**: Pattern to identify target browser windows
- **typing_delay**: Delay between keystrokes (seconds); increase if characters are missed
- **window_switch_delay**: Delay between switching windows (seconds)

#### Feedback Settings

```json
"feedback": {
    "audio_enabled": true,
    "popup_enabled": true,
    "log_queries": true,
    "log_file": "dragon_voice_queries.log"
}
```

- **audio_enabled**: Play a sound when a search is detected
- **popup_enabled**: Show a notification when a search is detected
- **log_queries**: Save detected queries to a log file
- **log_file**: Path to the log file

#### Advanced Settings

```json
"advanced": {
    "max_retries": 3,
    "retry_delay": 1.0,
    "search_timeout": 5.0
}
```

- **max_retries**: Number of times to retry a failed action
- **retry_delay**: Delay between retry attempts (seconds)
- **search_timeout**: Maximum time to wait for a search to complete

## Dragon Medical One Integration

This section explains how to configure Dragon Medical One to work with the Dragon Voice Project.

### File Output Method (Recommended)

The recommended method is to have Dragon Medical One save dictation to a text file:

1. **In Dragon Medical One**:
   - Open Dragon Medical One settings
   - Look for output options (consult Dragon Medical One documentation)
   - Configure it to save dictation to a text file
   - Set the file path to match your configuration (default: `C:/dragon_query.txt`)

2. **Test the Integration**:
   - Start Dragon Medical One
   - Dictate a test phrase that includes your command prefix
     - Example: "search for aspirin dosage guidelines"
   - Verify that the text appears in the specified file

### Clipboard Method (Alternative)

If the file method is not available, you can use the clipboard method:

1. **In Dragon Medical One**:
   - Configure Dragon to copy dictation to the clipboard
   - This might involve creating a custom command in Dragon

2. **In Dragon Voice Project**:
   - Set the `mode` in configuration to `clipboard`
   - Start the monitoring script

3. **Test the Integration**:
   - Dictate a test phrase with the command prefix
   - Verify that the system detects and processes the command

## Daily Usage

This section explains how to use the Dragon Voice Project in your daily workflow.

### Starting the System

There are three ways to start the Dragon Voice Project:

1. **Manual Start** (from Command Prompt/PowerShell):
   ```
   cd C:\path\to\DragonVoiceProject
   python src/dragon_monitor.py
   ```

2. **Using the Batch File**:
   - Double-click the `start_dragon_voice.bat` file created during setup

3. **Automatic Start** (if configured during setup):
   - The system will start automatically when you log in to Windows

### Preparing Your Browser Windows

For optimal use:

1. Open multiple Chrome windows (not just tabs)
2. Navigate each window to a different medical resource:
   - One for PubMed
   - One for UpToDate
   - One for your EHR system
   - Etc.
3. Arrange the windows across your screen(s) as desired

### Using Voice Commands

To perform a search:

1. Ensure the Dragon Voice Project is running
2. Use Dragon Medical One to dictate a command following this pattern:
   ```
   [command_prefix] [your search query]
   ```
   Example: "search for latest hypertension guidelines"

3. The system will:
   - Detect your command
   - Extract the search query
   - Type it into all open Chrome windows
   - Press Enter to execute the search in each window

### Best Practices

- **Clear Dictation**: Speak clearly, especially when saying the command prefix
- **Pausing**: Pause briefly after the command prefix
- **Query Length**: Keep search queries concise for best results
- **Window Arrangement**: Arrange windows so you can see all search results simultaneously

## Advanced Features

### Customizing the Command Prefix

You can change the command prefix to anything that suits your workflow:

1. Edit the configuration (using setup.py or directly)
2. Change the `command_prefix` value
3. Examples:
   - "lookup"
   - "find information on"
   - "research"

### Multiple Prefixes

To use multiple command prefixes:

1. Edit `dragon_monitor.py`
2. Find the function that checks for the command prefix
3. Modify it to check for multiple prefixes

### Custom Actions

Advanced users can extend the script to perform different actions:

1. Edit `dragon_monitor.py`
2. Add new functions for different actions
3. Modify the command detection to trigger different functions based on different prefixes

## Troubleshooting

### Common Issues and Solutions

#### System Not Detecting Commands

**Symptoms:**
- You dictate commands, but nothing happens

**Potential Solutions:**
1. **Check Monitoring Mode**:
   - Ensure the correct mode is selected in configuration (file or clipboard)
   
2. **Check Command Prefix**:
   - Verify you're using the exact command prefix specified in configuration
   - Check for unintended spaces or punctuation

3. **Check File Path**:
   - If using file mode, ensure the path in configuration matches where Dragon is saving output
   - Check file permissions

4. **Check Running Status**:
   - Ensure the dragon_monitor.py script is actually running
   - Look for any error messages in the terminal

#### Searches Not Working in Browsers

**Symptoms:**
- System detects commands but doesn't perform searches properly

**Potential Solutions:**
1. **Check Browser Windows**:
   - Ensure Chrome windows are open and visible
   - Verify the window title contains the pattern specified in configuration

2. **Adjust Typing Delay**:
   - If characters are missing, increase the `typing_delay` value

3. **Check Focus Issues**:
   - Ensure no dialogs or popups are stealing focus
   - Try clicking on a browser window before dictating

#### System Crashes

**Symptoms:**
- The script terminates unexpectedly

**Potential Solutions:**
1. **Check Logs**:
   - Look for error messages in the terminal
   - Check if any log files were created

2. **Update Packages**:
   - Run `pip install -U pygetwindow pyautogui pyperclip win10toast`
   - Restart the script

3. **Try Default Configuration**:
   - Reset to default configuration values

### Diagnostic Steps

If you encounter issues that aren't resolved by the above solutions:

1. **Enable Debug Mode**:
   - Edit `dragon_monitor.py`
   - Find the logging setup section
   - Set logging level to DEBUG

2. **Run in Verbose Mode**:
   - From command line: `python src/dragon_monitor.py --verbose`

3. **Check System Resources**:
   - Ensure your computer has adequate memory available
   - Close unnecessary applications

## FAQ

### General Questions

**Q: How many browser windows can the system control simultaneously?**
A: There's no hard limit, but performance may degrade with too many windows. Most users find 3-5 windows optimal.

**Q: Does this work with browsers other than Chrome?**
A: By default, it's configured for Chrome, but you can modify the `window_title_pattern` in the configuration to target other browsers.

**Q: Can I use this for non-medical searches?**
A: Absolutely! While designed for medical professionals, the system works for any search needs.

### Technical Questions

**Q: Does this modify my Dragon Medical One installation?**
A: No. The Dragon Voice Project only reads the output from Dragon Medical One; it doesn't modify or interfere with its operation.

**Q: Is the system listening to all my dictations?**
A: No. The system only processes text that contains the command prefix (e.g., "search for").

**Q: Will this work if I have multiple monitors?**
A: Yes, and multi-monitor setups are ideal for this system, as you can arrange multiple browser windows across screens.

**Q: Can I customize what keys are pressed after typing the query?**
A: Yes, but it requires modifying the code. By default, it presses Enter, but you could change this to any key combination.

### Support Questions

**Q: How do I get updates to the Dragon Voice Project?**
A: Check the project repository regularly for updates, or set up notifications if available.

**Q: What should I do if I find a bug?**
A: Document the issue with steps to reproduce, and report it through the appropriate channels for the project.

---

This user guide will be updated as new features are added or existing features are modified. For the latest information, check the project repository or documentation directory. 