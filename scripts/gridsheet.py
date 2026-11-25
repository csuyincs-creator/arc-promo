# Contact sheet with a 10% grid on every image, to read off horizon rows and circle positions.
import sys, os
from PIL import Image, ImageDraw, ImageFont
out, cols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
cw, ch = 640, 480
rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (cw * cols, ch * rows), 'black')
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 18)
for k, f in enumerate(files):
    im = Image.open(f).convert('RGB')
    im.thumbnail((cw, ch - 24))
    d = ImageDraw.Draw(im)
    w, h = im.size
    for i in range(1, 10):
        c = (255, 255, 0) if i == 5 else (255, 60, 60)
        d.line([(0, h * i / 10), (w, h * i / 10)], fill=c, width=1)
        d.line([(w * i / 10, 0), (w * i / 10, h)], fill=c, width=1)
    x, y = (k % cols) * cw, (k // cols) * ch
    sheet.paste(im, (x, y + 24))
    ImageDraw.Draw(sheet).text((x + 4, y + 2), os.path.basename(f), fill='yellow', font=font)
sheet.save(out, quality=85)
