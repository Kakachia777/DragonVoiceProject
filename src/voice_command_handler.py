#!/usr/bin/env python3
"""
Voice command handling functionality for DragonVoice
"""

import logging
from datetime import datetime

class VoiceCommandHandler:
    """Handles voice commands and their display"""

    def __init__(self, parent, colors, fonts):
        """Initialize the voice command handler"""
        self.parent = parent
        self.colors = colors
        self.fonts = fonts
        self.setup_display()

    def setup_display(self):
        """Set up the voice command display"""
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
            text="🎤 Voice Commands",
            font=self.fonts["title"],
            text_color=self.colors["text_bright"]
        )
        title.pack(side="left")

        # Clear button
        clear_button = self.parent.CTkButton(
            header,
            text="Clear",
            command=self.clear_display,
            fg_color=self.colors["bg_light"],
            hover_color=self.colors["accent_primary"],
            width=80
        )
        clear_button.pack(side="right")

        # Commands display
        self.text_display = self.parent.CTkTextbox(
            self.frame,
            fg_color=self.colors["bg_light"],
            text_color=self.colors["text_bright"],
            font=self.fonts["normal"],
            corner_radius=10,
            border_width=1,
            border_color=self.colors["bg_light"],
            height=200
        )
        self.text_display.pack(fill="both", expand=True, padx=20, pady=(5, 20))

        # Configure text tags
        self.text_display._textbox.tag_configure(
            "timestamp",
            foreground=self.colors["accent_secondary"]
        )
        self.text_display._textbox.tag_configure(
            "command",
            foreground=self.colors["text_bright"]
        )
        self.text_display._textbox.tag_configure(
            "system",
            foreground=self.colors["status_blue"]
        )

        # Add initial message
        self.text_display.configure(state="normal")
        system_pos = self.text_display.index("end-1c")
        self.text_display.insert("end", "Voice commands will appear here after you click 'Start Voice Assistant'.\n\n")
        self.text_display._textbox.tag_add("system", system_pos, self.text_display.index("end-2c"))
        self.text_display.configure(state="disabled")

    def handle_command(self, command):
        """Handle a voice command and update the display"""
        try:
            # Add timestamp and command to display
            self.text_display.configure(state="normal")
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Add timestamp with formatting
            timestamp_pos = self.text_display.index("end-1c")
            self.text_display.insert("end", f"[{timestamp}] ")
            self.text_display._textbox.tag_add("timestamp", timestamp_pos, self.text_display.index("end-1c"))

            # Add command with formatting
            command_pos = self.text_display.index("end-1c")
            self.text_display.insert("end", f"{command}\n\n")
            self.text_display._textbox.tag_add("command", command_pos, self.text_display.index("end-2c"))

            # Auto-scroll to bottom
            self.text_display.see("end")
            self.text_display.configure(state="disabled")

            return True

        except Exception as e:
            logging.error(f"Error handling voice command: {str(e)}")
            return False

    def clear_display(self):
        """Clear the voice commands display"""
        self.text_display.configure(state="normal")
        self.text_display.delete("1.0", "end")
        # Add initial message
        system_pos = self.text_display.index("end-1c")
        self.text_display.insert("end", "Voice commands will appear here after you click 'Start Voice Assistant'.\n\n")
        self.text_display._textbox.tag_add("system", system_pos, self.text_display.index("end-2c"))
        self.text_display.configure(state="disabled")

    def get_frame(self):
        """Get the main frame"""
        return self.frame 