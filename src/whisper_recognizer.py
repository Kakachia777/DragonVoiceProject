#!/usr/bin/env python3
"""
WhisperRecognizer - A class for handling audio recording and transcription using OpenAI's Whisper API
"""

import os
import time
import wave
import tempfile
import threading
import numpy as np
import sounddevice as sd
import logging
from datetime import datetime
import openai

class WhisperRecognizer:
    """
    A class for handling audio recording and transcription using OpenAI's Whisper API
    """
    
    def __init__(self, api_key=None, model="whisper-1"):
        """Initialize the WhisperRecognizer with improved audio handling"""
        # Set API key
        if api_key:
            self.api_key = api_key
            openai.api_key = api_key
        
        # Set model
        self.model = model
        
        # Recording settings
        self.sample_rate = 16000  # 16kHz for Whisper
        self.channels = 1  # Mono
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.recording_thread = None
        self.device = None
        
        # Audio processing settings
        self.chunk_size = 1024  # Audio buffer size
        self.gain = 1.0  # Audio gain
        self.noise_gate = 0.001  # Noise gate threshold
        self.peak_level = 0.0  # Peak level tracking
        self.current_volume = 0.0
        
        # Temporary file for saving audio
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = None
        
        # Initialize sounddevice settings
        try:
            # Get default device info
            default_device = sd.default.device[0]
            device_info = sd.query_devices(default_device, 'input')
            logging.info(f"Default input device: {device_info['name']}")
            
            # Set default parameters based on device capabilities
            self.default_samplerate = int(device_info['default_samplerate'])
            self.default_channels = min(2, device_info['max_input_channels'])
            
            logging.info("Audio system initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing audio system: {str(e)}")
            self.default_samplerate = 44100
            self.default_channels = 1
        
        logging.info("WhisperRecognizer initialized with improved audio handling")
    
    def start_recording(self, device=None, samplerate=None, channels=None):
        """Start recording audio with improved device handling"""
        if self.recording:
            logging.warning("Recording already in progress")
            return False
        
        try:
            # Store device
            self.device = device if device is not None else sd.default.device[0]
            
            # Use provided parameters or defaults
            self.sample_rate = samplerate or self.default_samplerate
            self.channels = channels or self.default_channels
            
            # Get device info and validate parameters
            try:
                device_info = sd.query_devices(self.device, 'input')
                logging.info(f"Using device: {device_info['name']}")
                
                # Validate and adjust sample rate if needed
                supported_samplerate = int(device_info['default_samplerate'])
                if self.sample_rate != supported_samplerate:
                    logging.warning(f"Adjusting sample rate from {self.sample_rate} to {supported_samplerate}")
                    self.sample_rate = supported_samplerate
                
                # Validate and adjust channels if needed
                max_channels = device_info['max_input_channels']
                if self.channels > max_channels:
                    logging.warning(f"Adjusting channels from {self.channels} to {max_channels}")
                    self.channels = max_channels
                
            except Exception as e:
                logging.warning(f"Error querying device {self.device}, using defaults: {e}")
                self.device = None  # Fall back to default device
                self.sample_rate = self.default_samplerate
                self.channels = self.default_channels
            
            # Clear previous audio data
            self.audio_data = []
            self.current_volume = 0.0
            self.peak_level = 0.0
            
            # Set recording flag
            self.recording = True
            
            # Configure and start audio stream
            try:
                self.stream = sd.InputStream(
                    device=self.device,
                    channels=self.channels,
                    samplerate=self.sample_rate,
                    callback=self._audio_callback,
                    blocksize=self.chunk_size,
                    dtype=np.float32
                )
                self.stream.start()
                
                # Start recording thread
                self.recording_thread = threading.Thread(target=self._record_audio)
                self.recording_thread.daemon = True
                self.recording_thread.start()
                
                logging.info(f"Started recording: {self.sample_rate}Hz, {self.channels} channels")
                return True
                
            except Exception as e:
                logging.error(f"Error starting audio stream: {str(e)}")
                self.recording = False
                return False
            
        except Exception as e:
            logging.error(f"Error starting recording: {str(e)}")
            self.recording = False
            return False
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Process audio data from the stream"""
        if status:
            logging.warning(f"Audio status: {status}")
        
        try:
            # Convert to float32 if needed
            if indata.dtype != np.float32:
                indata = indata.astype(np.float32)
            
            # Apply gain
            indata = indata * self.gain
            
            # Calculate volume (RMS)
            volume = float(np.sqrt(np.mean(indata**2)))
            
            # Apply noise gate
            if volume < self.noise_gate:
                indata = np.zeros_like(indata)
                volume = 0.0
            
            # Update peak level with decay
            if volume > self.peak_level:
                self.peak_level = volume
            else:
                # Gradual decay of peak level
                self.peak_level = max(0.0, self.peak_level * 0.95)
            
            # Apply smoothing to current volume
            alpha = 0.1  # Smoothing factor
            self.current_volume = (alpha * volume) + ((1 - alpha) * self.current_volume)
            
            # Only append data if still recording
            if self.recording:
                self.audio_data.append(indata.copy())
            
        except Exception as e:
            logging.error(f"Error in audio callback: {str(e)}")
            # Don't stop recording on callback error, just log it
    
    def _record_audio(self):
        """Monitor the audio stream and handle errors"""
        try:
            while self.recording:
                time.sleep(0.1)
                
                # Check stream health
                if not self.stream.active:
                    logging.error("Audio stream inactive, attempting to restart...")
                    try:
                        self.stream.stop()
                        self.stream.start()
                    except Exception as e:
                        logging.error(f"Failed to restart stream: {str(e)}")
                        self.recording = False
                        break
            
        except Exception as e:
            logging.error(f"Error in recording thread: {str(e)}")
            self.recording = False
        
        finally:
            if self.stream:
                try:
                    self.stream.stop()
                    self.stream.close()
                except:
                    pass
                self.stream = None
    
    def stop_recording(self):
        """Stop recording audio with improved cleanup"""
        if not self.recording:
            logging.warning("No recording in progress")
            return False
        
        try:
            # Set recording flag to False to stop the recording thread
            self.recording = False
            
            # Wait for recording thread to finish
            if self.recording_thread and self.recording_thread.is_alive():
                self.recording_thread.join(timeout=2.0)
            
            # Close the stream if it's still open
            if self.stream and not self.stream.closed:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            # Reset peak level
            self.peak_level = 0.0
            
            logging.info("Recording stopped and cleaned up")
            return True
            
        except Exception as e:
            logging.error(f"Error stopping recording: {str(e)}")
            return False
    
    def set_gain(self, gain):
        """Set the audio gain"""
        self.gain = max(0.0, float(gain))
        logging.debug(f"Audio gain set to {self.gain}")
    
    def set_noise_gate(self, threshold):
        """Set the noise gate threshold"""
        self.noise_gate = max(0.0, float(threshold))
        logging.debug(f"Noise gate set to {self.noise_gate}")
    
    def get_current_volume(self):
        """Get the current audio volume"""
        return self.current_volume
    
    def get_peak_level(self):
        """Get the peak audio level"""
        return self.peak_level
    
    def reset_peak(self):
        """Reset the peak level"""
        self.peak_level = 0.0
    
    def save_audio_to_file(self, filename=None):
        """Save recorded audio to a file"""
        if not self.audio_data:
            logging.warning("No audio data to save")
            return None
        
        try:
            # Create a temporary file if no filename is provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(self.temp_dir, f"recording_{timestamp}.wav")
            
            # Combine all audio chunks
            audio_data = np.concatenate(self.audio_data)
            
            # Save to WAV file
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(self.sample_rate)
                wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())
            
            # Store the filename for later use
            self.temp_file = filename
            
            logging.info(f"Audio saved to {filename}")
            return filename
            
        except Exception as e:
            logging.error(f"Error saving audio: {str(e)}")
            return None
    
    def transcribe_audio(self, audio_file=None, language="en", response_format="text"):
        """Transcribe audio using OpenAI's Whisper API"""
        if not audio_file and self.temp_file:
            audio_file = self.temp_file
        
        if not audio_file:
            logging.warning("No audio file to transcribe")
            return None
        
        if not os.path.exists(audio_file):
            logging.error(f"Audio file not found: {audio_file}")
            return None
        
        try:
            # Open the audio file
            with open(audio_file, "rb") as f:
                # Call the OpenAI API
                transcript = openai.Audio.transcribe(
                    model=self.model,
                    file=f,
                    language=language,
                    response_format=response_format
                )
            
            logging.info(f"Transcription successful: {str(transcript)[:50]}...")
            return transcript
            
        except Exception as e:
            logging.error(f"Error transcribing audio: {str(e)}")
            return None
    
    def get_audio_level(self):
        """Get the current audio level (0.0 to 1.0)"""
        try:
            # Check if we have audio data
            if not hasattr(self, 'audio_data') or not self.audio_data:
                return 0.0
                
            # Get the latest chunk of audio data
            latest_chunk = self.audio_data[-1]
            
            # Calculate volume (RMS)
            if len(latest_chunk) > 0:
                # Apply a noise floor threshold
                noise_floor = 0.005
                
                # Calculate RMS volume
                volume = np.sqrt(np.mean(latest_chunk**2))
                
                # Apply noise floor
                if volume < noise_floor:
                    return 0.0
                    
                # Scale volume to a reasonable range (0.0 to 1.0)
                # This scaling is more conservative to avoid constant 100% readings
                volume = min(1.0, volume * 5)  # Scale by 5 instead of a higher value
                
                return volume
            else:
                return 0.0
                
        except Exception as e:
            logging.error(f"Error getting audio level: {str(e)}")
            return 0.0
    
    def cleanup(self):
        """Clean up resources"""
        # Stop recording if in progress
        if self.recording:
            self.stop_recording()
        
        # Remove temporary files
        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.remove(self.temp_file)
            except:
                pass
        
        # Remove temporary directory
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
            except:
                pass
        
        logging.info("WhisperRecognizer cleaned up")
    
    def get_audio_data(self):
        """Get the latest chunk of audio data for visualization"""
        if not self.recording or not self.audio_data or len(self.audio_data) == 0:
            return None
        
        # Return the most recent chunk of audio data
        return self.audio_data[-1] if self.audio_data else None 