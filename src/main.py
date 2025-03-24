#!/usr/bin/env python3
"""
DragonVoice - Terminal-based Voice Assistant
"""

import os
import sys
import logging
import argparse
import json
import sounddevice as sd
import soundfile as sf
import numpy as np
from pathlib import Path
import openai
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DragonVoice:
    """Terminal-based voice assistant"""
    
    def __init__(self):
        """Initialize the voice assistant"""
        # Create directories
        self.recordings_dir = Path("recordings")
        self.transcriptions_dir = Path("transcriptions")
        self.config_dir = Path("config")
        
        for directory in [self.recordings_dir, self.transcriptions_dir, self.config_dir]:
            directory.mkdir(exist_ok=True)
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize state
        self.recording = False
        self.last_recording = None
        
        logger.info("DragonVoice initialized")
    
    def load_config(self):
        """Load configuration from file"""
        config_file = self.config_dir / "config.json"
        
        if config_file.exists():
            with open(config_file, "r") as f:
                return json.load(f)
        
        # Create default config
        config = {
            "audio": {
                "samplerate": 44100,
                "channels": 1,
                "device": None
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "model": "whisper-1"
            }
        }
        
        # Save default config
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
        
        return config
    
    def record_audio(self, duration=None):
        """
        Record audio
        
        Args:
            duration: Recording duration in seconds (None for manual stop)
        """
        try:
            print("\nRecording... Press Ctrl+C to stop")
            logger.info("Starting audio recording")
            
            # Initialize audio input stream
            audio_data = []
            self.recording = True
            
            def callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio input status: {status}")
                audio_data.append(indata.copy())
                # Print a simple level meter
                level = np.abs(indata).mean()
                meter = "#" * int(level * 50)
                print(f"\rLevel: [{meter:<50}]", end="", flush=True)
            
            with sd.InputStream(
                channels=self.config["audio"]["channels"],
                samplerate=self.config["audio"]["samplerate"],
                device=self.config["audio"]["device"],
                callback=callback
            ):
                if duration:
                    sd.sleep(int(duration * 1000))
                else:
                    try:
                        while self.recording:
                            sd.sleep(100)
                    except KeyboardInterrupt:
                        pass
            
            # Concatenate audio data
            self.last_recording = np.concatenate(audio_data)
            
            # Save recording
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.recordings_dir / f"recording_{timestamp}.wav"
            sf.write(filename, self.last_recording, self.config["audio"]["samplerate"])
            
            print(f"\nRecording saved to {filename}")
            logger.info(f"Recording saved to {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error recording audio: {str(e)}")
            raise
        finally:
            self.recording = False
    
    def transcribe_audio(self, audio_file=None):
        """
        Transcribe audio using Whisper API
        
        Args:
            audio_file: Path to audio file (uses last recording if None)
        """
        try:
            # Check API key
            api_key = self.config["openai"]["api_key"]
            if not api_key:
                raise ValueError("OpenAI API key not configured")
            
            # Set API key
            openai.api_key = api_key
            
            # Get audio file
            if audio_file is None:
                if self.last_recording is None:
                    raise ValueError("No recording available")
                audio_file = self.recordings_dir / "temp.wav"
                sf.write(audio_file, self.last_recording, self.config["audio"]["samplerate"])
            
            print("\nTranscribing audio...")
            logger.info("Starting transcription")
            
            # Send transcription request
            with open(audio_file, "rb") as f:
                response = openai.Audio.transcribe(
                    model=self.config["openai"]["model"],
                    file=f
                )
            
            # Get transcribed text
            text = response["text"]
            
            # Save transcription
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.transcriptions_dir / f"transcription_{timestamp}.txt"
            with open(filename, "w") as f:
                f.write(text)
            
            print(f"\nTranscription: {text}")
            print(f"Saved to {filename}")
            logger.info(f"Transcription saved to {filename}")
            
            return text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise
    
    def configure(self):
        """Configure the application"""
        try:
            print("\nDragonVoice Configuration")
            print("=======================")
            
            # Audio settings
            print("\nAudio Settings:")
            
            # List audio devices
            devices = sd.query_devices()
            print("\nAvailable audio devices:")
            for i, device in enumerate(devices):
                print(f"{i}: {device['name']}")
            
            device = input("\nSelect input device (number or press Enter for default): ")
            if device.strip():
                self.config["audio"]["device"] = int(device)
            
            samplerate = input("Sample rate (press Enter for 44100): ")
            if samplerate.strip():
                self.config["audio"]["samplerate"] = int(samplerate)
            
            channels = input("Channels (press Enter for 1): ")
            if channels.strip():
                self.config["audio"]["channels"] = int(channels)
            
            # OpenAI settings
            print("\nOpenAI Settings:")
            
            api_key = input("API Key (press Enter to keep current): ")
            if api_key.strip():
                self.config["openai"]["api_key"] = api_key
            
            model = input("Model (press Enter for whisper-1): ")
            if model.strip():
                self.config["openai"]["model"] = model
            
            # Save configuration
            config_file = self.config_dir / "config.json"
            with open(config_file, "w") as f:
                json.dump(self.config, f, indent=4)
            
            print("\nConfiguration saved")
            logger.info("Configuration updated")
            
        except Exception as e:
            logger.error(f"Error configuring application: {str(e)}")
            raise
    
    def run(self):
        """Run the application"""
        try:
            print("\nDragonVoice Terminal")
            print("===================")
            
            while True:
                print("\nCommands:")
                print("1. Record")
                print("2. Transcribe last recording")
                print("3. Record and transcribe")
                print("4. Configure")
                print("5. Exit")
                
                choice = input("\nEnter command (1-5): ")
                
                if choice == "1":
                    self.record_audio()
                elif choice == "2":
                    self.transcribe_audio()
                elif choice == "3":
                    filename = self.record_audio()
                    self.transcribe_audio(filename)
                elif choice == "4":
                    self.configure()
                elif choice == "5":
                    print("\nGoodbye!")
                    break
                else:
                    print("\nInvalid command")
        
        except Exception as e:
            logger.error(f"Error running application: {str(e)}")
            raise

def main():
    """Main entry point"""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(description="DragonVoice - Terminal-based Voice Assistant")
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")
        args = parser.parse_args()
        
        # Set log level
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Create and run application
        app = DragonVoice()
        app.run()
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 