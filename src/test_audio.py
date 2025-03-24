#!/usr/bin/env python3
"""
Test script for improved audio handling and visualization in the Dragon Voice Project.
"""

import os
import sys
import time
import logging
import tkinter as tk
import customtkinter as ctk
import sounddevice as sd
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class AudioLevelMeter:
    """A visual meter for displaying audio levels"""
    
    def __init__(self, parent):
        """Initialize the audio level meter"""
        # Create main window if no parent
        if parent is None:
            self.window = ctk.CTk()
            self.window.title("Audio Level Test")
            self.window.geometry("600x400")
            parent = self.window
        else:
            self.window = None
        
        # Create frame
        self.frame = ctk.CTkFrame(parent)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create controls
        self.create_controls()
        
        # Create level meter
        self.create_level_meter()
        
        # Initialize audio
        self.init_audio()
    
    def create_controls(self):
        """Create control panel"""
        control_frame = ctk.CTkFrame(self.frame)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Device selection
        device_frame = ctk.CTkFrame(control_frame)
        device_frame.pack(side="left", padx=10, pady=5)
        
        ctk.CTkLabel(device_frame, text="Input Device:").pack(side="left", padx=5)
        
        self.device_var = tk.StringVar(value="Default")
        self.device_menu = ctk.CTkOptionMenu(
            device_frame,
            variable=self.device_var,
            values=["Default"],
            command=self.on_device_change
        )
        self.device_menu.pack(side="left", padx=5)
        
        # Refresh button
        ctk.CTkButton(
            device_frame,
            text="🔄",
            width=30,
            command=self.refresh_devices
        ).pack(side="left", padx=5)
        
        # Gain control
        gain_frame = ctk.CTkFrame(control_frame)
        gain_frame.pack(side="left", padx=10, pady=5)
        
        ctk.CTkLabel(gain_frame, text="Gain:").pack(side="left", padx=5)
        
        self.gain_var = tk.DoubleVar(value=1.0)
        gain_slider = ctk.CTkSlider(
            gain_frame,
            from_=0.0,
            to=2.0,
            variable=self.gain_var,
            width=100,
            command=self.on_gain_change
        )
        gain_slider.pack(side="left", padx=5)
        
        # Start/Stop button
        self.start_button = ctk.CTkButton(
            control_frame,
            text="Start",
            command=self.toggle_recording
        )
        self.start_button.pack(side="right", padx=10)
    
    def create_level_meter(self):
        """Create the level meter display"""
        meter_frame = ctk.CTkFrame(self.frame)
        meter_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Level display
        self.level_var = tk.StringVar(value="-∞ dB")
        self.level_label = ctk.CTkLabel(
            meter_frame,
            textvariable=self.level_var,
            font=("Courier", 24)
        )
        self.level_label.pack(pady=10)
        
        # Create canvas for meter
        self.canvas = tk.Canvas(
            meter_frame,
            height=60,
            bg='black',
            highlightthickness=1,
            highlightbackground='gray'
        )
        self.canvas.pack(fill="x", padx=10, pady=10)
        
        # Peak hold line
        self.peak_level = 0
        self.peak_hold_time = time.time()
    
    def init_audio(self):
        """Initialize audio handling"""
        self.recording = False
        self.stream = None
        self.refresh_devices()
    
    def refresh_devices(self):
        """Refresh the list of audio devices"""
        try:
            devices = sd.query_devices()
            device_list = ["Default"]
            
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    device_list.append(f"{dev['name']} (ID: {i})")
            
            self.device_menu.configure(values=device_list)
            if self.device_var.get() not in device_list:
                self.device_var.set("Default")
                
        except Exception as e:
            logging.error(f"Error refreshing devices: {e}")
    
    def get_device_id(self):
        """Get the numeric ID from the device selection"""
        device_str = self.device_var.get()
        if "ID:" in device_str:
            try:
                return int(device_str.split("ID:")[1].strip().rstrip(")"))
            except:
                pass
        return None
    
    def on_device_change(self, selection):
        """Handle device selection change"""
        if self.recording:
            self.stop_recording()
            self.start_recording()
    
    def on_gain_change(self, value):
        """Handle gain adjustment"""
        pass  # Gain is applied in audio callback
    
    def toggle_recording(self):
        """Toggle recording state"""
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()
    
    def start_recording(self):
        """Start recording and monitoring audio levels"""
        try:
            device_id = self.get_device_id()
            
            # Get device info
            if device_id is not None:
                device_info = sd.query_devices(device_id, 'input')
                samplerate = int(device_info['default_samplerate'])
                channels = min(2, device_info['max_input_channels'])
            else:
                samplerate = 44100
                channels = 1
            
            # Start the stream
            self.stream = sd.InputStream(
                device=device_id,
                channels=channels,
                samplerate=samplerate,
                callback=self.audio_callback
            )
            self.stream.start()
            
            self.recording = True
            self.start_button.configure(text="Stop")
            
            # Start animation
            self.animate()
            
        except Exception as e:
            logging.error(f"Error starting recording: {e}")
    
    def stop_recording(self):
        """Stop recording"""
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.start_button.configure(text="Start")
    
    def audio_callback(self, indata, frames, time_info, status):
        """Process audio data and update level"""
        if status:
            logging.warning(f"Audio status: {status}")
        
        try:
            # Calculate RMS value
            rms = np.sqrt(np.mean(indata**2))
            
            # Apply gain
            rms = rms * self.gain_var.get()
            
            # Convert to decibels
            if rms > 0:
                db = 20 * np.log10(rms)
            else:
                db = -60
            
            # Update peak
            if db > self.peak_level:
                self.peak_level = db
                self.peak_hold_time = time.time()
            
            # Update level display
            self.level_var.set(f"{db:>6.1f} dB")
            
        except Exception as e:
            logging.error(f"Error in audio callback: {e}")
    
    def animate(self):
        """Animate the level meter"""
        if not self.recording:
            return
        
        try:
            # Get canvas dimensions
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
            
            # Clear canvas
            self.canvas.delete("all")
            
            # Get current level
            try:
                db = float(self.level_var.get().split()[0])
            except:
                db = -60
            
            # Normalize level to 0-1 range
            level = (db + 60) / 60  # -60dB to 0dB
            level = max(0, min(1, level))
            
            # Draw background
            self.canvas.create_rectangle(0, 0, width, height, fill='black')
            
            # Draw level meter
            if level > 0:
                meter_width = int(width * level)
                
                # Calculate color
                if db < -20:  # Green
                    color = '#00ff00'
                elif db < -10:  # Yellow
                    color = '#ffff00'
                else:  # Red
                    color = '#ff0000'
                
                self.canvas.create_rectangle(
                    0, 0, meter_width, height,
                    fill=color, outline=''
                )
            
            # Draw peak hold
            if time.time() - self.peak_hold_time < 2.0:  # Hold peak for 2 seconds
                peak_x = int(width * ((self.peak_level + 60) / 60))
                self.canvas.create_line(
                    peak_x, 0, peak_x, height,
                    fill='white', width=2
                )
            else:
                # Let peak fall
                self.peak_level = max(-60, self.peak_level - 0.5)
            
            # Draw tick marks
            for db in [-60, -50, -40, -30, -20, -10, 0]:
                x = int(width * ((db + 60) / 60))
                self.canvas.create_line(
                    x, height-10, x, height,
                    fill='white'
                )
                self.canvas.create_text(
                    x, height-15,
                    text=str(db),
                    fill='white',
                    anchor='s',
                    font=('Arial', 8)
                )
            
        except Exception as e:
            logging.error(f"Error in animation: {e}")
        
        # Schedule next frame
        if self.window:
            self.window.after(33, self.animate)  # ~30 FPS
    
    def run(self):
        """Start the application"""
        if self.window:
            self.window.mainloop()

def main():
    """Main function"""
    app = AudioLevelMeter(None)
    app.run()

if __name__ == "__main__":
    main() 