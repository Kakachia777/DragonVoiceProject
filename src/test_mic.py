#!/usr/bin/env python3
"""
Test script for microphone functionality in the Dragon Voice Project.
"""

import os
import sys
import time
import logging
import sounddevice as sd
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def list_audio_devices():
    """List all available audio devices"""
    try:
        devices = sd.query_devices()
        print("\nAvailable Audio Devices:")
        print("-" * 80)
        print(f"{'ID':<4} {'Name':<30} {'Input':<6} {'Output':<6} {'Channels':<10} {'Sample Rate':<12}")
        print("-" * 80)
        
        for i, device in enumerate(devices):
            name = device['name']
            inputs = device['max_input_channels']
            outputs = device['max_output_channels']
            samplerate = device['default_samplerate']
            
            print(f"{i:<4} {name[:30]:<30} {inputs:<6} {outputs:<6} {f'In:{inputs},Out:{outputs}':<10} {samplerate:<12.0f}")
        
        print("\nDefault Devices:")
        print(f"Input: {sd.default.device[0]} - {devices[sd.default.device[0]]['name']}")
        print(f"Output: {sd.default.device[1]} - {devices[sd.default.device[1]]['name']}")
        
    except Exception as e:
        print(f"Error listing audio devices: {e}")

def test_microphone(device_id=None, duration=5):
    """Test microphone recording"""
    try:
        # Get device info
        if device_id is not None:
            device_info = sd.query_devices(device_id, 'input')
            print(f"\nTesting microphone: {device_info['name']}")
        else:
            device_id = sd.default.device[0]
            device_info = sd.query_devices(device_id, 'input')
            print(f"\nTesting default microphone: {device_info['name']}")
        
        # Set up parameters
        samplerate = int(device_info['default_samplerate'])
        channels = min(2, device_info['max_input_channels'])
        dtype = np.float32
        
        # Initialize variables for volume calculation
        volume_data = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            
            # Calculate volume (RMS)
            volume = np.sqrt(np.mean(indata**2))
            volume_data.append(volume)
            
            # Print volume meter
            meter_length = 50
            volume_normalized = min(1.0, volume * 5)  # Adjust sensitivity
            bars = int(volume_normalized * meter_length)
            print(f"\rVolume: [{'|' * bars}{' ' * (meter_length - bars)}] {volume:.4f}", end='')
        
        # Record audio
        print(f"\nRecording for {duration} seconds...")
        print("Speak into the microphone to test levels")
        
        with sd.InputStream(
            device=device_id,
            channels=channels,
            samplerate=samplerate,
            dtype=dtype,
            callback=audio_callback
        ):
            time.sleep(duration)
        
        print("\n\nRecording finished")
        
        # Print statistics
        if volume_data:
            print("\nAudio Statistics:")
            print(f"Average volume: {np.mean(volume_data):.4f}")
            print(f"Peak volume: {np.max(volume_data):.4f}")
            print(f"Min volume: {np.min(volume_data):.4f}")
        
    except Exception as e:
        print(f"\nError testing microphone: {e}")

def main():
    """Main function"""
    print("Dragon Voice Project - Microphone Test")
    print("=====================================")
    
    # List available devices
    list_audio_devices()
    
    # Ask user which device to test
    try:
        choice = input("\nEnter device ID to test (press Enter for default): ").strip()
        device_id = int(choice) if choice else None
        
        # Test the selected microphone
        test_microphone(device_id)
        
    except ValueError:
        print("Invalid device ID. Using default device.")
        test_microphone()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 