#!/usr/bin/env python3
"""
Script to fix the dragon_gui.py file by removing duplicate methods and ensuring proper structure
"""
import re
import os
import sys
from datetime import datetime

# Define the duplicate methods to remove (second occurrences)
DUPLICATE_METHODS = {
    'draw_gradient': [271, 567],
    'update_sensitivity': [792, 1033],
    'start_manual_recording': [2785, 4172],
    'stop_manual_recording': [2833, 4215],
    'transcribe_last_recording': [2892, 4274],
    'process_transcription': [2978, 4360],
    'animate_level_meter': [3028, 4410],
    'refresh_monitor_visualization': [3091, 4473],
    'run_test': [4114, 4856]
}

def fix_dragon_gui(input_file, output_file):
    """Fix the dragon_gui.py file by removing duplicate methods"""
    try:
        print(f"Reading {input_file}...")
        if not os.path.exists(input_file):
            print(f"Error: Input file {input_file} does not exist.")
            return False
        
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"File read successfully. Size: {len(content)} bytes")
        
        # Split the content into lines
        lines = content.split('\n')
        print(f"Total lines: {len(lines)}")
        
        # Create a set to track which methods to remove
        methods_to_remove = set()
        
        # For each duplicate method, mark the second occurrence for removal
        for method_name, line_numbers in DUPLICATE_METHODS.items():
            if len(line_numbers) > 1:
                # Keep the first occurrence, remove the rest
                for line_number in line_numbers[1:]:
                    if line_number - 1 < len(lines):
                        methods_to_remove.add(line_number - 1)  # Adjust for 0-based indexing
                        print(f"Marking method '{method_name}' at line {line_number} for removal")
                    else:
                        print(f"Warning: Line {line_number} is out of range (max: {len(lines)})")
        
        # Create a new list of lines, excluding the duplicate methods
        new_lines = []
        skip_method = False
        
        for i, line in enumerate(lines):
            # Check if this line starts a method to remove
            if i in methods_to_remove:
                # This is the start of a method to remove
                skip_method = True
                print(f"Removing duplicate method at line {i+1}: {line}")
                continue
            
            # If we're skipping a method, check if this line ends the method definition
            if skip_method:
                # Check if this line has less indentation (end of method)
                if line.strip() and not line.startswith('    '):
                    skip_method = False
                # Or if it's a new method definition
                elif line.strip().startswith('def '):
                    skip_method = False
                else:
                    # Still in the method to skip
                    continue
            
            # Add the line to the new content
            new_lines.append(line)
        
        # Join the lines back into a single string
        new_content = '\n'.join(new_lines)
        
        # Write the fixed content to the output file
        print(f"Writing fixed content to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Fixed file saved to {output_file}")
        print(f"Original file size: {len(content)} bytes, New file size: {len(new_content)} bytes")
        print(f"Original line count: {len(lines)}, New line count: {len(new_lines)}")
        return True
    
    except Exception as e:
        print(f"Error fixing file: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Create a timestamp for the backup file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_file = 'src/dragon_gui.py'
    output_file = f'src/dragon_gui_fixed_{timestamp}.py'
    
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