#!/usr/bin/env python3
"""
Whisper API Integration for Dragon Voice Project

This module provides integration with OpenAI's Whisper API for high-quality
speech recognition. It handles audio recording, processing, and transcription.
"""

import os
import time
import wave
import json
import tempfile
import threading
import logging
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any, Union
from pathlib import Path

try:
    import sounddevice as sd
    import soundfile as sf
    from openai import OpenAI
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please install: pip install openai sounddevice soundfile numpy")
    raise

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("whisper_integration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WhisperRecognizer:
    """Handles audio recording and transcription using OpenAI's Whisper API"""
    
    def __init__(self, api_key: str = None, model: str = "whisper-1", base_url: str = None):
        """
        Initialize the WhisperRecognizer
        
        Args:
            api_key: OpenAI API key
            model: Whisper model to use
            base_url: Optional API base URL (for using alternative endpoints)
        """
        # Set up OpenAI client
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("No API key provided. Set OPENAI_API_KEY env var or pass as argument")
        
        # Initialize OpenAI client with optional base URL
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
        
        self.model = model
        
        # Recording settings
        self.sample_rate = 16000  # Required for Whisper
        self.channels = 1  # Mono audio
        self.dtype = np.float32
        
        # State variables
        self.recording = False
        self.stream = None
        self.audio_data = []
        self.current_volume = 0.0
        
        # Audio processing
        self.chunk_size = 1024
        self.gain = 1.0
        self.noise_gate = 0.01
        
        # Create temp directory for audio files
        self.temp_dir = Path(tempfile.mkdtemp())
        logger.info(f"Using temporary directory: {self.temp_dir}")
        
        # Initialize audio device settings
        self._init_audio_device()
    
    def _init_audio_device(self):
        """Initialize audio device settings"""
        try:
            # Get default input device
            device_id = sd.default.device[0]
            device_info = sd.query_devices(device_id, 'input')
            
            logger.info(f"Using input device: {device_info['name']}")
            logger.info(f"Sample rate: {self.sample_rate} Hz")
            logger.info(f"Channels: {self.channels}")
            
        except Exception as e:
            logger.error(f"Error initializing audio device: {e}")
            raise
    
    def start_recording(self, device: Optional[int] = None) -> bool:
        """
        Start recording audio
        
        Args:
            device: Optional device ID to use for recording
            
        Returns:
            bool: True if recording started successfully
        """
        if self.recording:
            logger.warning("Already recording")
            return False
        
        try:
            # Configure input stream
            self.stream = sd.InputStream(
                device=device,
                channels=self.channels,
                samplerate=self.sample_rate,
                dtype=self.dtype,
                blocksize=self.chunk_size,
                callback=self._audio_callback
            )
            
            # Clear previous recording
            self.audio_data = []
            self.current_volume = 0.0
            
            # Start recording
            self.stream.start()
            self.recording = True
            
            logger.info("Recording started")
            return True
            
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            self.recording = False
            return False
    
    def stop_recording(self) -> bool:
        """
        Stop recording audio
        
        Returns:
            bool: True if recording stopped successfully
        """
        if not self.recording:
            logger.warning("Not recording")
            return False
        
        try:
            self.recording = False
            
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            logger.info("Recording stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping recording: {e}")
            return False
    
    def _audio_callback(self, indata: np.ndarray, frames: int, 
                       time_info: Dict, status: Any) -> None:
        """Process audio data from the input stream"""
        if status:
            logger.warning(f"Audio stream status: {status}")
        
        try:
            # Apply gain
            data = indata * self.gain
            
            # Calculate current volume (RMS)
            rms = np.sqrt(np.mean(data**2))
            
            # Apply noise gate
            if rms < self.noise_gate:
                data = np.zeros_like(data)
                rms = 0.0
            
            # Update volume with smoothing
            alpha = 0.1
            self.current_volume = (alpha * rms) + ((1 - alpha) * self.current_volume)
            
            # Store audio data if recording
            if self.recording:
                self.audio_data.append(data.copy())
                
        except Exception as e:
            logger.error(f"Error in audio callback: {e}")
    
    def save_audio_to_file(self) -> Optional[str]:
        """
        Save recorded audio to a temporary WAV file
        
        Returns:
            str: Path to saved audio file, or None if failed
        """
        if not self.audio_data:
            logger.warning("No audio data to save")
            return None
        
        try:
            # Combine all audio chunks
            audio_data = np.concatenate(self.audio_data)
            
            # Generate temp file path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_file = self.temp_dir / f"recording_{timestamp}.wav"
            
            # Save as WAV file
            sf.write(
                temp_file,
                audio_data,
                self.sample_rate,
                subtype='PCM_16'
            )
            
            logger.info(f"Audio saved to: {temp_file}")
            return str(temp_file)
            
        except Exception as e:
            logger.error(f"Error saving audio: {e}")
            return None
    
    def transcribe_audio(self, audio_file: str, **kwargs) -> Optional[Dict]:
        """
        Transcribe audio using Whisper API
        
        Args:
            audio_file: Path to audio file
            **kwargs: Additional parameters for the Whisper API
                - language: ISO language code
                - prompt: Optional text to guide transcription
                - response_format: json, text, srt, verbose_json, or vtt
                - temperature: Sampling temperature (0.0 to 1.0)
                - timestamp_granularities: List of 'word' and/or 'segment'
        
        Returns:
            dict: Transcription result or None if failed
        """
        try:
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            logger.info(f"Transcribing audio file: {audio_file}")
            
            # Open audio file
            with open(audio_file, 'rb') as f:
                # Call Whisper API
                response = self.client.audio.transcriptions.create(
                    model=self.model,
                    file=f,
                    **kwargs
                )
            
            logger.info("Transcription completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    def translate_audio(self, audio_file: str, **kwargs) -> Optional[Dict]:
        """
        Translate audio to English using Whisper API
        
        Args:
            audio_file: Path to audio file
            **kwargs: Additional parameters for the Whisper API
                - prompt: Optional text to guide translation
                - response_format: json, text, srt, verbose_json, or vtt
                - temperature: Sampling temperature (0.0 to 1.0)
        
        Returns:
            dict: Translation result or None if failed
        """
        try:
            if not os.path.exists(audio_file):
                raise FileNotFoundError(f"Audio file not found: {audio_file}")
            
            logger.info(f"Translating audio file: {audio_file}")
            
            # Open audio file
            with open(audio_file, 'rb') as f:
                # Call Whisper API
                response = self.client.audio.translations.create(
                    model=self.model,
                    file=f,
                    **kwargs
                )
            
            logger.info("Translation completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error translating audio: {e}")
            return None
    
    def cleanup(self):
        """Clean up temporary files and resources"""
        try:
            # Stop any ongoing recording
            if self.recording:
                self.stop_recording()
            
            # Remove temp directory and contents
            if self.temp_dir.exists():
                for file in self.temp_dir.glob("*"):
                    file.unlink()
                self.temp_dir.rmdir()
                
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Example usage
if __name__ == "__main__":
    # This is just for testing the module directly
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        exit(1)
    
    recognizer = WhisperRecognizer(api_key=api_key)
    print("Say something...")
    
    text = recognizer.transcribe_audio(max_seconds=10)
    print(f"Transcription: {text}")
    
    recognizer.cleanup() 