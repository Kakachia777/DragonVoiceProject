#!/usr/bin/env python3
"""
DragonVoiceProject - Voice Assistant Launcher

This script provides an easy way to launch the DragonVoiceProject voice assistant
and related components. It can launch both the chatbot windows and the voice assistant
in a single command, making it easier to set up the system.

Usage:
    python launch_assistant.py [--chatbots COUNT] [--mode {direct,dragon}]

Options:
    --chatbots COUNT         Number of chatbot windows to launch (default: all)
    --mode {direct,dragon}   Voice input mode (default: dragon)

Requirements:
    - All dependencies for the DragonVoiceProject
"""

import os
import sys
import time
import argparse
import subprocess
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('DragonVoiceProject')

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="DragonVoiceProject Voice Assistant Launcher")
    
    parser.add_argument("--chatbots", type=int, default=11,
                      help="Number of chatbot windows to launch (default: all)")
    
    parser.add_argument("--mode", choices=["direct", "dragon"], default="dragon",
                      help="Voice input mode (default: dragon)")
    
    parser.add_argument("--config-only", action="store_true",
                      help="Only run the configuration tool without launching")
    
    parser.add_argument("--skip-launch", action="store_true",
                      help="Skip launching chatbot windows")
    
    parser.add_argument("--screens", type=int, default=0,
                      help="Number of screens to configure for (default: auto-detect)")
    
    return parser.parse_args()

def launch_chatbots(count):
    """Launch chatbot windows for testing."""
    logger.info(f"Launching {count} chatbot windows")
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "launch_chatbots.py")
    
    if not os.path.exists(script_path):
        logger.error(f"Chatbot launcher script not found: {script_path}")
        return False
    
    try:
        subprocess.Popen([sys.executable, script_path, "--count", str(count)])
        logger.info("Chatbot launcher started")
        return True
    except Exception as e:
        logger.error(f"Error launching chatbots: {e}")
        return False

def run_configuration(screens):
    """Run the multi-screen configuration tool."""
    logger.info("Starting multi-screen configuration")
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "multi_screen_config.py")
    
    if not os.path.exists(script_path):
        logger.error(f"Configuration script not found: {script_path}")
        return False
    
    try:
        cmd = [sys.executable, script_path]
        if screens > 0:
            cmd.extend(["--screens", str(screens)])
        
        # Run configuration tool and wait for it to complete
        process = subprocess.Popen(cmd)
        process.wait()
        
        if process.returncode == 0:
            logger.info("Configuration completed successfully")
            return True
        else:
            logger.error(f"Configuration failed with code {process.returncode}")
            return False
    
    except Exception as e:
        logger.error(f"Error running configuration: {e}")
        return False

def start_voice_assistant(mode):
    """Start the voice assistant."""
    logger.info(f"Starting voice assistant in {mode} mode")
    
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_assistant.py")
    
    if not os.path.exists(script_path):
        logger.error(f"Voice assistant script not found: {script_path}")
        return False
    
    try:
        subprocess.Popen([sys.executable, script_path, "--mode", mode])
        logger.info("Voice assistant started")
        return True
    except Exception as e:
        logger.error(f"Error starting voice assistant: {e}")
        return False

def main():
    """Main function to run the launcher."""
    args = parse_arguments()
    
    print("\n" + "=" * 60)
    print("DragonVoiceProject - Voice Assistant Launcher")
    print("=" * 60)
    
    # First, run configuration if requested
    if args.config_only:
        run_configuration(args.screens)
        return
    
    # Launch chatbot windows if not skipped
    if not args.skip_launch:
        print("\nStep 1: Launching chatbot windows")
        success = launch_chatbots(args.chatbots)
        
        if success:
            print("Chatbot windows being launched. Wait for them to open...")
            time.sleep(5)  # Give time for windows to open
        else:
            print("Failed to launch chatbot windows. Check the log for details.")
            if input("Continue anyway? (y/n): ").lower() != 'y':
                return
    
    # Run configuration tool
    print("\nStep 2: Configuring chatbot positions")
    if input("Would you like to configure chatbot positions now? (y/n): ").lower() == 'y':
        success = run_configuration(args.screens)
        
        if not success:
            print("Configuration failed. Check the log for details.")
            if input("Continue anyway? (y/n): ").lower() != 'y':
                return
    
    # Start voice assistant
    print("\nStep 3: Starting voice assistant")
    if input("Start the voice assistant now? (y/n): ").lower() == 'y':
        success = start_voice_assistant(args.mode)
        
        if success:
            print("\nVoice assistant started!")
            print("\nTo use the voice assistant:")
            if args.mode == "direct":
                print("1. Copy text with the command prefix to clipboard")
                print("2. The assistant will distribute it to all configured chatbots")
            else:
                print("1. Dictate with Dragon Medical One using the command prefix")
                print("2. Dragon will send the text to the assistant")
                print("3. The assistant will distribute it to all configured chatbots")
            
            print("\nThe voice assistant is running in the background.")
            print("Press Ctrl+C in the voice assistant window to stop it.")
        else:
            print("Failed to start voice assistant. Check the log for details.")
    
    print("\n" + "=" * 60)
    print("Setup complete")
    print("=" * 60)

if __name__ == "__main__":
    main() 