"""Generate sample leaf images for testing (colored placeholders)."""
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("pip install Pillow")
    exit(1)

OUT = Path(__file__).parent

SAMPLES = [
    ("tomato_early_blight.jpg", (139, 90, 43), "brown spots"),
    ("tomato_healthy.jpg", (34, 139, 34), "healthy green"),
    ("potato_early_blight.jpg", (160, 82, 45), "potato leaf"),
    ("pepper_bacterial.jpg", (85, 107, 47), "pepper leaf"),
]


def create_image(name: str, color: tuple, label: str):
    img = Image.new("RGB", (400, 400), color)
    draw = ImageDraw.Draw(img)
    draw.ellipse([80, 60, 320, 340], fill=(color[0] + 20, min(255, color[1] + 40), color[2]))
    draw.text((120, 180), label[:12], fill=(255, 255, 255))
    img.save(OUT / name)
    print(f"Created {OUT / name}")


if __name__ == "__main__":
    for name, color, label in SAMPLES:
        create_image(name, color, label)
