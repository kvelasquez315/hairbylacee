"""
Lacee's Salon — Photo Processor
================================
Place your raw photos in salon/raw/ then run:
  python3 process_photos.py

Processed images saved to salon/images/

Hair work photos (name photo1.jpg–photo10.jpg):
  1. Ash-blonde texture close-up     → keep RIGHT half  (split shot)
  2. Brunette balayage result         → keep RIGHT half  (split shot)
  3. Blonde girl, flower wall         → keep LEFT half   (split shot)
  4. Dark hair from behind, full      → trim edges only  (already a good full shot)
  5. Before/after reddish-brown       → keep RIGHT half  (after shot)
  6. Silver/ash hair from behind      → keep RIGHT half  (split shot)
  7. Long dark curly, salon           → keep CENTER-RIGHT (3-panel shot)
  8. Blonde wavy, sage jacket         → keep RIGHT half  (split shot)
  9. Pink highlights (Huskers)        → trim edges only  (mostly full shot)
 10. Dark brunette waves, flower wall → keep RIGHT half  (split shot)

Lacee personal photos (name lacee1.jpg, lacee2.jpg):
 lacee1. Sitting in chair, full body → no crop, gentle warm enhancement
 lacee2. With flowers, over shoulder → no crop, gentle warm enhancement
         Both sized to portrait 800×1066 with soft warmth filter
"""

import os
from PIL import Image, ImageEnhance, ImageFilter

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")
OUT_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT_DIR, exist_ok=True)

# Crop boxes as (left%, top%, right%, bottom%) — percentages of original dimensions
CROP_PLANS = {
    1:  (0.50, 0.03, 1.00, 0.97),   # right half
    2:  (0.47, 0.03, 1.00, 0.97),   # right half
    3:  (0.02, 0.03, 0.56, 0.97),   # left half
    4:  (0.03, 0.04, 0.97, 0.97),   # trim edges
    5:  (0.50, 0.03, 1.00, 0.97),   # right half (after)
    6:  (0.50, 0.04, 1.00, 0.97),   # right half
    7:  (0.32, 0.03, 0.90, 0.97),   # center-right panel
    8:  (0.44, 0.03, 1.00, 0.97),   # right half
    9:  (0.03, 0.05, 0.97, 0.97),   # trim edges + slight crop
    10: (0.47, 0.03, 1.00, 0.97),   # right half
}

# Enhancement settings per photo (brightness, contrast, saturation, sharpness)
# Values are multipliers: 1.0 = no change
ENHANCE = {
    1:  (1.08, 1.22, 1.15, 1.4),   # cool tones — subtle lift, higher contrast
    2:  (1.10, 1.20, 1.20, 1.5),   # warm brunette — pop the warmth
    3:  (1.12, 1.18, 1.18, 1.4),   # salon interior — bright & clean
    4:  (1.08, 1.25, 1.15, 1.5),   # dark hair — contrast boost to show depth
    5:  (1.06, 1.28, 1.20, 1.4),   # reddish-brown — enhance the richness
    6:  (1.10, 1.20, 1.10, 1.5),   # silver/ash — cool, high contrast
    7:  (1.08, 1.22, 1.18, 1.5),   # long dark curly — depth + shine
    8:  (1.12, 1.18, 1.22, 1.4),   # golden blonde — warm & bright
    9:  (1.10, 1.18, 1.25, 1.3),   # pink highlights — let the color pop
    10: (1.08, 1.25, 1.15, 1.4),   # dark brunette — depth boost
}

# Target output dimensions (portrait orientation for website)
TARGET_W = 800
TARGET_H = 1066  # ~3:4 ratio


def process(num):
    filename = f"photo{num}.jpg"
    src = os.path.join(RAW_DIR, filename)

    if not os.path.exists(src):
        # Try common extensions
        for ext in (".jpeg", ".png", ".webp", ".JPG", ".JPEG"):
            alt = os.path.join(RAW_DIR, f"photo{num}{ext}")
            if os.path.exists(alt):
                src = alt
                break
        else:
            print(f"  [SKIP] photo{num} not found in raw/")
            return

    img = Image.open(src).convert("RGB")
    w, h = img.size

    # Crop
    lp, tp, rp, bp = CROP_PLANS[num]
    left   = int(w * lp)
    top    = int(h * tp)
    right  = int(w * rp)
    bottom = int(h * bp)
    img = img.crop((left, top, right, bottom))

    # Resize to target (maintain aspect, then center-crop to exact target)
    img.thumbnail((TARGET_W * 2, TARGET_H * 2), Image.LANCZOS)
    iw, ih = img.size
    scale = max(TARGET_W / iw, TARGET_H / ih)
    new_w = int(iw * scale)
    new_h = int(ih * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    # Center crop to target
    cx = (new_w - TARGET_W) // 2
    cy = (new_h - TARGET_H) // 2
    img = img.crop((cx, cy, cx + TARGET_W, cy + TARGET_H))

    # Enhance
    bri, con, sat, sha = ENHANCE[num]
    img = ImageEnhance.Brightness(img).enhance(bri)
    img = ImageEnhance.Contrast(img).enhance(con)
    img = ImageEnhance.Color(img).enhance(sat)
    img = ImageEnhance.Sharpness(img).enhance(sha)

    # Gentle unsharp mask for crisp detail
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=3))

    # Save
    out_path = os.path.join(OUT_DIR, f"photo{num}.jpg")
    img.save(out_path, "JPEG", quality=92, optimize=True)
    print(f"  [OK]   photo{num}.jpg  →  {TARGET_W}x{TARGET_H}px  ({os.path.getsize(out_path)//1024}KB)")


def process_lacee(name, crop, enhance, output_name):
    """Process one of Lacee's personal photos."""
    src = None
    for ext in (".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG"):
        candidate = os.path.join(RAW_DIR, f"{name}{ext}")
        if os.path.exists(candidate):
            src = candidate
            break

    if src is None:
        print(f"  [SKIP] {name} not found in raw/")
        return

    img = Image.open(src).convert("RGB")
    w, h = img.size

    lp, tp, rp, bp = crop
    img = img.crop((int(w * lp), int(h * tp), int(w * rp), int(h * bp)))

    # Resize — keep aspect ratio, center-crop to portrait target
    scale = max(TARGET_W / img.width, TARGET_H / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.LANCZOS)
    cx = (nw - TARGET_W) // 2
    cy = (nh - TARGET_H) // 2
    img = img.crop((cx, cy, cx + TARGET_W, cy + TARGET_H))

    bri, con, sat, sha = enhance
    img = ImageEnhance.Brightness(img).enhance(bri)
    img = ImageEnhance.Contrast(img).enhance(con)
    img = ImageEnhance.Color(img).enhance(sat)
    img = ImageEnhance.Sharpness(img).enhance(sha)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=45, threshold=4))

    out_path = os.path.join(OUT_DIR, output_name)
    img.save(out_path, "JPEG", quality=94, optimize=True)
    print(f"  [OK]   {output_name}  →  {TARGET_W}x{TARGET_H}px  ({os.path.getsize(out_path)//1024}KB)")


# Lacee personal photo specs
LACEE_PHOTOS = [
    {
        "name":   "lacee1",
        "output": "lacee1.jpg",
        # Full body chair shot — keep full frame, trim slight top space
        "crop":   (0.04, 0.02, 0.96, 0.97),
        # Gentle warmth: lift shadows, subtle saturation, keep skin natural
        "enhance": (1.06, 1.14, 1.12, 1.35),
    },
    {
        "name":   "lacee2",
        "output": "lacee2.jpg",
        # Flowers/over-shoulder portrait — already perfectly framed
        "crop":   (0.03, 0.02, 0.97, 0.97),
        # Same gentle warmth for consistency
        "enhance": (1.06, 1.14, 1.12, 1.35),
    },
]


if __name__ == "__main__":
    print("Processing hair work photos (1–10)...\n")
    for i in range(1, 11):
        process(i)

    print("\nProcessing Lacee personal photos...\n")
    for spec in LACEE_PHOTOS:
        process_lacee(spec["name"], spec["crop"], spec["enhance"], spec["output"])

    print("\nDone! Check the images/ folder.")
