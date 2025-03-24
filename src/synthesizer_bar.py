#!/usr/bin/env python3
"""
Synthesizer Bar - A visual component for the DragonVoice GUI that shows voice detection
with improved visualization and smoother animations
"""

import tkinter as tk
import customtkinter as ctk
import numpy as np
import logging
from typing import Dict, Any
import time

class SynthesizerBar:
    """
    A visual component that shows voice detection levels with improved visualization
    """
    
    def __init__(self, parent, colors: Dict[str, str], fonts: Dict[str, Any]):
        """Initialize the synthesizer bar with improved visuals"""
        self.parent = parent
        self.colors = colors
        self.fonts = fonts
        
        # Animation smoothing
        self.current_level = 0
        self.target_level = 0
        self.smoothing_factor = 0.3  # Adjust for smoother/faster transitions
        self.last_update = time.time()
        
        # Peak hold
        self.peak_level = 0
        self.peak_hold_time = 1.0  # seconds to hold peak
        self.last_peak_time = time.time()
        
        # Create the frame
        self.frame = ctk.CTkFrame(
            parent,
            fg_color=colors["bg_dark"],
            corner_radius=10,
            height=80
        )
        
        # Header frame
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        # Synthesizer label with icon
        self.label = ctk.CTkLabel(
            header_frame,
            text="🎤 Voice Detection",
            font=fonts["normal"],
            text_color=colors["text_bright"]
        )
        self.label.pack(side="left")
        
        # Level indicator text
        self.level_text = ctk.CTkLabel(
            header_frame,
            text="0 dB",
            font=fonts["small"],
            text_color=colors["text_dim"]
        )
        self.level_text.pack(side="right")
        
        # Create level meter canvas
        self.canvas = ctk.CTkCanvas(
            self.frame,
            bg=colors["bg_dark"],
            highlightthickness=0,
            height=30
        )
        
        # Pack widgets
        self.frame.pack(fill="x", padx=20, pady=10)
        self.canvas.pack(fill="x", padx=15, pady=(0, 10))
        
        # Initialize with zero level
        self.update(0)
        
        # Start animation loop
        self._animate()
    
    def _animate(self):
        """Animate smooth transitions between levels"""
        current_time = time.time()
        dt = current_time - self.last_update
        
        # Smooth transition to target level
        diff = self.target_level - self.current_level
        self.current_level += diff * self.smoothing_factor
        
        # Update peak level
        if self.current_level > self.peak_level:
            self.peak_level = self.current_level
            self.last_peak_time = current_time
        elif current_time - self.last_peak_time > self.peak_hold_time:
            self.peak_level = max(self.current_level, self.peak_level - 20 * dt)  # Gradual peak fall
        
        # Draw the visualization
        self._draw_meter(self.current_level)
        
        # Update timestamp
        self.last_update = current_time
        
        # Schedule next animation frame
        self.parent.after(16, self._animate)  # ~60 FPS
    
    def _draw_meter(self, level: float):
        """Draw the level meter with improved visuals"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Get canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Ensure we have valid dimensions
        if width <= 1:
            width = 200
        if height <= 1:
            height = 30
        
        # Draw background
        self.canvas.create_rectangle(
            0, 0, width, height,
            fill=self.colors["bg_dark"], 
            outline=self.colors["bg_medium"],
            width=1
        )
        
        # Ensure level is in range 0-100
        level = max(0, min(100, level))
        
        # Calculate meter width
        meter_width = max(1, min(width - 2, (width - 2) * (level / 100)))
        
        # Draw gradient meter
        segments = 50
        segment_width = meter_width / segments if segments > 0 else 0
        
        for i in range(segments):
            # Calculate segment position
            x1 = 1 + (i * segment_width)
            x2 = x1 + segment_width
            
            # Calculate color based on position
            if level < 30:
                color = self._interpolate_color(
                    self.colors["status_green"],
                    self.colors["status_yellow"],
                    i / segments
                )
            else:
                color = self._interpolate_color(
                    self.colors["status_yellow"],
                    self.colors["status_red"],
                    i / segments
                )
            
            # Draw segment
            if x1 < meter_width:
                self.canvas.create_rectangle(
                    x1, 1,
                    min(x2, meter_width), height - 1,
                    fill=color,
                    outline=""
                )
        
        # Draw peak indicator
        if self.peak_level > 0:
            peak_x = 1 + ((width - 2) * (self.peak_level / 100))
            self.canvas.create_line(
                peak_x, 1,
                peak_x, height - 1,
                fill=self.colors["text_bright"],
                width=2
            )
        
        # Draw tick marks and labels
        self._draw_ticks(width, height)
        
        # Update level text
        self.level_text.configure(text=f"{int(level)} dB")
    
    def _draw_ticks(self, width: int, height: int):
        """Draw tick marks and labels"""
        for i in range(11):  # 0% to 100% in 10% increments
            tick_x = 1 + ((width - 2) * (i / 10))
            tick_height = height / 4 if i % 5 == 0 else height / 8
            
            self.canvas.create_line(
                tick_x, height - 1,
                tick_x, height - tick_height,
                fill=self.colors["text_dim"],
                width=1
            )
            
            # Add labels at major ticks
            if i in [0, 5, 10] and width > 100:
                self.canvas.create_text(
                    tick_x, height - tick_height - 5,
                    text=f"{i*10}",
                    fill=self.colors["text_dim"],
                    font=("Helvetica", 7)
                )
    
    def _interpolate_color(self, color1: str, color2: str, factor: float) -> str:
        """Interpolate between two colors"""
        # Convert hex to RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        # Interpolate
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def update(self, level: float):
        """Update the target level for smooth animation"""
        self.target_level = level
    
    def update_level(self, level: float):
        """Alias for update method to maintain compatibility"""
        self.update(level) 