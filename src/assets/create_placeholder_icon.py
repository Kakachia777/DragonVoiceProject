#!/usr/bin/env python3
"""
Create placeholder icons for the DragonVoiceProject GUI.

This script generates simple placeholder icons for the application
when no actual icons are available. It creates:
1. A dragon_icon.ico file for the application icon
2. A dragon_logo.png file for the application logo

Requirements:
- PIL (Pillow)
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_app_icon():
    """Create a simple application icon."""
    # Create a transparent image
    img = Image.new('RGBA', (256, 256), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a blue circle background
    draw.ellipse((16, 16, 240, 240), fill=(30, 136, 229, 255))
    
    # Draw a stylized "D" in white
    try:
        # Try to use a nice font if available
        font = ImageFont.truetype("Arial Bold", 160)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw the text
    draw.text((85, 40), "D", fill=(255, 255, 255, 255), font=font)
    
    # Save as ICO
    img.save("dragon_icon.ico")
    
    # Also save as PNG
    img.save("dragon_icon.png")
    
    print(f"Created application icon: dragon_icon.ico and dragon_icon.png")

def create_app_logo():
    """Create a simple application logo."""
    # Create a transparent image
    img = Image.new('RGBA', (512, 512), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a gradient-like background (simulated with concentric circles)
    colors = [
        (25, 118, 210, 255),  # Darker blue
        (30, 136, 229, 255),  # Medium blue
        (33, 150, 243, 255)   # Lighter blue
    ]
    
    # Draw concentric circles
    for i, color in enumerate(colors):
        size = 420 - i * 40
        offset = (512 - size) // 2
        draw.ellipse((offset, offset, offset + size, offset + size), fill=color)
    
    # Draw a stylized "D" in white
    try:
        # Try to use a nice font if available
        font = ImageFont.truetype("Arial Bold", 280)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw the text
    draw.text((170, 100), "D", fill=(255, 255, 255, 255), font=font)
    
    # Save as PNG
    img.save("dragon_logo.png")
    
    print(f"Created application logo: dragon_logo.png")

def main():
    """Main function to create all icons."""
    # Get the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the script directory
    os.chdir(script_dir)
    
    # Create the icons
    create_app_icon()
    create_app_logo()
    
    print("All icons created successfully!")

if __name__ == "__main__":
    main() 