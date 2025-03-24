#!/usr/bin/env python3
"""
Comprehensive script to fix the dragon_gui.py file by removing all duplicate methods
"""
import re
import os
import sys
from datetime import datetime

def find_duplicate_methods(content):
    """Find all duplicate method definitions in the content"""
    # Find all method definitions
    method_pattern = re.compile(r'^(\s+)def\s+(\w+)\s*\(', re.MULTILINE)
    methods = method_pattern.finditer(content)
    
    # Track method definitions
    method_positions = {}
    
    for match in methods:
        indentation = match.group(1)
        method_name = match.group(2)
        position = match.start()
        line_number = content[:position].count('\n') + 1
        
        if method_name not in method_positions:
            method_positions[method_name] = []
        
        method_positions[method_name].append((line_number, position, indentation))
    
    # Find duplicates
    duplicates = {}
    for method_name, positions in method_positions.items():
        if len(positions) > 1:
            # Keep the first occurrence, mark the rest for removal
            duplicates[method_name] = positions[1:]
    
    return duplicates

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

def fix_dragon_gui(input_file, output_file):
    """Fix the dragon_gui.py file by removing all duplicate methods"""
    try:
        print(f"Reading {input_file}...")
        if not os.path.exists(input_file):
            print(f"Error: Input file {input_file} does not exist.")
            return False
        
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"File read successfully. Size: {len(content)} bytes")
        
        # Find duplicate methods
        duplicates = find_duplicate_methods(content)
        
        if not duplicates:
            print("No duplicate methods found.")
            return True
        
        print(f"Found {sum(len(positions) for positions in duplicates.values())} duplicate methods to remove:")
        for method_name, positions in duplicates.items():
            print(f"  - '{method_name}' has {len(positions)} duplicates at lines: {[pos[0] for pos in positions]}")
        
        # Remove duplicates (in reverse order to avoid position shifts)
        positions_to_remove = []
        for method_name, positions in duplicates.items():
            for line_number, start_pos, indentation in positions:
                end_pos = find_method_end(content, start_pos, indentation)
                positions_to_remove.append((start_pos, end_pos))
        
        # Sort positions in reverse order
        positions_to_remove.sort(reverse=True)
        
        # Remove the duplicate methods
        for start_pos, end_pos in positions_to_remove:
            line_number = content[:start_pos].count('\n') + 1
            method_line = content[start_pos:content.find('\n', start_pos)]
            print(f"Removing duplicate method at line {line_number}: {method_line.strip()}")
            content = content[:start_pos] + content[end_pos:]
        
        # Write the fixed content to the output file
        print(f"Writing fixed content to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Fixed file saved to {output_file}")
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
    output_file = f'src/dragon_gui_fixed_comprehensive_{timestamp}.py'
    
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