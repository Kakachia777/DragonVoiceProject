#!/usr/bin/env python3
"""
Microphone Test Utility for Dragon Voice Project

This script provides a simple utility to test microphone selection and recording
functionality. It lists all available audio input devices and allows the user to
select one for testing.
"""

import os
import sys
import time
import numpy as np
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import sounddevice as sd
    import soundfile as sf
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install required packages: pip install sounddevice soundfile numpy")
    sys.exit(1)

class MicrophoneTestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dragon Voice - Microphone Test")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Set up the main frame
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            self.main_frame, 
            text="Microphone Test Utility",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # Device selection frame
        device_frame = ttk.LabelFrame(self.main_frame, text="Audio Input Devices", padding=10)
        device_frame.pack(fill=tk.X, pady=10)
        
        # Device list
        self.device_listbox = tk.Listbox(device_frame, height=10, width=70)
        self.device_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for device list
        scrollbar = ttk.Scrollbar(device_frame, orient=tk.VERTICAL, command=self.device_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.device_listbox.config(yscrollcommand=scrollbar.set)
        
        # Refresh button
        refresh_button = ttk.Button(
            self.main_frame, 
            text="Refresh Device List",
            command=self.refresh_device_list
        )
        refresh_button.pack(pady=5)
        
        # Test frame
        test_frame = ttk.LabelFrame(self.main_frame, text="Test Recording", padding=10)
        test_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Status label
        self.status_label = ttk.Label(
            test_frame,
            text="Select a device and click 'Test' to record audio",
            font=("Helvetica", 10)
        )
        self.status_label.pack(pady=10)
        
        # Level meter
        self.level_frame = ttk.Frame(test_frame, height=30)
        self.level_frame.pack(fill=tk.X, pady=10)
        
        self.level_canvas = tk.Canvas(
            self.level_frame,
            height=30,
            bg="#333333",
            highlightthickness=0
        )
        self.level_canvas.pack(fill=tk.X)
        
        # Test button
        self.test_button = ttk.Button(
            test_frame,
            text="Test Selected Device",
            command=self.test_microphone
        )
        self.test_button.pack(pady=10)
        
        # Duration selection
        duration_frame = ttk.Frame(test_frame)
        duration_frame.pack(pady=5)
        
        ttk.Label(duration_frame, text="Recording Duration (seconds): ").pack(side=tk.LEFT)
        
        self.duration_var = tk.IntVar(value=5)
        duration_spinbox = ttk.Spinbox(
            duration_frame,
            from_=1,
            to=10,
            textvariable=self.duration_var,
            width=5
        )
        duration_spinbox.pack(side=tk.LEFT)
        
        # Results frame
        self.results_frame = ttk.LabelFrame(self.main_frame, text="Test Results", padding=10)
        self.results_frame.pack(fill=tk.X, pady=10)
        
        self.results_text = tk.Text(self.results_frame, height=5, width=70)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Initialize
        self.refresh_device_list()
        
        # Recording state
        self.recording = False
        self.audio_data = []
        
    def refresh_device_list(self):
        """Refresh the list of available audio input devices"""
        try:
            # Clear the listbox
            self.device_listbox.delete(0, tk.END)
            
            # Get devices
            devices = sd.query_devices()
            
            # Add default device
            self.device_listbox.insert(tk.END, "Default Microphone")
            
            # Add input devices
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    self.device_listbox.insert(
                        tk.END, 
                        f"{device['name']} (ID: {i}) - {device['max_input_channels']} channels"
                    )
            
            # Select the first device
            self.device_listbox.selection_set(0)
            
            # Update status
            self.status_label.config(
                text=f"Found {self.device_listbox.size() - 1} input devices. Select one and click 'Test'."
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh device list: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
    
    def test_microphone(self):
        """Test the selected microphone"""
        if self.recording:
            return
        
        try:
            # Get selected device
            selection = self.device_listbox.curselection()
            if not selection:
                messagebox.showinfo("Info", "Please select a device first")
                return
            
            device_str = self.device_listbox.get(selection[0])
            device_id = None
            
            # Extract device ID if not default
            if device_str != "Default Microphone":
                try:
                    device_id = int(device_str.split("ID: ")[1].split(")")[0])
                except:
                    messagebox.showerror("Error", "Failed to parse device ID")
                    return
            
            # Get device info
            device_info = sd.query_devices(device_id)
            samplerate = int(device_info['default_samplerate'])
            
            # Clear previous results
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Testing device: {device_info['name']}\n")
            self.results_text.insert(tk.END, f"Sample rate: {samplerate} Hz\n")
            self.results_text.insert(tk.END, f"Channels: {device_info['max_input_channels']}\n")
            
            # Update status
            self.status_label.config(text=f"Recording from {device_info['name']}... Speak now!")
            
            # Get duration
            duration = self.duration_var.get()
            
            # Reset audio data
            self.audio_data = []
            self.recording = True
            
            # Disable test button during recording
            self.test_button.config(state=tk.DISABLED)
            
            # Start recording in a separate thread
            import threading
            threading.Thread(target=self._record_audio, args=(device_id, samplerate, duration)).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test microphone: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
            self.recording = False
            self.test_button.config(state=tk.NORMAL)
    
    def _record_audio(self, device_id, samplerate, duration):
        """Record audio from the selected device"""
        try:
            # Create a callback function to process audio data
            def audio_callback(indata, frames, time_info, status):
                if status:
                    print(f"Status: {status}")
                
                # Copy audio data
                self.audio_data.append(indata.copy())
                
                # Calculate volume level (RMS)
                volume = np.sqrt(np.mean(indata**2))
                
                # Update level meter
                self.root.after(0, lambda: self._update_level_meter(volume))
            
            # Start audio stream
            with sd.InputStream(
                device=device_id,
                channels=1,
                callback=audio_callback,
                samplerate=samplerate,
                blocksize=int(samplerate * 0.1)  # 100ms blocks
            ):
                # Update status
                self.root.after(0, lambda: self.status_label.config(text=f"Recording... {duration} seconds"))
                
                # Wait for duration
                sd.sleep(int(duration * 1000))
            
            # Combine all audio chunks
            if self.audio_data:
                audio_data_combined = np.concatenate(self.audio_data)
                
                # Save to a temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                    sf.write(temp_file.name, audio_data_combined, samplerate)
                    temp_filename = temp_file.name
                
                # Update status
                self.root.after(0, lambda: self.status_label.config(text="Playing back recording..."))
                
                # Play back the recording
                sd.play(audio_data_combined, samplerate)
                sd.wait()
                
                # Update status
                self.root.after(0, lambda: self.status_label.config(text="Test completed successfully!"))
                
                # Update results
                self.root.after(0, lambda: self.results_text.insert(tk.END, f"Recording saved to: {temp_filename}\n"))
                self.root.after(0, lambda: self.results_text.insert(tk.END, f"Audio length: {len(audio_data_combined)/samplerate:.2f} seconds\n"))
                self.root.after(0, lambda: self.results_text.insert(tk.END, "Test completed successfully!"))
            else:
                # Update status
                self.root.after(0, lambda: self.status_label.config(text="No audio recorded!"))
        
        except Exception as e:
            # Update status
            self.root.after(0, lambda: self.status_label.config(text=f"Error: {str(e)}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Recording failed: {str(e)}"))
        
        finally:
            # Reset recording state
            self.recording = False
            
            # Enable test button
            self.root.after(0, lambda: self.test_button.config(state=tk.NORMAL))
    
    def _update_level_meter(self, volume):
        """Update the level meter visualization"""
        # Clear canvas
        self.level_canvas.delete("all")
        
        # Get canvas dimensions
        width = self.level_canvas.winfo_width()
        height = self.level_canvas.winfo_height()
        
        # Ensure we have valid dimensions
        if width <= 1:
            width = 400
        
        # Scale volume for better visualization (0-100 range)
        scaled_volume = min(100, volume * 100) / 100
        
        # Calculate meter width based on volume (0.0 to 1.0)
        meter_width = max(1, min(width - 2, (width - 2) * scaled_volume))
        
        # Determine color based on level
        if scaled_volume < 0.3:
            color = "#4CAF50"  # Green
        elif scaled_volume < 0.7:
            color = "#FFC107"  # Yellow
        else:
            color = "#F44336"  # Red
        
        # Draw meter with a small margin
        if meter_width > 0:
            self.level_canvas.create_rectangle(
                1, 1, meter_width + 1, height - 1,
                fill=color, outline=""
            )
        
        # Add level text
        if width > 50:
            self.level_canvas.create_text(
                width / 2, height / 2,
                text=f"{int(volume * 100)}%",
                fill="#FFFFFF",
                font=("Helvetica", 10, "bold")
            )

def main():
    root = tk.Tk()
    app = MicrophoneTestApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 