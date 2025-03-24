#!/usr/bin/env python3
"""
Script to create a clean version of dragon_gui.py by extracting only the essential parts
"""
import re
import os
from datetime import datetime

def extract_methods(content):
    """Extract all method definitions from the content"""
    # Find all method definitions
    method_pattern = re.compile(r'^(\s+)def\s+(\w+)\s*\(', re.MULTILINE)
    methods = method_pattern.finditer(content)
    
    # Track method definitions
    method_info = {}
    
    for match in methods:
        indentation = match.group(1)
        method_name = match.group(2)
        start_pos = match.start()
        line_number = content[:start_pos].count('\n') + 1
        
        # Find the end of the method
        end_pos = find_method_end(content, start_pos, indentation)
        method_code = content[start_pos:end_pos]
        
        if method_name not in method_info:
            method_info[method_name] = (line_number, method_code)
    
    return method_info

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

def extract_class_definition(content):
    """Extract the class definition from the content"""
    # Find the class definition
    class_pattern = re.compile(r'^class\s+DragonVoiceGUI', re.MULTILINE)
    match = class_pattern.search(content)
    
    if not match:
        return None
    
    class_start = match.start()
    
    # Find the end of the class definition (next class or end of file)
    next_class = re.compile(r'^class\s+', re.MULTILINE).search(content, class_start + 1)
    if next_class:
        class_end = next_class.start()
    else:
        class_end = len(content)
    
    return content[class_start:class_end]

def extract_imports_and_constants(content):
    """Extract imports and constants from the content"""
    # Find the class definition to know where to stop
    class_pattern = re.compile(r'^class\s+DragonVoiceGUI', re.MULTILINE)
    match = class_pattern.search(content)
    
    if not match:
        return ""
    
    return content[:match.start()]

def extract_main_function(content):
    """Extract the main function from the content"""
    # Find the main function
    main_pattern = re.compile(r'^def\s+main\s*\(', re.MULTILINE)
    match = main_pattern.search(content)
    
    if not match:
        return None
    
    main_start = match.start()
    
    # Find the end of the main function
    if_name_pattern = re.compile(r'^if\s+__name__\s*==\s*[\'"]__main__[\'"]', re.MULTILINE)
    if_name_match = if_name_pattern.search(content, main_start)
    
    if if_name_match:
        main_end = if_name_match.start()
    else:
        main_end = len(content)
    
    main_function = content[main_start:main_end]
    
    # Also get the if __name__ == "__main__" block
    if if_name_match:
        if_name_start = if_name_match.start()
        if_name_end = len(content)
        if_name_block = content[if_name_start:if_name_end]
        return main_function + "\n\n" + if_name_block
    
    return main_function

def create_clean_file(input_file, output_file):
    """Create a clean version of dragon_gui.py"""
    try:
        print(f"Reading {input_file}...")
        if not os.path.exists(input_file):
            print(f"Error: Input file {input_file} does not exist.")
            return False
        
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"File read successfully. Size: {len(content)} bytes")
        
        # Extract imports and constants
        imports_and_constants = extract_imports_and_constants(content)
        print(f"Extracted imports and constants: {len(imports_and_constants)} bytes")
        
        # Extract the class definition
        class_definition = extract_class_definition(content)
        if not class_definition:
            print("Error: Could not find DragonVoiceGUI class definition.")
            return False
        
        print(f"Extracted class definition: {len(class_definition)} bytes")
        
        # Extract the main function
        main_function = extract_main_function(content)
        if not main_function:
            print("Warning: Could not find main function.")
            main_function = ""
        
        print(f"Extracted main function: {len(main_function)} bytes")
        
        # Create the clean content
        clean_content = imports_and_constants + "\n\n" + class_definition + "\n\n" + main_function
        
        # Write the clean content to the output file
        print(f"Writing clean content to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(clean_content)
        
        print(f"Clean file saved to {output_file}")
        print(f"Original file size: {len(content)} bytes, Clean file size: {len(clean_content)} bytes")
        return True
    
    except Exception as e:
        print(f"Error creating clean file: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Create a timestamp for the output file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    input_file = 'src/dragon_gui.py'
    output_file = f'src/dragon_gui_clean_{timestamp}.py'
    
    # Create the clean file
    success = create_clean_file(input_file, output_file)
    
    if success:
        print("Clean file created successfully!")
        
        # Verify the clean file exists
        if os.path.exists(output_file):
            print(f"Verified: {output_file} exists")
            print(f"File size: {os.path.getsize(output_file)} bytes")
        else:
            print(f"Error: {output_file} was not created")
    else:
        print("Failed to create clean file.") 