#!/usr/bin/env python3
"""
Updated Dragon Voice GUI with improved voice command and transcription handling
"""

from whisper_integration import WhisperRecognizer
from voice_command_handler import VoiceCommandHandler
from transcription_handler import TranscriptionHandler
import os
import sys
import json
import time
import logging
import webbrowser
import threading
from datetime import datetime
from pathlib import Path

# GUI libraries
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

# System monitoring
import psutil
import platform

# Window management
import pygetwindow as gw
import pyautogui
import sounddevice as sd
import numpy as np
import tempfile

# Custom components
from synthesizer_bar import SynthesizerBar

# Try to import soundfile, but don't fail if it's not available
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("Warning: soundfile module not found. Some audio features will be limited.")

# Constants
DEFAULT_CONFIG_PATH = "src/config.json"

class DragonVoiceGUI:
    """
    Main GUI class for the Dragon Voice Project with improved voice command
    and transcription handling.
    """

    def __init__(self, config_path=DEFAULT_CONFIG_PATH):
        """Initialize the DragonVoice GUI application"""
        logging.info("Initializing DragonVoiceGUI")

        try:
            # Initialize logging
            self.setup_logging()

            # Initialize state variables
            self.recording_active = False
            self.continuous_recording = False
            self.is_fullscreen = False

            # Create main application window
            self.app = ctk.CTk()
            self.app.title("DragonVoice")
            self.app.geometry("1200x800")
            self.app.minsize(900, 600)

            # Load configuration
            self.config_path = config_path
            self.config = self.load_config()
            logging.info(f"Configuration loaded from {config_path}")

            # Set up theme and colors
            self.setup_theme()

            # Initialize Whisper recognizer
            self.init_whisper_recognizer()

            # Set up UI components
            self.setup_ui()

            # Start system monitoring
            self.start_system_monitoring()

        except Exception as e:
            logging.error(f"Error initializing DragonVoiceGUI: {str(e)}")
            raise

    def create_dashboard_tab(self):
        """Create the dashboard tab content with improved handlers"""
        # Create scrollable main container
        dashboard_container = ctk.CTkScrollableFrame(
            self.tab_view.tab("Dashboard"),
            fg_color="transparent"
        )
        dashboard_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Configure grid layout
        dashboard_container.columnconfigure(0, weight=2)
        dashboard_container.columnconfigure(1, weight=1)

        # Status panel (top left)
        status_panel = self.create_status_panel(dashboard_container)
        status_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))

        # Voice assistant control panel (top right)
        control_panel = self.create_voice_control_panel(dashboard_container)
        control_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=(0, 10))

        # Voice Commands section (middle)
        self.voice_command_handler = VoiceCommandHandler(dashboard_container, self.colors, self.fonts)
        commands_frame = self.voice_command_handler.get_frame()
        commands_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 10))

        # Transcription section (bottom)
        self.transcription_handler = TranscriptionHandler(
            dashboard_container, 
            self.colors, 
            self.fonts,
            on_enter_callback=self.process_transcription
        )
        transcription_frame = self.transcription_handler.get_frame()
        transcription_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(0, 10))

    def transcribe_last_recording(self):
        """Transcribe the last recording and update displays"""
        if not hasattr(self, 'whisper_recognizer'):
            self.update_status("Whisper recognizer not initialized", log_level="error")
            return None

        try:
            # Save audio to file
            audio_file = self.whisper_recognizer.save_audio_to_file()
            if not audio_file:
                self.update_status("No audio data to transcribe", log_level="warning")
                return None

            # Transcribe audio
            self.update_status("Transcribing audio...", log_level="info")
            transcript = self.whisper_recognizer.transcribe_audio(
                audio_file,
                language="en",
                response_format="verbose_json"
            )

            if transcript:
                self.update_status(f"Transcription successful", log_level="info")
                
                # Update the transcription display
                if hasattr(self, 'transcription_handler'):
                    self.transcription_handler.update_transcription(transcript.text)

                # Add to voice commands display
                if hasattr(self, 'voice_command_handler'):
                    self.voice_command_handler.handle_command(transcript.text)

                # Automatically start recording again for continuous voice command recognition
                if hasattr(self, 'continuous_recording') and self.continuous_recording:
                    self.app.after(1000, self.start_manual_recording)

                return transcript.text
            else:
                self.update_status("Transcription failed", log_level="error")
                return None

        except Exception as e:
            self.update_status(f"Transcription error: {str(e)}", log_level="error")
            return None

    def process_transcription(self, text):
        """Process transcribed text and send to chatbots"""
        try:
            # Send to active chatbot(s)
            self.send_to_chatbots(text)
            
            # Update status
            self.update_status("Text sent to chatbots", log_level="info")

        except Exception as e:
            self.update_status(f"Error processing transcription: {str(e)}", log_level="error")

    def send_to_chatbots(self, text):
        """Send text to active chatbots"""
        # This is a placeholder - implement actual chatbot communication
        logging.info(f"Sending text to chatbots: {text}")
        # You would implement the actual chatbot communication here
        pass

    # ... rest of the DragonVoiceGUI class implementation ... 