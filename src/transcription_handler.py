#!/usr/bin/env python3
"""
Transcription handling functionality for DragonVoice
"""

import logging
from datetime import datetime

class TranscriptionHandler:
    """Handles transcriptions and their display"""

    def __init__(self, parent, colors, fonts, on_enter_callback=None):
        """Initialize the transcription handler"""
        self.parent = parent
        self.colors = colors
        self.fonts = fonts
        self.on_enter_callback = on_enter_callback
        self.setup_display()

    def setup_display(self):
        """Set up the transcription display"""
        # Create main frame
        self.frame = self.parent.CTkFrame(
            self.parent,
            fg_color=self.colors["bg_medium"],
            corner_radius=15,
            border_width=1,
            border_color=self.colors["bg_light"]
        )

        # Header
        header = self.parent.CTkFrame(self.frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        # Title with icon
        title = self.parent.CTkLabel(
            header,
            text="📝 Transcription",
            font=self.fonts["title"],
            text_color=self.colors["text_bright"]
        )
        title.pack(side="left")

        # Controls frame
        controls = self.parent.CTkFrame(header, fg_color="transparent")
        controls.pack(side="right")

        # Clear button
        clear_button = self.parent.CTkButton(
            controls,
            text="Clear",
            command=self.clear_display,
            fg_color=self.colors["bg_light"],
            hover_color=self.colors["accent_primary"],
            width=80
        )
        clear_button.pack(side="right", padx=(0, 10))

        # Enter button
        self.enter_button = self.parent.CTkButton(
            controls,
            text="Enter",
            command=self.on_enter_pressed,
            fg_color=self.colors["accent_primary"],
            hover_color=self.colors["accent_secondary"],
            width=100,
            state="disabled"
        )
        self.enter_button.pack(side="right")

        # Transcription display
        self.text_display = self.parent.CTkTextbox(
            self.frame,
            fg_color=self.colors["bg_light"],
            text_color=self.colors["text_bright"],
            font=self.fonts["large"],
            corner_radius=10,
            border_width=1,
            border_color=self.colors["bg_light"],
            height=150
        )
        self.text_display.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        # Configure text tags
        self.text_display._textbox.tag_configure(
            "timestamp",
            foreground=self.colors["accent_secondary"]
        )
        self.text_display._textbox.tag_configure(
            "transcription",
            foreground=self.colors["text_bright"]
        )

        # Add initial message
        self.text_display.configure(state="normal")
        self.text_display.insert("end", "Transcribed text will appear here...\n")
        self.text_display.configure(state="disabled")

    def update_transcription(self, text):
        """Update the transcription display with new text"""
        try:
            self.text_display.configure(state="normal")
            self.text_display.delete("1.0", "end")
            self.text_display.insert("end", text)
            self.text_display.configure(state="disabled")
            
            # Enable enter button if there's text
            if text and text != "Transcribed text will appear here...\n":
                self.enter_button.configure(state="normal")
            else:
                self.enter_button.configure(state="disabled")

            return True

        except Exception as e:
            logging.error(f"Error updating transcription: {str(e)}")
            return False

    def clear_display(self):
        """Clear the transcription display"""
        self.text_display.configure(state="normal")
        self.text_display.delete("1.0", "end")
        self.text_display.insert("end", "Transcribed text will appear here...\n")
        self.text_display.configure(state="disabled")
        self.enter_button.configure(state="disabled")

    def on_enter_pressed(self):
        """Handle the enter button press"""
        if self.on_enter_callback:
            text = self.text_display.get("1.0", "end-1c").strip()
            if text and text != "Transcribed text will appear here...":
                self.on_enter_callback(text)
                self.clear_display()

    def get_frame(self):
        """Get the main frame"""
        return self.frame 