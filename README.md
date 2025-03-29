# Dragon Voice Assistant

A powerful voice assistant that transcribes your speech and sends it to multiple chatbots simultaneously.

## Features

- **Modern, User-Friendly Interface**: Clean, card-based design with intuitive controls
- **Voice Transcription**: Record your voice and instantly transcribe it
- **Multi-Chatbot Support**: Send transcribed text to multiple AI chatbots at once
- **Clipboard Integration**: Paste text from clipboard directly to chatbots
- **Audio Device Selection**: Choose your preferred recording device
- **Customizable Settings**: Adjust gain, enable/disable features, and more

## Computer A vs Computer B

This project provides two separate executables:

- **DragonVoiceA.exe**: Uses `Dragon_cli2.py` with a green-themed UI
- **DragonVoiceB.exe**: Uses `dragon_cli.py` with a blue-themed UI

Both applications have the same functionality but are designed to be run on different computers for specialized workflows.

## Building the Executables

### Option 1: Using the Python Script (Recommended)

1. Make sure you have Python 3.8+ installed
2. Run the build script:
   ```
   python build_pyinstaller.py
   ```
3. The script will:
   - Install required dependencies
   - Clean existing build files
   - Build both executables
   - Create output folders with all necessary files
   - Generate ZIP files for easy distribution

### Option 2: Using Windows Batch File

1. Double-click `build_executables.bat` to run the batch file
2. Follow the on-screen instructions

### Option 3: Manual Build

If you prefer to build manually:

1. Install PyInstaller: `pip install pyinstaller`
2. Build Computer A:
   ```
   pyinstaller --name=DragonVoiceA --onefile --noconsole --icon=dragon_icon.ico --add-data=dragon_icon.ico;. --add-data=config.json;. dragon_gui_minimal_a.py
   ```
3. Build Computer B:
   ```
   pyinstaller --name=DragonVoiceB --onefile --noconsole --icon=dragon_icon.ico --add-data=dragon_icon.ico;. --add-data=config.json;. dragon_gui_minimal_b.py
   ```
4. Create output directories and copy necessary files

## Using the Application

1. Extract the ZIP file for your computer (A or B)
2. Double-click the executable (`DragonVoiceA.exe` or `DragonVoiceB.exe`)
3. Use the buttons to:
   - **Record Voice**: Click to start recording, speak, and wait for transcription
   - **Quick Mode**: Record and send to chatbots in one step
   - **Paste from Clipboard**: Send clipboard content to chatbots
   - **Retry Failed**: Retry sending to any chatbots that failed
   - **Settings**: Configure audio device, gain, and other options

### Pinning to Taskbar

For quick access, you can pin the application to your Windows taskbar:

1. Right-click the shortcut file (`.lnk`) from the build output or desktop
2. Select "Pin to taskbar" from the context menu
3. The application will now be available directly from your taskbar

Alternatively, if you've already run the application:
1. Right-click the application icon in the taskbar
2. Select "Pin to taskbar"

### Keyboard Shortcuts

- **F9**: Start recording
- **F10**: Quick mode (record and send)

## Chatbot Configuration

### Setting Chatbot Input Coordinates

In the configuration file, you can specify coordinates for your chatbots:

```json
"chatbot_input": {
    "enabled": true,
    "delay_between_inputs": 0.5,
    "coordinates": [
        {
            "name": "Chatbot A",
            "x": 1000,
            "y": 500,
            "post_wait": 0.5
        },
        {
            "name": "Chatbot B",
            "x": 1200,
            "y": 600,
            "key_press": "enter",
            "post_wait": 0.5
        },
        {
            "name": "Chatbot C",
            "x": 1500,
            "y": 700,
            "key_press": ["shift", "enter"],
            "post_wait": 0.5
        }
    ]
}
```

### Coordinate Options

Each chatbot entry in the coordinates array supports these options:

- **name**: A descriptive name for the chatbot (for logs)
- **x, y**: Screen coordinates where to click (required)
- **post_wait**: Time to wait after all actions (default: 0.5s)
- **press_enter**: Whether to press Enter after pasting (default: true)
- **key_press**: Custom key or key combination to press after pasting:
  - Single key: `"key_press": "enter"` or `"key_press": "tab"`
  - Key combination: `"key_press": ["ctrl", "enter"]` or `"key_press": ["shift", "enter"]`
- **post_clicks**: Additional clicks to perform after the main actions:
  ```json
  "post_clicks": [
      {"x": 1050, "y": 550, "delay": 1.0}
  ]
  ```

## Troubleshooting

If you encounter issues:

1. **Missing dependencies**: Run `pip install -r requirements.txt`
2. **Audio device issues**: Select a different audio device in Settings
3. **Chatbot coordination issues**: Use the Calibrate button in Settings to set up chatbot coordinates
4. **Application crashes**: Check the console output for error messages

## Requirements

- Python 3.8+ (for building)
- Windows 10/11
- Microphone for voice input 