#!/usr/bin/env python3
"""
Script to analyze duplicate method definitions in dragon_gui.py
"""
import re
import sys

def find_duplicate_methods(file_path):
    """Find duplicate method definitions in a Python file"""
    with open(file_path, 'r', encoding='utf-8') as f:
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
        method_positions[method_name].append(line_number)
    
    # Print duplicate methods
    print(f"Analyzing file: {file_path}")
    print("Duplicate methods found:")
    print("=" * 50)
    
    duplicates_found = False
    for method_name, count in method_counts.items():
        if count > 1:
            duplicates_found = True
            print(f"Method '{method_name}' appears {count} times at lines: {method_positions[method_name]}")
    
    if not duplicates_found:
        print("No duplicate methods found.")
    
    # Print total method count
    print(f"\nTotal methods found: {len(method_counts)}")
    return duplicates_found

if __name__ == "__main__":
    # Use the file path provided as a command-line argument, or default to dragon_gui.py
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'src/dragon_gui.py'
    find_duplicate_methods(file_path) 