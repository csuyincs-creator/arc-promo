"""Draw candidate circles on a source photo (with a 10% grid) to verify disc parameters.
    python check_circle.py raw/bubble.jpg out.jpg 1686,1736,765 [cx,cy,r ...]"""
import sys
from PIL import Image, ImageDraw
src, out, *circles = sys.argv[1:]
im = Image.open(src).convert('RGB')
k = 1200 / im.width
im = im.resize((1200, int(im.height * k)))
d = ImageDraw.Draw(im)
for i in range(1, 10):
    d.line([(120 * i, 0), (120 * i, im.height)], fill=(255, 255, 0), width=1)
    d.line([(0, im.height * i / 10), (1200, im.height * i / 10)], fill=(255, 255, 0), width=1)
for c, col in zip(circles, ['red', 'cyan', 'lime', 'magenta']):
    cx, cy, r = map(float, c.split(','))
    d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], outline=col, width=3)
im.save(out, quality=88)
print(f'{src}: {im.width / k:.0f}x{im.height / k:.0f} px; grid lines every 10%')
