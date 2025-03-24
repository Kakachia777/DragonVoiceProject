#!/usr/bin/env python3
"""
Final script to fix the dragon_gui.py file by removing all duplicate methods
"""
import re
import os
import sys
from datetime import datetime

# List of known duplicate methods to keep only the first occurrence
DUPLICATE_METHODS = [
    'draw_gradient',
    'update_sensitivity',
    'start_manual_recording',
    'stop_manual_recording',
    'transcribe_last_recording',
    'process_transcription',
    'animate_level_meter',
    'refresh_monitor_visualization',
    'run_test',
    'update_level',
    'record_audio',
    'audio_callback',
    'play_audio',
    'update_playback_progress'
]

def fix_dragon_gui(input_file, output_file):
    """Fix the dragon_gui.py file by removing all duplicate methods"""
    try:
        print(f"Reading {input_file}...")
        if not os.path.exists(input_file):
            print(f"Error: Input file {input_file} does not exist.")
            return False
        
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        print(f"File read successfully. Size: {original_size} bytes")
        
        # Find all method definitions
        method_pattern = re.compile(r'^(\s+)def\s+(\w+)\s*\(', re.MULTILINE)
        methods = list(method_pattern.finditer(content))
        
        # Track method occurrences
        method_occurrences = {}
        positions_to_remove = []
        
        for match in methods:
            indentation = match.group(1)
            method_name = match.group(2)
            start_pos = match.start()
            line_number = content[:start_pos].count('\n') + 1
            
            # Check if this is a duplicate method we want to handle
            if method_name in DUPLICATE_METHODS:
                if method_name not in method_occurrences:
                    method_occurrences[method_name] = 1
                else:
                    method_occurrences[method_name] += 1
                    
                    # This is a duplicate occurrence, mark it for removal
                    end_pos = find_method_end(content, start_pos, indentation)
                    positions_to_remove.append((start_pos, end_pos, method_name, line_number))
        
        # Sort positions in reverse order to avoid position shifts
        positions_to_remove.sort(reverse=True, key=lambda x: x[0])
        
        # Remove the duplicate methods
        for start_pos, end_pos, method_name, line_number in positions_to_remove:
            print(f"Removing duplicate method '{method_name}' at line {line_number}")
            content = content[:start_pos] + content[end_pos:]
        
        # Write the fixed content to the output file
        print(f"Writing fixed content to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed file saved to {output_file}")
        print(f"Original file size: {original_size} bytes, Fixed file size: {len(content)} bytes")
        return True
    
    except Exception as e:
        print(f"Error fixing file: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def find_method_end(content, start_pos, indentation):
    """Find the end position of a method definition"""
    lines = content[start_pos:].split('\n')
    
    # Skip the first line (method definition)
    end_pos = start_pos + len(lines[0]) + 1
    
    # Check each subsequent line
    for i, line in enumerate(lines[1:], 1):
        # If we find a line with the same or less indentation, we've reached the end
        if line.strip() and not line.startswith(indentation):
            break
        
        end_pos += len(line) + 1  # Add 1 for the newline
    
    return end_pos

if __name__ == "__main__":
    # Create a timestamp for the output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Use the file path provided as a command-line argument, or default to dragon_gui.py
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'src/dragon_gui.py'
    output_file = f'src/dragon_gui_final_{timestamp}.py'
    
    # Fix the file
    success = fix_dragon_gui(input_file, output_file)
    
    if success:
        print("File fixed successfully!")
        
        # Verify the fixed file exists
        if os.path.exists(output_file):
            print(f"Verified: {output_file} exists")
            print(f"File size: {os.path.getsize(output_file)} bytes")
        else:
            print(f"Error: {output_file} was not created")
    else:
        print("Failed to fix the file.") 