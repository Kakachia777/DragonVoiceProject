#!/usr/bin/env python3
"""
Script to check for multiple class definitions in a Python file
"""
import re
import sys

def check_classes(file_path):
    """Check for multiple class definitions in a Python file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all class definitions
    class_pattern = re.compile(r'^class\s+(\w+)', re.MULTILINE)
    classes = class_pattern.finditer(content)
    
    # Count occurrences of each class
    class_counts = {}
    class_positions = {}
    
    for match in classes:
        class_name = match.group(1)
        position = match.start()
        line_number = content[:position].count('\n') + 1
        
        if class_name not in class_counts:
            class_counts[class_name] = 0
            class_positions[class_name] = []
        
        class_counts[class_name] += 1
        class_positions[class_name].append(line_number)
    
    # Print class information
    print(f"Analyzing file: {file_path}")
    print("Classes found:")
    print("=" * 50)
    
    for class_name, count in class_counts.items():
        print(f"Class '{class_name}' appears {count} times at lines: {class_positions[class_name]}")
    
    # Print total class count
    print(f"\nTotal classes found: {len(class_counts)}")
    print(f"Total class definitions: {sum(class_counts.values())}")

if __name__ == "__main__":
    # Use the file path provided as a command-line argument, or default to dragon_gui.py
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'src/dragon_gui.py'
    check_classes(file_path) 