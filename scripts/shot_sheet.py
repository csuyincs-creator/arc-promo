"""Contact sheet of generated shots (the visible 4K frame), with the arc's top marked in red.
    python shot_sheet.py public/shots out/shots_sheet.jpg [name ...]    (default: every shot)"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont
folder, out, *names = sys.argv[1:]
if not names:
    names = sorted(f[:-4] for f in os.listdir(folder) if f.endswith('.jpg') and not f.endswith('_glow.jpg'))
cw, ch, cols = 640, 360, 5
rows = (len(names) + cols - 1) // cols
sheet = Image.new('RGB', (cw * cols, ch * rows), 'black')
try:
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 20)
except OSError:
    font = ImageFont.load_default()
for k, n in enumerate(names):
    im = Image.open(os.path.join(folder, f'{n}.jpg')).crop((320, 240, 4160, 2400)).resize((cw, ch))
    d = ImageDraw.Draw(im)
    d.line([(0, ch * 0.6), (cw, ch * 0.6)], fill=(255, 0, 0), width=1)
    d.text((6, 4), n, fill='yellow', font=font)
    sheet.paste(im, ((k % cols) * cw, (k // cols) * ch))
sheet.save(out, quality=85)
print(f'{len(names)} shots -> {out}')
