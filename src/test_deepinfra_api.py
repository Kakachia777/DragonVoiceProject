#!/usr/bin/env python3
"""
Test script to verify Deepinfra API key independently
"""

import os
import time
import numpy as np
import sounddevice as sd
import soundfile as sf
import requests

def record_audio(duration=5, sample_rate=16000):
    """Record audio for specified duration"""
    print(f"\nRecording for {duration} seconds...")
    print("Speak now...")
    
    # Record audio
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.float32
    )
    sd.wait()  # Wait until recording is finished
    print("Recording finished!")
    
    # Save to file
    audio_file = "test_audio.mp3"
    sf.write(audio_file, recording, sample_rate)
    print(f"Saved recording to {audio_file}")
    
    return audio_file

def test_deepinfra_api():
    """Test Deepinfra API key and connection"""
    print("\nTesting Deepinfra API Connection...")
    print("-" * 50)
    
    # Record audio first
    audio_file = record_audio(duration=5)
    
    # Use provided API key
    api_key = "j3ydNXEmQFyDKwl5mWxSzcvdZcTLJw1t"
    print(f"\nUsing API Key: {api_key}")
    
    # Set up API request
    base_url = "https://api.deepinfra.com/v1/inference/openai/whisper-large-v3"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "task": "transcribe",
        "language": "en",  # Specify English language
        "temperature": 0,
        "chunk_level": "segment",
        "chunk_length_s": 30
    }
    
    try:
        print(f"\nUsing audio file: {audio_file}")
        print(f"File size: {os.path.getsize(audio_file)} bytes")
        
        files = {
            'audio': (audio_file, open(audio_file, 'rb'), 'audio/mpeg')
        }
        
        print("\nMaking API request...")
        response = requests.post(base_url, headers=headers, data=data, files=files)
        
        # Check response
        if response.status_code == 200:
            print("\n✅ API Key Test Successful!")
            print("Response:", response.json())
            return True
        else:
            print("\n❌ API Key Test Failed!")
            print(f"Status Code: {response.status_code}")
            print("Response:", response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print("\n❌ API Key Test Failed!")
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print("Response:", e.response.text)
        return False
        
    finally:
        # Cleanup
        if 'files' in locals():
            files['audio'][1].close()
        # Remove the audio file after testing
        if os.path.exists(audio_file):
            os.remove(audio_file)
            print("\nCleaned up test audio file")

if __name__ == "__main__":
    test_deepinfra_api() 