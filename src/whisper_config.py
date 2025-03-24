#!/usr/bin/env python3
"""
Whisper API Configuration - Handles Whisper API settings and configuration UI
"""

import os
import json
import logging
import threading
import tempfile
import numpy as np
import soundfile as sf
import customtkinter as ctk
from openai import OpenAI

class WhisperConfigFrame(ctk.CTkFrame):
    """Frame for Whisper API configuration settings"""
    
    def __init__(self, parent, colors, fonts, config, config_path, update_status_callback):
        super().__init__(parent, fg_color=colors["bg_medium"], corner_radius=10)
        
        self.colors = colors
        self.fonts = fonts
        self.config = config
        self.config_path = config_path
        self.update_status = update_status_callback
        self.parent = parent  # Store parent reference
        
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        
        # Create the configuration UI
        self.create_config_ui()
    
    def create_config_ui(self):
        """Create the Whisper API configuration UI"""
        current_row = 0
        
        # Section title
        title = ctk.CTkLabel(
            self,
            text="Whisper API Settings",
            font=self.fonts["title"],
            text_color=self.colors["text_bright"]
        )
        title.grid(row=current_row, column=0, sticky="w", padx=15, pady=(15, 10))
        current_row += 1

        # API Key
        api_key_frame = ctk.CTkFrame(self, fg_color="transparent")
        api_key_frame.grid(row=current_row, column=0, sticky="ew", padx=15, pady=5)
        api_key_frame.grid_columnconfigure(1, weight=1)

        api_key_label = ctk.CTkLabel(
            api_key_frame,
            text="API Key",
            font=self.fonts["normal"],
            text_color=self.colors["text_normal"],
            width=150,
            anchor="w"
        )
        api_key_label.grid(row=0, column=0)

        # Set default API key if not already set
        default_api_key = "j3ydNXEmQFyDKwl5mWxSzcvdZcTLJw1t"
        if not self.config.get("openai_api_key"):
            self.config["openai_api_key"] = default_api_key
            
        self.api_key_var = ctk.StringVar(value=self.config.get("openai_api_key", default_api_key))
        
        api_key_entry = ctk.CTkEntry(
            api_key_frame,
            textvariable=self.api_key_var,
            width=300,
            show="•"
        )
        api_key_entry.grid(row=0, column=1, padx=10)

        show_key = ctk.CTkButton(
            api_key_frame,
            text="👁️",
            width=40,
            command=lambda: api_key_entry.configure(show="" if api_key_entry.cget("show") == "•" else "•")
        )
        show_key.grid(row=0, column=2)
        current_row += 1

        # Base URL
        base_url_frame = ctk.CTkFrame(self, fg_color="transparent")
        base_url_frame.grid(row=current_row, column=0, sticky="ew", padx=15, pady=5)
        base_url_frame.grid_columnconfigure(1, weight=1)

        base_url_label = ctk.CTkLabel(
            base_url_frame,
            text="API Base URL",
            font=self.fonts["normal"],
            text_color=self.colors["text_normal"],
            width=150,
            anchor="w"
        )
        base_url_label.grid(row=0, column=0)

        # Set DeepInfra base URL
        default_base_url = "https://api.deepinfra.com/v1/inference/openai/whisper-large-v3"
        self.base_url_var = ctk.StringVar(value=self.config.get("base_url", default_base_url))
        
        base_url_entry = ctk.CTkEntry(
            base_url_frame,
            textvariable=self.base_url_var,
            width=300
        )
        base_url_entry.grid(row=0, column=1, padx=10)
        current_row += 1

        # Model Selection
        model_frame = ctk.CTkFrame(self, fg_color="transparent")
        model_frame.grid(row=current_row, column=0, sticky="ew", padx=15, pady=5)
        model_frame.grid_columnconfigure(1, weight=1)

        model_label = ctk.CTkLabel(
            model_frame,
            text="Model",
            font=self.fonts["normal"],
            text_color=self.colors["text_normal"],
            width=150,
            anchor="w"
        )
        model_label.grid(row=0, column=0)

        # Set model to openai/whisper-large-v3 for DeepInfra
        self.model_var = ctk.StringVar(value=self.config.get("whisper_model", "openai/whisper-large-v3"))
        model_dropdown = ctk.CTkOptionMenu(
            model_frame,
            values=["openai/whisper-large-v3"],  # Only this model is supported for now
            variable=self.model_var,
            width=300
        )
        model_dropdown.grid(row=0, column=1, padx=10)
        current_row += 1

        # Language Selection
        language_frame = ctk.CTkFrame(self, fg_color="transparent")
        language_frame.grid(row=current_row, column=0, sticky="ew", padx=15, pady=5)
        language_frame.grid_columnconfigure(1, weight=1)

        language_label = ctk.CTkLabel(
            language_frame,
            text="Language",
            font=self.fonts["normal"],
            text_color=self.colors["text_normal"],
            width=150,
            anchor="w"
        )
        language_label.grid(row=0, column=0)

        self.language_var = ctk.StringVar(value=self.config.get("whisper_language", "en"))  # Default to English
        
        # Create a dropdown for language instead of a text entry
        language_dropdown = ctk.CTkOptionMenu(
            language_frame,
            values=["en - English", "es - Spanish", "fr - French", "de - German", "it - Italian", "pt - Portuguese", "nl - Dutch", "ja - Japanese", "zh - Chinese", "ru - Russian"],
            width=300
        )
        language_dropdown.set("en - English")  # Set default to English
        
        # Function to update the language variable when dropdown changes
        def on_language_change(choice):
            # Extract the language code (first 2 characters)
            lang_code = choice.split(" ")[0]
            self.language_var.set(lang_code)
        
        language_dropdown.configure(command=on_language_change)
        language_dropdown.grid(row=0, column=1, padx=10)
        
        current_row += 1

        # Response Format
        format_frame = ctk.CTkFrame(self, fg_color="transparent")
        format_frame.grid(row=current_row, column=0, sticky="ew", padx=15, pady=5)
        format_frame.grid_columnconfigure(1, weight=1)

        format_label = ctk.CTkLabel(
            format_frame,
            text="Response Format",
            font=self.fonts["normal"],
            text_color=self.colors["text_normal"],
            width=150,
            anchor="w"
        )
        format_label.grid(row=0, column=0)

        self.format_var = ctk.StringVar(value=self.config.get("response_format", "json"))
        format_dropdown = ctk.CTkOptionMenu(
            format_frame,
            values=["json", "text", "srt", "verbose_json", "vtt"],
            variable=self.format_var,
            width=300
        )
        format_dropdown.grid(row=0, column=1, padx=10)
        current_row += 1

        # Temperature
        temp_frame = ctk.CTkFrame(self, fg_color="transparent")
        temp_frame.grid(row=current_row, column=0, sticky="ew", padx=15, pady=5)
        temp_frame.grid_columnconfigure(1, weight=1)

        temp_label = ctk.CTkLabel(
            temp_frame,
            text="Temperature",
            font=self.fonts["normal"],
            text_color=self.colors["text_normal"],
            width=150,
            anchor="w"
        )
        temp_label.grid(row=0, column=0)

        self.temp_var = ctk.DoubleVar(value=self.config.get("temperature", 0))
        temp_slider = ctk.CTkSlider(
            temp_frame,
            from_=0.0,
            to=1.0,
            variable=self.temp_var,
            width=300
        )
        temp_slider.grid(row=0, column=1, padx=10)

        temp_value = ctk.CTkLabel(
            temp_frame,
            textvariable=self.temp_var,
            width=50
        )
        temp_value.grid(row=0, column=2)
        current_row += 1

        # Timestamp Granularity
        timestamp_frame = ctk.CTkFrame(self, fg_color="transparent")
        timestamp_frame.grid(row=current_row, column=0, sticky="ew", padx=15, pady=5)
        timestamp_frame.grid_columnconfigure(1, weight=1)

        timestamp_label = ctk.CTkLabel(
            timestamp_frame,
            text="Timestamp Granularity",
            font=self.fonts["normal"],
            text_color=self.colors["text_normal"],
            width=150,
            anchor="w"
        )
        timestamp_label.grid(row=0, column=0)

        self.timestamp_var = ctk.StringVar(value=self.config.get("timestamp_granularity", "word"))
        timestamp_dropdown = ctk.CTkOptionMenu(
            timestamp_frame,
            values=["word", "segment"],
            variable=self.timestamp_var,
            width=300
        )
        timestamp_dropdown.grid(row=0, column=1, padx=10)
        current_row += 1

        # Buttons frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=current_row, column=0, sticky="ew", padx=15, pady=15)
        button_frame.grid_columnconfigure(1, weight=1)

        # Test connection button
        test_button = ctk.CTkButton(
            button_frame,
            text="Test Connection",
            command=self.test_connection,
            fg_color=self.colors["accent_secondary"],
            hover_color=self.colors["accent_primary"],
            width=150
        )
        test_button.grid(row=0, column=0, sticky="w")

        # Save button
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Changes",
            command=self.save_config,
            fg_color=self.colors["accent_primary"],
            hover_color=self.colors["accent_secondary"],
            width=150
        )
        save_button.grid(row=0, column=1, sticky="e")
    
    def save_config(self):
        """Save the Whisper API configuration"""
        try:
            # Update config dictionary with new values
            self.config["openai_api_key"] = self.api_key_var.get()
            self.config["base_url"] = self.base_url_var.get()
            self.config["whisper_model"] = self.model_var.get()
            self.config["whisper_language"] = self.language_var.get()
            self.config["response_format"] = self.format_var.get()
            self.config["temperature"] = self.temp_var.get()
            self.config["timestamp_granularity"] = self.timestamp_var.get()

            # Save to config file
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=4)

            # Update environment variable for API key
            os.environ["OPENAI_API_KEY"] = self.api_key_var.get()

            # Show success message
            self.update_status("Whisper configuration saved successfully", "info")

        except Exception as e:
            logging.error(f"Error saving Whisper configuration: {str(e)}")
            self.update_status(f"Error saving configuration: {str(e)}", "error")
    
    def test_connection(self):
        """Test the Whisper API connection with current settings"""
        try:
            # Store dialog reference at class level to prevent garbage collection
            self.test_dialog = ctk.CTkToplevel(self)
            self.test_dialog.title("Testing Whisper API Connection")
            self.test_dialog.geometry("400x200")
            self.test_dialog.transient(self)
            self.test_dialog.grab_set()

            # Status label
            self.test_status_label = ctk.CTkLabel(
                self.test_dialog,
                text="Testing connection...",
                font=self.fonts["normal"],
                text_color=self.colors["text_bright"]
            )
            self.test_status_label.pack(pady=20)

            # Progress indicator
            self.test_progress = ctk.CTkProgressBar(
                self.test_dialog,
                width=300,
                mode="indeterminate"
            )
            self.test_progress.pack(pady=20)
            self.test_progress.start()

            # Get current settings before starting thread
            api_key = self.api_key_var.get()
            base_url = self.base_url_var.get()
            
            if not api_key:
                self.show_test_error("API key is required")
                return

            if not base_url:
                self.show_test_error("API base URL is required")
                return

            # Run test in separate thread
            self.test_thread = threading.Thread(target=self._run_connection_test, 
                                             args=(api_key, base_url),
                                             daemon=True)
            self.test_thread.start()

        except Exception as e:
            logging.error(f"Error testing Whisper connection: {str(e)}")
            self.update_status(f"Error testing connection: {str(e)}", "error")

    def _run_connection_test(self, api_key, base_url):
        """Run the actual connection test in a separate thread"""
        temp_file = None
        try:
            # Initialize client with DeepInfra settings
            client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )

            # Create a small test audio file
            sample_rate = 16000
            duration = 1  # 1 second of silence
            audio_data = np.zeros(int(sample_rate * duration))
            
            # Create a unique temporary file name
            temp_dir = tempfile.gettempdir()
            temp_file_path = os.path.join(temp_dir, f"whisper_test_{threading.get_ident()}.wav")
            
            try:
                # Save audio data to file
                sf.write(temp_file_path, audio_data, sample_rate)
                
                # Test transcription with DeepInfra settings
                with open(temp_file_path, "rb") as audio_file:
                    response = client.audio.transcriptions.create(
                        model="openai/whisper-large-v3",  # Correct model name
                        file=audio_file,
                        response_format="json",
                        language="en"  # Explicitly set language for testing
                    )
            finally:
                # Clean up temp file
                try:
                    if os.path.exists(temp_file_path):
                        os.close(audio_file.fileno())  # Ensure file handle is closed
                        os.unlink(temp_file_path)
                except Exception as cleanup_error:
                    logging.warning(f"Failed to clean up temporary file: {cleanup_error}")

            # Schedule success UI update on main thread
            if hasattr(self, 'test_dialog') and self.test_dialog.winfo_exists():
                self.test_dialog.after(0, self.show_test_success)

        except Exception as e:
            # Schedule error UI update on main thread
            if hasattr(self, 'test_dialog') and self.test_dialog.winfo_exists():
                error_msg = str(e)
                if "404" in error_msg:
                    error_msg = "API endpoint not found. Please check if the API URL is correct."
                self.test_dialog.after(0, lambda: self.show_test_error(error_msg))

    def show_test_success(self):
        """Show success message in test dialog"""
        if hasattr(self, 'test_dialog') and self.test_dialog.winfo_exists():
            if hasattr(self, 'test_status_label'):
                self.test_status_label.configure(
                    text="Connection successful!\nDeepInfra Whisper API is working properly.",
                    text_color=self.colors["status_green"]
                )
            if hasattr(self, 'test_progress'):
                self.test_progress.stop()
                self.test_progress.pack_forget()
            
            close_button = ctk.CTkButton(
                self.test_dialog,
                text="Close",
                command=self.test_dialog.destroy,
                fg_color=self.colors["accent_primary"]
            )
            close_button.pack(pady=20)

    def show_test_error(self, error_msg):
        """Show error message in test dialog"""
        if hasattr(self, 'test_dialog') and self.test_dialog.winfo_exists():
            if hasattr(self, 'test_status_label'):
                self.test_status_label.configure(
                    text=f"Connection failed:\n{error_msg}",
                    text_color=self.colors["status_red"]
                )
            if hasattr(self, 'test_progress'):
                self.test_progress.stop()
                self.test_progress.pack_forget()
            
            close_button = ctk.CTkButton(
                self.test_dialog,
                text="Close",
                command=self.test_dialog.destroy,
                fg_color=self.colors["accent_primary"]
            )
            close_button.pack(pady=20) 