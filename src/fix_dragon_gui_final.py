#!/usr/bin/env python3
"""
Final script to fix the dragon_gui.py file by removing all duplicate methods
This script takes a more direct approach by identifying specific duplicate methods
"""
import os
import sys
import re
from datetime import datetime

# Define the duplicate methods to remove (with their line ranges)
DUPLICATE_METHODS = [
    # Method name, start line, end line (inclusive)
    ('draw_gradient', 567, 590),
    ('update_sensitivity', 1033, 1050),
    ('start_manual_recording', 4112, 4153),
    ('stop_manual_recording', 4154, 4211),
    ('transcribe_last_recording', 4212, 4296),
    ('process_transcription', 4297, 4345),
    ('animate_level_meter', 4346, 4407),
    ('refresh_monitor_visualization', 4408, 4472),
    ('run_test', 4790, 4855)
]

def fix_dragon_gui(input_file, output_file):
    """Fix the dragon_gui.py file by removing specific duplicate methods"""
    try:
        print(f"Reading {input_file}...")
        if not os.path.exists(input_file):
            print(f"Error: Input file {input_file} does not exist.")
            return False
        
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"File read successfully. Total lines: {len(lines)}")
        
        # Create a set of line numbers to remove
        lines_to_remove = set()
        for method_name, start_line, end_line in DUPLICATE_METHODS:
            # Adjust for 0-based indexing
            start_idx = start_line - 1
            end_idx = end_line - 1
            
            # Validate line ranges
            if start_idx < 0 or end_idx >= len(lines):
                print(f"Warning: Invalid line range for {method_name}: {start_line}-{end_line}")
                continue
            
            # Add lines to remove set
            for i in range(start_idx, end_idx + 1):
                lines_to_remove.add(i)
            
            print(f"Marked method '{method_name}' at lines {start_line}-{end_line} for removal")
        
        # Create new content without the duplicate methods
        new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
        
        # Write the fixed content to the output file
        print(f"Writing fixed content to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        # Now check for any remaining duplicates
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all method definitions
        method_pattern = re.compile(r'^\s+def\s+(\w+)\s*\(', re.MULTILINE)
        methods = method_pattern.finditer(content)
        
        # Count occurrences of each method
        method_counts = {}
        method_positions = {}
        
        for match in methods:
            method_name = match.group(1)
            position = match.start()
            line_number = content[:position].count('\n') + 1
            
            if method_name not in method_counts:
                method_counts[method_name] = 0
                method_positions[method_name] = []
            
            method_counts[method_name] += 1
            method_positions[method_name].append((line_number, position))
        
        # Find duplicates
        duplicates_found = False
        for method_name, count in method_counts.items():
            if count > 1:
                duplicates_found = True
                print(f"Still found duplicate method: '{method_name}' appears {count} times at lines: {[pos[0] for pos in method_positions[method_name]]}")
                
                # Remove all but the first occurrence
                positions_to_remove = sorted(method_positions[method_name][1:], reverse=True)
                
                for line_number, position in positions_to_remove:
                    # Find the end of the method
                    lines = content[position:].split('\n')
                    
                    # Get the indentation of the method definition
                    indentation_match = re.match(r'^(\s+)', lines[0])
                    if not indentation_match:
                        print(f"Warning: Could not determine indentation for method at line {line_number}")
                        continue
                    
                    indentation = indentation_match.group(1)
                    
                    # Skip the first line (method definition)
                    end_pos = position + len(lines[0]) + 1
                    
                    # Check each subsequent line
                    for i, line in enumerate(lines[1:], 1):
                        # If we find a line with the same or less indentation, we've reached the end
                        if line.strip() and not line.startswith(indentation):
                            break
                        
                        end_pos += len(line) + 1  # Add 1 for the newline
                    
                    print(f"Removing duplicate method '{method_name}' at line {line_number}")
                    content = content[:position] + content[end_pos:]
        
        # If we found and removed more duplicates, write the file again
        if duplicates_found:
            print("Writing file again after removing additional duplicates...")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"Fixed file saved to {output_file}")
        print(f"Original line count: {len(lines)}, New line count: {len(content.split(chr(10)))}")
        print(f"Removed {len(lines) - len(content.split(chr(10)))} lines")
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
    output_file = f'src/dragon_gui_fixed_final_{timestamp}.py'
    
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