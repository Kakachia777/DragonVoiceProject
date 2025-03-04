# Dragon Voice Project - Quick Reference Guide

## Getting Started

### Installation
```
python src/setup.py
```

### Start the System
```
python src/dragon_monitor.py
```
Or double-click `start_dragon_voice.bat`

## Voice Commands

Basic pattern:
```
[command_prefix] [your search query]
```

Example:
```
"search for hypertension treatment guidelines"
```

## Configuration File Location
```
DragonVoiceProject/src/config.json
```

## Common Settings

| Setting | Description | Default |
|---------|-------------|---------|
| mode | Input method (file/clipboard) | file |
| file_path | Path to Dragon output file | C:/dragon_query.txt |
| command_prefix | Trigger phrase | "search for" |
| window_title_pattern | Browser window identifier | "Chrome" |
| typing_delay | Delay between keystrokes | 0.05 seconds |

## Quick Troubleshooting

### System Not Detecting Commands
1. Is the monitor script running?
2. Are you using the correct command prefix?
3. Is Dragon correctly outputting to file/clipboard?

### Searches Not Working
1. Are Chrome windows open and visible?
2. Does window title contain "Chrome"?
3. Try increasing typing_delay if characters are missed

### System Crashes
1. Check terminal for error messages
2. Try updating packages:
   ```
   pip install -U pygetwindow pyautogui pyperclip win10toast
   ```
3. Reset to default configuration

## Best Practices

1. **Clear Dictation**: Speak clearly, especially the command prefix
2. **Browser Setup**: Open separate windows (not just tabs)
3. **Multiple Monitors**: Arrange windows across screens
4. **Test First**: Try simple queries before critical use

## Need More Help?

See the full user guide:
```
DragonVoiceProject/docs/user_guide.md
``` 