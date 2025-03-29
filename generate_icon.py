from PIL import Image, ImageDraw, ImageFont
import os

def create_dragon_icon(output_filename="dragon_icon.ico", size=256):
    """
    Create a simple dragon icon.
    """
    # Create a new image with a white background
    img = Image.new('RGBA', (size, size), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Dragon color (green)
    dragon_color = (34, 139, 34)  # Forest Green
    
    # Draw a simple dragon silhouette
    # Head
    draw.ellipse((size//3, size//4, size*2//3, size//2), fill=dragon_color)
    
    # Body
    draw.ellipse((size//6, size//2, size*5//6, size*3//4), fill=dragon_color)
    
    # Tail
    points = [
        (size//6, size*5//8),  # Start at body
        (size//12, size*3//4),  # Curve out
        (size//24, size*7//8),  # Tail tip
        (size//8, size*3//4),   # Back in
        (size//4, size*5//8)    # Connect to body
    ]
    draw.polygon(points, fill=dragon_color)
    
    # Wings
    wing_points1 = [
        (size//2, size//2),     # Top of body
        (size//4, size//3),     # Wing tip
        (size*3//8, size//2)    # Back to body
    ]
    draw.polygon(wing_points1, fill=dragon_color)
    
    wing_points2 = [
        (size//2, size//2),     # Top of body
        (size*3//4, size//3),   # Wing tip
        (size*5//8, size//2)    # Back to body
    ]
    draw.polygon(wing_points2, fill=dragon_color)
    
    # Eyes
    eye_size = size // 20
    draw.ellipse((size*3//8, size*3//8, size*3//8 + eye_size, size*3//8 + eye_size), fill=(255, 255, 255))
    draw.ellipse((size*5//8 - eye_size, size*3//8, size*5//8, size*3//8 + eye_size), fill=(255, 255, 255))
    
    # Draw fire from mouth
    fire_points = [
        (size*2//3, size*3//8),  # Mouth
        (size*3//4, size//4),    # Fire tip
        (size*5//6, size*3//8),  # Bottom of fire
        (size*2//3, size*3//8)   # Back to mouth
    ]
    draw.polygon(fire_points, fill=(255, 69, 0))  # Orange-Red
    
    # Save the icon in different sizes
    # For ico format, we need multiple sizes
    img_32 = img.resize((32, 32), Image.LANCZOS)
    img_48 = img.resize((48, 48), Image.LANCZOS)
    img_64 = img.resize((64, 64), Image.LANCZOS)
    img_128 = img.resize((128, 128), Image.LANCZOS)
    
    # Save as an icon file
    img.save(output_filename, format='ICO', sizes=[(32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    
    print(f"Icon created: {output_filename}")
    return output_filename

if __name__ == "__main__":
    create_dragon_icon() 