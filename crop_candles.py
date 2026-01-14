"""
Crop 6 candlestick patterns from composite image
Image size: 1024x682
Layout: 2 rows x 3 columns
Each cell needs to be cropped to exclude text labels
"""

from PIL import Image
import os

# Open the source image
src_path = r'C:/Users/sec/.gemini/antigravity/brain/ffb75746-adba-46ef-9093-d06e5fb035b5/uploaded_image_1768390174764.png'
img = Image.open(src_path)

# Output directory
out_dir = r'c:\Users\sec\Desktop\Naspick\images\candle_patterns'
os.makedirs(out_dir, exist_ok=True)

# Image dimensions
w, h = img.size  # 1024 x 682

# Grid: 3 columns, 2 rows
col_width = w // 3  # ~341
row_height = h // 2  # ~341

# Define crop boxes for each pattern (left, upper, right, lower)
# Excluding text labels at the bottom (~80px) and some top padding
# Image: 1024x682, Grid: 3 cols x 2 rows

# More precise coordinates based on visual inspection
# Row 1 candles appear in y: 30~200, Row 2 candles in y: 320~520
# Text is below the candles

# Manually tuned crop boxes (left, top, right, bottom) - CANDLES ONLY, NO TEXT
# Adjusted to center the candles better within each crop
patterns = {
    # Row 1 (upper half: 0-341) - adjusted for center alignment
    "hammer": (85, 20, 215, 200),            # Single candle
    "shooting_star": (380, 5, 530, 200),     # Single candle with star  
    "bullish_engulfing": (720, 20, 930, 200), # Two candles
    # Row 2 (lower half: 341-682) - adjusted for center alignment
    "bearish_engulfing": (65, 300, 275, 510),
    "morning_star": (355, 300, 595, 510),
    "evening_star": (700, 300, 940, 510),
}

# Crop each pattern
cropped_images = {}
for name, box in patterns.items():
    cropped = img.crop(box)
    cropped_images[name] = cropped
    print(f"{name}: {cropped.size}")

# Find the max dimensions to standardize
max_w = max(c.size[0] for c in cropped_images.values())
max_h = max(c.size[1] for c in cropped_images.values())

# Final size (square for consistency)
final_size = 128  # Output icon size

# Save each pattern resized to final size
for name, cropped in cropped_images.items():
    # Resize maintaining aspect ratio and center on transparent canvas
    ratio = min(final_size / cropped.size[0], final_size / cropped.size[1])
    new_size = (int(cropped.size[0] * ratio), int(cropped.size[1] * ratio))
    resized = cropped.resize(new_size, Image.Resampling.LANCZOS)
    
    # Create transparent canvas
    canvas = Image.new('RGBA', (final_size, final_size), (0, 0, 0, 0))
    
    # Center the resized image on canvas
    offset = ((final_size - new_size[0]) // 2, (final_size - new_size[1]) // 2)
    canvas.paste(resized, offset)
    
    # Save
    out_path = os.path.join(out_dir, f'{name}.png')
    canvas.save(out_path, 'PNG')
    print(f"Saved: {out_path}")

print(f"\nAll 6 patterns saved to: {out_dir}")
