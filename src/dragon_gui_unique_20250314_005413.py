#!/usr/bin/env python3
"""
Dragon Voice GUI - Main application interface for Dragon Voice Project
"""

from whisper_integration import WhisperRecognizer
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
import os
import time
import threading

# Custom components
from synthesizer_bar import SynthesizerBar

# Try to import soundfile, but don't fail if it's not available
try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("Warning: soundfile module not found. Some audio features will be limited.")

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Changed from INFO to WARNING
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("dragon_gui.log"),
        logging.StreamHandler()
    ]
)

# Constants
DEFAULT_CONFIG_PATH = "src/config.json"
ASSETS_DIR = os.path.join("src", "assets")

# Add Whisper integration




class DragonVoiceGUI:
    """
    Main GUI class for the Dragon Voice Project

    Provides a modern, feature-rich interface for controlling the voice assistant,
    managing chatbots, and configuring system settings.
    """



















        def draw_gradient():
            width = self.header_canvas.winfo_width()
            if width <= 1:  # Not yet properly initialized
                self.app.after(100, draw_gradient)
                return

            height = 90
            # Create a more sophisticated gradient
            for i in range(width):
                # Calculate gradient position (0 to 1)
                pos = i / width

                # Create a gradient with accent color highlights
                if pos < 0.2:  # First section - dark to medium with accent hint
                    ratio = pos / 0.2
                    r1, g1, b1 = self.hex_to_rgb(self.colors["bg_dark"])
                    r2, g2, b2 = self.hex_to_rgb(self.colors["bg_medium"])
                    r3, g3, b3 = self.hex_to_rgb(self.colors["accent_primary"])

                    # Mix colors with a hint of accent
                    r = r1 + (r2 - r1) * ratio + (r3 - r1) * ratio * 0.1
                    g = g1 + (g2 - g1) * ratio + (g3 - g1) * ratio * 0.1
                    b = b1 + (b2 - b1) * ratio + (b3 - b1) * ratio * 0.1
                elif pos < 0.8:  # Middle section - medium to medium with subtle variation
                    ratio = (pos - 0.2) / 0.6
                    r1, g1, b1 = self.hex_to_rgb(self.colors["bg_medium"])
                    r2, g2, b2 = self.hex_to_rgb(
                        self._adjust_color_brightness(
                            self.colors["bg_medium"], 1.1))

                    r = r1 + (r2 - r1) * ratio
                    g = g1 + (g2 - g1) * ratio
                    b = b1 + (b2 - b1) * ratio
                else:  # Last section - medium to dark with accent hint
                    ratio = (pos - 0.8) / 0.2
                    r1, g1, b1 = self.hex_to_rgb(self.colors["bg_medium"])
                    r2, g2, b2 = self.hex_to_rgb(self.colors["bg_dark"])
                    r3, g3, b3 = self.hex_to_rgb(
                        self.colors["accent_secondary"])

                    # Mix colors with a hint of accent
                    r = r1 + (r2 - r1) * ratio + (r3 - r1) * ratio * 0.1
                    g = g1 + (g2 - g1) * ratio + (g3 - g1) * ratio * 0.1
                    b = b1 + (b2 - b1) * ratio + (b3 - b1) * ratio * 0.1

                color = f'#{int(r):02x}{int(g):02x}{int(b):02x}'
                self.header_canvas.create_line(i, 0, i, height, fill=color)

            # Add accent line at bottom with glow effect
            for i in range(3):
                alpha = 0.3 + (0.7 * (i / 2))  # Increasing opacity
                glow_color = self._adjust_color_brightness(
                    self.colors["accent_primary"], alpha)
            self.header_canvas.create_line(
                0, height - 3 + i, width, height - 3 + i,
                fill=glow_color,
                width=1
            )

        # Schedule gradient drawing
        self.app.after(100, draw_gradient)

        # Create a container for the header content
        header_content = ctk.CTkFrame(
            self.header_frame, fg_color="transparent")
        header_content.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            relwidth=1,
            relheight=0.8)

        # Left side - Logo and title
        logo_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        logo_frame.pack(side="left", padx=(30, 0))

        # Try to load logo image if available
        try:
            logo_path = os.path.join("src", "assets", "dragon_logo.png")
            if os.path.exists(logo_path):
                logo_image = ctk.CTkImage(
                    light_image=Image.open(logo_path),
                    dark_image=Image.open(logo_path),
                    size=(40, 40)
                )
                logo_label = ctk.CTkLabel(
                    logo_frame,
                    image=logo_image,
                    text=""
                )
                logo_label.pack(side="left", padx=(0, 15))
        except Exception as e:
            logging.error(f"Failed to load logo: {str(e)}")

        # App title with modern styling
        title_label = ctk.CTkLabel(
            logo_frame,
            text="DragonVoice",
            font=self.fonts["header"],
            text_color=self.colors["text_bright"]
        )
        title_label.pack(side="left")

        # Version with pill background
        version_pill = ctk.CTkFrame(
            logo_frame,
            fg_color=self.colors["accent_primary"],
            corner_radius=12,
            height=24
        )
        version_pill.pack(side="left", padx=(10, 0), pady=(8, 0))

        version_label = ctk.CTkLabel(
            version_pill,
            text="v2.0",
            font=self.fonts["small"],
            text_color=self.colors["text_bright"]
        )
        version_label.pack(padx=10, pady=2)

        # Center - Status indicator
        status_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        status_frame.pack(side="left", expand=True)

        # Right side - Controls
        controls_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        controls_frame.pack(side="right", padx=(0, 30))

        # Microphone selector with improved styling
        mic_frame = ctk.CTkFrame(
            controls_frame,
            fg_color=self.colors["bg_light"],
            corner_radius=8
        )
        mic_frame.pack(side="left", padx=(0, 15), pady=5)

        mic_label = ctk.CTkLabel(
            mic_frame,
            text="Microphone:",
            font=self.fonts["small"],
            text_color=self.colors["text_normal"]
        )
        mic_label.pack(side="left", padx=(10, 5), pady=5)

        # Microphone dropdown
        self.mic_var = ctk.StringVar(value="Default Microphone")
        self.mic_dropdown = ctk.CTkOptionMenu(
            mic_frame,
            values=["Default Microphone"],
            variable=self.mic_var,
            width=150,
            dynamic_resizing=True,
            fg_color=self.colors["bg_medium"],
            button_color=self.colors["accent_primary"],
            button_hover_color=self.colors["accent_secondary"],
            dropdown_fg_color=self.colors["bg_medium"]
        )
        self.mic_dropdown.pack(side="left", padx=(0, 10), pady=5)

        # Theme toggle button
        theme_button = ctk.CTkButton(
            controls_frame,
            text="",
            width=36,
            height=36,
            corner_radius=10,
            fg_color=self.colors["bg_light"],
            hover_color=self.colors["accent_primary"],
            text_color=self.colors["text_bright"],
            command=self.toggle_theme
        )
        theme_button.pack(side="left", padx=(0, 10))

        # Settings button
        settings_button = ctk.CTkButton(
            controls_frame,
            text="Settings",
            width=100,
            height=36,
            corner_radius=10,
            fg_color=self.colors["bg_light"],
            hover_color=self.colors["accent_primary"],
            text_color=self.colors["text_bright"],
            command=self.show_settings
        )
        settings_button.pack(side="left", padx=(0, 10))

        # Help button
        help_button = ctk.CTkButton(
            controls_frame,
            text="Help",
            width=80,
            height=36,
            corner_radius=10,
            fg_color=self.colors["bg_light"],
            hover_color=self.colors["accent_primary"],
            text_color=self.colors["text_bright"],
            command=self.show_help
        )
        help_button.pack(side="left")

        # Refresh microphone list
        self.refresh_mic_list()





















        def update_sensitivity(*args):
            self.sensitivity_value.configure(text=f"{int(self.sensitivity_var.get() * 100)}%")
            if hasattr(self, 'gain_var'):
                self.gain_var.set(self.sensitivity_var.get())

        self.sensitivity_var.trace_add("write", update_sensitivity)
        
        # Initialize gain variable for level meter
        self.gain_var = ctk.DoubleVar(value=self.sensitivity_var.get())

        # Status indicator with improved styling
        status_frame = ctk.CTkFrame(
            control_panel,
            fg_color=self.colors["bg_light"],
            corner_radius=10,
            height=50
        )
        status_frame.pack(fill="x", padx=20, pady=10)
        status_frame.pack_propagate(False)

        status_label = ctk.CTkLabel(
            status_frame,
            text="Status: Idle",
            font=self.fonts["normal"],
            text_color=self.colors["text_normal"]
        )
        status_label.pack(side="left", padx=15, pady=10)

        self.status_indicator = ctk.CTkFrame(
            status_frame,
            fg_color=self.colors["status_gray"],
            width=20,
            height=20,
            corner_radius=10
        )
        self.status_indicator.pack(side="right", padx=15)

        # Add text display window for pronounced text
        text_display_frame = ctk.CTkFrame(
            dashboard_container,
            fg_color=self.colors["bg_medium"],
            corner_radius=15,
            border_width=1,
            border_color=self.colors["bg_light"]
        )
        text_display_frame.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="nsew",
            pady=(
                5,
                5))  # Reduced top padding from 10 to 5 and added bottom padding of 5

        # Text display header
        text_display_header = ctk.CTkFrame(
            text_display_frame, fg_color="transparent", height=50)
        text_display_header.pack(fill="x", padx=20, pady=(15, 5))

        text_display_title = ctk.CTkLabel(
            text_display_header,
            text="Voice Commands",
            font=self.fonts["title"],
            text_color=self.colors["text_bright"]
        )
        text_display_title.pack(side="left")

        # Clear button
        clear_button = ctk.CTkButton(
            text_display_header,
            text="Clear",
            command=lambda: self.text_display.configure(
                state="normal") or self.text_display.delete(
                1.0,
                "end") or self.text_display.configure(
                state="disabled"),
            fg_color=self.colors["accent_secondary"],
            hover_color=self._adjust_color_brightness(
                self.colors["accent_secondary"],
                0.8),
            width=80,
            corner_radius=8,
            font=self.fonts["small"])
        clear_button.pack(side="right")

        # Text display area
        self.text_display = ctk.CTkTextbox(
            text_display_frame,
            fg_color=self.colors["bg_light"],
            text_color=self.colors["text_bright"],
            font=self.fonts["large"],
            corner_radius=10,
            border_width=1,
            border_color=self.colors["bg_light"],
            height=120  # Reduced height from 150 to 120
        )
        self.text_display.pack(fill="both", expand=True, padx=20, pady=(5, 10))  # Reduced bottom padding from 20 to 10

        # Configure text tags for formatting - access the underlying Tkinter
        # Text widget
        self.text_display._textbox.tag_configure(
            "timestamp", foreground=self.colors["accent_secondary"])
        self.text_display._textbox.tag_configure(
            "command", foreground=self.colors["text_bright"])
        self.text_display._textbox.tag_configure(
            "system", foreground=self.colors["status_blue"])
            
        # Add transcription section (new)
        transcription_frame = ctk.CTkFrame(
            dashboard_container,
            fg_color=self.colors["bg_medium"],
            corner_radius=15,
            border_width=1,
            border_color=self.colors["bg_light"]
        )
        transcription_frame.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="nsew",
            pady=(5, 0)  # Reduced top padding from 10 to 5
        )
        
        # Transcription header
        transcription_header = ctk.CTkFrame(
            transcription_frame, fg_color="transparent", height=50)
        transcription_header.pack(fill="x", padx=20, pady=(10, 5))  # Reduced top padding from 15 to 10
        
        transcription_title = ctk.CTkLabel(
            transcription_header,
            text="Transcribed Text",
            font=self.fonts["title"],
            text_color=self.colors["text_bright"]
        )
        transcription_title.pack(side="left")
        
        # Clear transcription button
        clear_transcription_button = ctk.CTkButton(
            transcription_header,
            text="Clear",
            command=lambda: self.transcription_display.configure(
                state="normal") or self.transcription_display.delete(
                1.0,
                "end") or self.transcription_display.configure(
                state="disabled"),
            fg_color=self.colors["accent_secondary"],
            hover_color=self._adjust_color_brightness(
                self.colors["accent_secondary"],
                0.8),
            width=80,
            corner_radius=8,
            font=self.fonts["small"]
        )
        clear_transcription_button.pack(side="right")
        
        # Transcription display area
        self.transcription_display = ctk.CTkTextbox(
            transcription_frame,
            fg_color=self.colors["bg_light"],
            text_color=self.colors["text_bright"],
            font=self.fonts["large"],
            corner_radius=10,
            border_width=1,
            border_color=self.colors["bg_light"],
            height=120  # Reduced height from 150 to 120
        )
        self.transcription_display.pack(fill="both", expand=True, padx=20, pady=(5, 10))
        
        # Enter button container
        enter_button_frame = ctk.CTkFrame(
            transcription_frame,
            fg_color="transparent"
        )
        enter_button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Enter button
        self.enter_button = ctk.CTkButton(
            enter_button_frame,
            text="Enter",
            command=self.process_transcription,
            fg_color=self.colors["accent_primary"],
            hover_color=self._adjust_color_brightness(
                self.colors["accent_primary"],
                0.8),
            height=40,
            corner_radius=10,
            font=self.fonts["subtitle"],
            state="disabled"  # Initially disabled until transcription is available
        )
        self.enter_button.pack(side="right", padx=(10, 0))

        # Quick settings with improved styling
        settings_frame = ctk.CTkFrame(
            control_panel,
            fg_color=self.colors["bg_light"],
            corner_radius=10
        )
        settings_frame.pack(fill="x", padx=20, pady=10)

        # Microphone sensitivity with improved styling
        sensitivity_label = ctk.CTkLabel(
            settings_frame,
            text="Microphone Sensitivity",
            font=self.fonts["normal"],
            text_color=self.colors["text_normal"]
        )
        sensitivity_label.pack(anchor="w", padx=15, pady=(15, 5))

        sensitivity_frame = ctk.CTkFrame(
            settings_frame, fg_color="transparent")
        sensitivity_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.sensitivity_var = ctk.DoubleVar(value=0.5)
        sensitivity_slider = ctk.CTkSlider(
            sensitivity_frame,
            from_=0.1,
            to=1.0,
            variable=self.sensitivity_var,
            width=200,
            progress_color=self.colors["accent_primary"],
            button_color=self.colors["accent_secondary"],
            button_hover_color=self.colors["accent_primary"]
        )
        sensitivity_slider.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(
                0,
                10))

        sensitivity_value = ctk.CTkLabel(
            sensitivity_frame,
            text=f"{int(self.sensitivity_var.get() * 100)}%",
            font=self.fonts["small"],
            width=40,
            text_color=self.colors["text_dim"]
        )
        sensitivity_value.pack(side="right")

        # Update sensitivity value when slider changes
        def update_sensitivity(*args):
            sensitivity_value.configure(
                text=f"{int(self.sensitivity_var.get() * 100)}%")
            # Also update the gain for the level meter
            if hasattr(self, 'gain_var'):
                self.gain_var.set(self.sensitivity_var.get())

        self.sensitivity_var.trace_add("write", update_sensitivity)

        # Initialize gain variable for level meter
        self.gain_var = ctk.DoubleVar(value=self.sensitivity_var.get())

        # Initialize monitor visualization
        self.app.after(500, self.refresh_monitor_visualization)












        def open_link(url):
            import webbrowser
            webbrowser.open(url)

        # Website link
        website_button = ctk.CTkButton(
            links_frame,
            text="Visit Website",
            command=lambda: open_link("https://dragonvoice.ai"),
            fg_color=self.colors["accent_primary"],
            hover_color=self.colors["accent_secondary"]
        )
        website_button.pack(anchor="w", padx=20, pady=5)

        # Documentation link
        docs_button = ctk.CTkButton(
            links_frame,
            text="Documentation",
            command=lambda: open_link("https://docs.dragonvoice.ai"),
            fg_color=self.colors["accent_primary"],
            hover_color=self.colors["accent_secondary"]
        )
        docs_button.pack(anchor="w", padx=20, pady=5)

        # GitHub link
        github_button = ctk.CTkButton(
            links_frame,
            text="GitHub Repository",
            command=lambda: open_link("https://github.com/dragonvoice/dragonvoice"),
            fg_color=self.colors["accent_primary"],
            hover_color=self.colors["accent_secondary"])
        github_button.pack(anchor="w", padx=20, pady=(5, 15))















        def add_chatbot():
            name = name_entry.get()
            chatbot_type = type_var.get()
            api_key = api_key_entry.get()

            if name and chatbot_type and api_key:
                # Add to config
                if "chatbots" not in self.config:
                    self.config["chatbots"] = {}

                self.config["chatbots"][name] = {
                    "type": chatbot_type,
                    "api_key": api_key,
                    "status": "Ready",
                    "color": self.colors["accent_primary"],
                    "icon": "🤖"
                }

                self.save_configuration()
                self.refresh_chatbot_list()
                dialog.destroy()
            else:
                # Show error
                error_label.configure(text="Please fill in all fields")

        add_button = ctk.CTkButton(
            dialog,
            text="Add Chatbot",
            command=add_chatbot,
            fg_color=self.colors["accent_primary"],
            hover_color=self.colors["accent_secondary"]
        )
        add_button.pack(anchor="center", pady=20)

        # Error label
        error_label = ctk.CTkLabel(
            dialog,
            text="",
            text_color=self.colors["error"]
        )
        error_label.pack(anchor="center")









        def on_enter(e):
            item.configure(fg_color=self.colors["bg_light"])

        def on_leave(e):
            item.configure(fg_color=self.colors["bg_dark"])

        item.bind("<Enter>", on_enter)
        item.bind("<Leave>", on_leave)

        # Icon and name container
        info_frame = ctk.CTkFrame(
            item,
            fg_color="transparent"
        )
        info_frame.pack(side="left", fill="y", padx=10)

        # Icon with colored background
        icon_frame = ctk.CTkFrame(
            info_frame,
            fg_color=config.get("color", self.colors["accent_primary"]),
            width=40,
            height=40,
            corner_radius=20
        )
        icon_frame.pack(side="left", padx=(0, 10))
        icon_frame.pack_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_frame,
            text=config.get("icon", "🤖"),
            font=ctk.CTkFont(size=20)
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        # Name and type
        text_frame = ctk.CTkFrame(
            info_frame,
            fg_color="transparent"
        )
        text_frame.pack(side="left", fill="y")

        name_label = ctk.CTkLabel(
            text_frame,
            text=name,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors["text_bright"]
        )
        name_label.pack(anchor="w")

        type_label = ctk.CTkLabel(
            text_frame,
            text=config.get("type", "Unknown"),
            font=ctk.CTkFont(size=12),
            text_color=self.colors["text_dim"]
        )
        type_label.pack(anchor="w")

        # Status indicator
        status_color = self.colors["status_green"] if config.get(
            "status") == "Ready" else self.colors["status_red"]
        status_frame = ctk.CTkFrame(
            item,
            fg_color="transparent"
        )
        status_frame.pack(side="right", fill="y", padx=10)

        status_dot = ctk.CTkLabel(
            status_frame,
            text="●",
            font=ctk.CTkFont(size=20),
            text_color=status_color
        )
        status_dot.pack(side="right", padx=5)

        status_label = ctk.CTkLabel(
            status_frame,
            text=config.get("status", "Unknown"),
            font=ctk.CTkFont(size=12),
            text_color=status_color
        )
        status_label.pack(side="right")

        # Make the entire item clickable
        item.bind(
            "<Button-1>",
            lambda e: self.show_chatbot_settings(
                name,
                config))














































































            
































            def update_progress(current, total):
                progress.set(current / total)
                progress_label.configure(
                    text=f"Progress: {int(current/total*100)}%")
                dialog.update()

            # Function to update level indicator
            def update_level(volume):
                # Scale volume (0-1) to width
                width = min(360, int(volume * 360))
                level_indicator.configure(width=width)

                # Update color based on level
                if volume < 0.3:
                    level_indicator.configure(
                        fg_color=self.colors["status_green"])
                elif volume < 0.7:
                    level_indicator.configure(
                        fg_color=self.colors["status_yellow"])
                else:
                    level_indicator.configure(
                        fg_color=self.colors["status_red"])

                # Update text
                level_text.configure(text=f"{int(volume * 100)}%")
                dialog.update()

            # Function to record audio
            def record_audio():
                status_label.configure(
                    text=f"Recording from: {device_info['name']}\nPlease speak now...")

                # Create array to store audio data
                audio_data = []

                # Start time
                start_time = time.time()

                # Callback function for audio stream
                def audio_callback(indata, frames, time_info, status):
                    if status:
                        logging.warning(f"Audio status: {status}")

                    # Copy audio data
                    audio_data.append(indata.copy())

                    # Calculate volume level (RMS)
                    volume = np.sqrt(np.mean(indata**2))

                    # Apply gain if available
                    if hasattr(self, 'gain_var'):
                        volume *= self.gain_var.get()

                    # Update level indicator
                    dialog.after(0, lambda: update_level(min(1.0, volume * 2)))

                    # Update progress
                    elapsed = time.time() - start_time
                    if elapsed < duration:
                        dialog.after(
                            0, lambda: update_progress(
                                elapsed, duration))

                # Start audio stream
                try:
                    with sd.InputStream(
                        device=device_id,
                        channels=1,
                        callback=audio_callback,
                        samplerate=samplerate,
                        blocksize=int(samplerate * 0.1)  # 100ms blocks
                    ):
                        # Wait for duration
                        sd.sleep(int(duration * 1000))
                except Exception as e:
                    error_msg = f"Error recording: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")
                    return None

                # Combine all audio chunks
                if audio_data:
                    return np.concatenate(audio_data)
                return None

            # Function to play audio
            def play_audio(audio_data):
                status_label.configure(text="Playing back recording...")
                progress.set(0)

                try:
                    # Start time
                    start_time = time.time()

                    # Play audio
                    sd.play(audio_data, samplerate)

                    # Update progress during playback
                    def update_playback_progress():
                        elapsed = time.time() - start_time
                        if elapsed < duration and not dialog.winfo_exists():
                            return

                        if elapsed < duration:
                            update_progress(elapsed, duration)
                            dialog.after(100, update_playback_progress)
                        else:
                            progress.set(1.0)
                            progress_label.configure(text="Progress: 100%")

                    # Start progress updates
                    update_playback_progress()

                    # Wait for playback to complete
                    sd.wait()

                    # Test completed
                    status_label.configure(
                        text="Test completed successfully!\n\nYour microphone is working properly.")
                    close_button.configure(state="normal")

                except Exception as e:
                    error_msg = f"Error playing back: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")

            # Run the recording in a separate thread
            def run_test():
                try:
                    # Record audio
                    audio_data = record_audio()

                    if audio_data is not None and len(audio_data) > 0:
                        # Play it back
                        play_audio(audio_data)
                    else:
                        status_label.configure(
                            text="No audio recorded or error occurred.\n\nPlease check if your microphone is properly connected and not muted.")
                        close_button.configure(state="normal")
                except Exception as e:
                    error_msg = f"Test failed: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")

            # Start the test in a separate thread
            threading.Thread(target=run_test, daemon=True).start()



            def update_level(volume):
                # Scale volume (0-1) to width
                width = min(360, int(volume * 360))
                level_indicator.configure(width=width)

                # Update color based on level
                if volume < 0.3:
                    level_indicator.configure(
                        fg_color=self.colors["status_green"])
                elif volume < 0.7:
                    level_indicator.configure(
                        fg_color=self.colors["status_yellow"])
                else:
                    level_indicator.configure(
                        fg_color=self.colors["status_red"])

                # Update text
                level_text.configure(text=f"{int(volume * 100)}%")
                dialog.update()

            # Function to record audio
            def record_audio():
                status_label.configure(
                    text=f"Recording from: {device_info['name']}\nPlease speak now...")

                # Create array to store audio data
                audio_data = []

                # Start time
                start_time = time.time()

                # Callback function for audio stream
                def audio_callback(indata, frames, time_info, status):
                    if status:
                        logging.warning(f"Audio status: {status}")

                    # Copy audio data
                    audio_data.append(indata.copy())

                    # Calculate volume level (RMS)
                    volume = np.sqrt(np.mean(indata**2))

                    # Apply gain if available
                    if hasattr(self, 'gain_var'):
                        volume *= self.gain_var.get()

                    # Update level indicator
                    dialog.after(0, lambda: update_level(min(1.0, volume * 2)))

                    # Update progress
                    elapsed = time.time() - start_time
                    if elapsed < duration:
                        dialog.after(
                            0, lambda: update_progress(
                                elapsed, duration))

                # Start audio stream
                try:
                    with sd.InputStream(
                        device=device_id,
                        channels=1,
                        callback=audio_callback,
                        samplerate=samplerate,
                        blocksize=int(samplerate * 0.1)  # 100ms blocks
                    ):
                        # Wait for duration
                        sd.sleep(int(duration * 1000))
                except Exception as e:
                    error_msg = f"Error recording: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")
                    return None

                # Combine all audio chunks
                if audio_data:
                    return np.concatenate(audio_data)
                return None

            # Function to play audio
            def play_audio(audio_data):
                status_label.configure(text="Playing back recording...")
                progress.set(0)

                try:
                    # Start time
                    start_time = time.time()

                    # Play audio
                    sd.play(audio_data, samplerate)

                    # Update progress during playback
                    def update_playback_progress():
                        elapsed = time.time() - start_time
                        if elapsed < duration and not dialog.winfo_exists():
                            return

                        if elapsed < duration:
                            update_progress(elapsed, duration)
                            dialog.after(100, update_playback_progress)
                        else:
                            progress.set(1.0)
                            progress_label.configure(text="Progress: 100%")

                    # Start progress updates
                    update_playback_progress()

                    # Wait for playback to complete
                    sd.wait()

                    # Test completed
                    status_label.configure(
                        text="Test completed successfully!\n\nYour microphone is working properly.")
                    close_button.configure(state="normal")

                except Exception as e:
                    error_msg = f"Error playing back: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")

            # Run the recording in a separate thread
            def run_test():
                try:
                    # Record audio
                    audio_data = record_audio()

                    if audio_data is not None and len(audio_data) > 0:
                        # Play it back
                        play_audio(audio_data)
                    else:
                        status_label.configure(
                            text="No audio recorded or error occurred.\n\nPlease check if your microphone is properly connected and not muted.")
                        close_button.configure(state="normal")
                except Exception as e:
                    error_msg = f"Test failed: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")

            # Start the test in a separate thread
            threading.Thread(target=run_test, daemon=True).start()



            def record_audio():
                status_label.configure(
                    text=f"Recording from: {device_info['name']}\nPlease speak now...")

                # Create array to store audio data
                audio_data = []

                # Start time
                start_time = time.time()

                # Callback function for audio stream
                def audio_callback(indata, frames, time_info, status):
                    if status:
                        logging.warning(f"Audio status: {status}")

                    # Copy audio data
                    audio_data.append(indata.copy())

                    # Calculate volume level (RMS)
                    volume = np.sqrt(np.mean(indata**2))

                    # Apply gain if available
                    if hasattr(self, 'gain_var'):
                        volume *= self.gain_var.get()

                    # Update level indicator
                    dialog.after(0, lambda: update_level(min(1.0, volume * 2)))

                    # Update progress
                    elapsed = time.time() - start_time
                    if elapsed < duration:
                        dialog.after(
                            0, lambda: update_progress(
                                elapsed, duration))

                # Start audio stream
                try:
                    with sd.InputStream(
                        device=device_id,
                        channels=1,
                        callback=audio_callback,
                        samplerate=samplerate,
                        blocksize=int(samplerate * 0.1)  # 100ms blocks
                    ):
                        # Wait for duration
                        sd.sleep(int(duration * 1000))
                except Exception as e:
                    error_msg = f"Error recording: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")
                    return None

                # Combine all audio chunks
                if audio_data:
                    return np.concatenate(audio_data)
                return None

            # Function to play audio
            def play_audio(audio_data):
                status_label.configure(text="Playing back recording...")
                progress.set(0)

                try:
                    # Start time
                    start_time = time.time()

                    # Play audio
                    sd.play(audio_data, samplerate)

                    # Update progress during playback
                    def update_playback_progress():
                        elapsed = time.time() - start_time
                        if elapsed < duration and not dialog.winfo_exists():
                            return

                        if elapsed < duration:
                            update_progress(elapsed, duration)
                            dialog.after(100, update_playback_progress)
                        else:
                            progress.set(1.0)
                            progress_label.configure(text="Progress: 100%")

                    # Start progress updates
                    update_playback_progress()

                    # Wait for playback to complete
                    sd.wait()

                    # Test completed
                    status_label.configure(
                        text="Test completed successfully!\n\nYour microphone is working properly.")
                    close_button.configure(state="normal")

                except Exception as e:
                    error_msg = f"Error playing back: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")

            # Run the recording in a separate thread
            def run_test():
                try:
                    # Record audio
                    audio_data = record_audio()

                    if audio_data is not None and len(audio_data) > 0:
                        # Play it back
                        play_audio(audio_data)
                    else:
                        status_label.configure(
                            text="No audio recorded or error occurred.\n\nPlease check if your microphone is properly connected and not muted.")
                        close_button.configure(state="normal")
                except Exception as e:
                    error_msg = f"Test failed: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")

            # Start the test in a separate thread
            threading.Thread(target=run_test, daemon=True).start()



                def audio_callback(indata, frames, time_info, status):
                    if status:
                        logging.warning(f"Audio status: {status}")

                    # Copy audio data
                    audio_data.append(indata.copy())

                    # Calculate volume level (RMS)
                    volume = np.sqrt(np.mean(indata**2))

                    # Apply gain if available
                    if hasattr(self, 'gain_var'):
                        volume *= self.gain_var.get()

                    # Update level indicator
                    dialog.after(0, lambda: update_level(min(1.0, volume * 2)))

                    # Update progress
                    elapsed = time.time() - start_time
                    if elapsed < duration:
                        dialog.after(
                            0, lambda: update_progress(
                                elapsed, duration))

                # Start audio stream
                try:
                    with sd.InputStream(
                        device=device_id,
                        channels=1,
                        callback=audio_callback,
                        samplerate=samplerate,
                        blocksize=int(samplerate * 0.1)  # 100ms blocks
                    ):
                        # Wait for duration
                        sd.sleep(int(duration * 1000))
                except Exception as e:
                    error_msg = f"Error recording: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")
                    return None

                # Combine all audio chunks
                if audio_data:
                    return np.concatenate(audio_data)
                return None



            def play_audio(audio_data):
                status_label.configure(text="Playing back recording...")
                progress.set(0)

                try:
                    # Start time
                    start_time = time.time()

                    # Play audio
                    sd.play(audio_data, samplerate)

                    # Update progress during playback
                    def update_playback_progress():
                        elapsed = time.time() - start_time
                        if elapsed < duration and not dialog.winfo_exists():
                            return

                        if elapsed < duration:
                            update_progress(elapsed, duration)
                            dialog.after(100, update_playback_progress)
                        else:
                            progress.set(1.0)
                            progress_label.configure(text="Progress: 100%")

                    # Start progress updates
                    update_playback_progress()

                    # Wait for playback to complete
                    sd.wait()

                    # Test completed
                    status_label.configure(
                        text="Test completed successfully!\n\nYour microphone is working properly.")
                    close_button.configure(state="normal")

                except Exception as e:
                    error_msg = f"Error playing back: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")

            # Run the recording in a separate thread
            def run_test():
                try:
                    # Record audio
                    audio_data = record_audio()

                    if audio_data is not None and len(audio_data) > 0:
                        # Play it back
                        play_audio(audio_data)
                    else:
                        status_label.configure(
                            text="No audio recorded or error occurred.\n\nPlease check if your microphone is properly connected and not muted.")
                        close_button.configure(state="normal")
                except Exception as e:
                    error_msg = f"Test failed: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")

            # Start the test in a separate thread
            threading.Thread(target=run_test, daemon=True).start()



                    def update_playback_progress():
                        elapsed = time.time() - start_time
                        if elapsed < duration and not dialog.winfo_exists():
                            return

                        if elapsed < duration:
                            update_progress(elapsed, duration)
                            dialog.after(100, update_playback_progress)
                        else:
                            progress.set(1.0)
                            progress_label.configure(text="Progress: 100%")

                    # Start progress updates
                    update_playback_progress()

                    # Wait for playback to complete
                    sd.wait()

                    # Test completed
                    status_label.configure(
                        text="Test completed successfully!\n\nYour microphone is working properly.")
                    close_button.configure(state="normal")



            def run_test():
                try:
                    # Record audio
                    audio_data = record_audio()

                    if audio_data is not None and len(audio_data) > 0:
                        # Play it back
                        play_audio(audio_data)
                    else:
                        status_label.configure(
                            text="No audio recorded or error occurred.\n\nPlease check if your microphone is properly connected and not muted.")
                        close_button.configure(state="normal")
                except Exception as e:
                    error_msg = f"Test failed: {str(e)}"
                    logging.error(error_msg)
                    status_label.configure(text=error_msg)
                    close_button.configure(state="normal")

            # Start the test in a separate thread
            threading.Thread(target=run_test, daemon=True).start()



























            











def main():
    """Main function to run the application"""
    try:
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='dragon_gui.log',
            filemode='a'
        )

        # Add console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

        logging.info("Starting DragonVoice application")

        # Initialize Tkinter before creating the app
        root = ctk.CTk()
        root.withdraw()  # Hide the root window

        # Create and run the GUI
        logging.info("Initializing DragonVoiceGUI")
        app = DragonVoiceGUI()

        # Check for required methods
        required_methods = [
            'toggle_voice_assistant',
            'refresh_chatbots',
            'load_config']
        for method in required_methods:
            if not hasattr(app, method):
                logging.error(f"Missing required method: {method}")
                raise AttributeError(
                    f"DragonVoiceGUI is missing required method: {method}")

        logging.info("Starting application main loop")
        app.run()

    except Exception as e:
        logging.error(f"Error running application: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")

        # Show error in a messagebox if possible
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror(
                "Dragon Voice Error",
                f"An error occurred:\n{str(e)}")
        except BaseException:
            pass

        # Print traceback for debugging
        import traceback
        traceback.print_exc()




if __name__ == "__main__":
    main()
