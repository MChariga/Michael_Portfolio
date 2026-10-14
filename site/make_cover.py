"""Designs the profile cover banner (2400x600) and the Parenting card image."""
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
U = "/home/claude/u/"; W, H, SS = 2400, 600, 2
def op(i): return Image.open(f"{U}{i:02d}.jpg").convert("RGB")
def crop(im, w, h, fx=.5, fy=.5):
    r = max(w / im.width, h / im.height); im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x = min(max(0, round(fx * im.width - w / 2)), im.width - w); y = min(max(0, round(fy * im.height - h / 2)), im.height - h)
    return im.crop((x, y, x + w, y + h))
def grade(im): 
    im = ImageEnhance.Contrast(im).enhance(1.07); im = ImageEnhance.Color(im).enhance(1.06); return im.filter(ImageFilter.UnsharpMask(1.2, 60, 3))
# base: navy gradient with soft rings
base = Image.new("RGB", (W, H)); px = base.load()
for x in range(W):
    t = min(1, x / 1500)
    c = (int(8 + (24 - 8) * t), int(30 + (66 - 30) * t), int(58 + (118 - 58) * t))
    for y in range(H): px[x, y] = c
ring = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ring)
for r in (260, 380, 500, 620): d.ellipse((220 - r, 470 - r, 220 + r, 470 + r), outline=(255, 255, 255, 18), width=2)
base = Image.alpha_composite(base.convert("RGBA"), ring)
s = 90; pitch = 575; gap = 10
panels = [(41, .5, .42), (0, .5, .48), (10, .5, .55)]
for i, (pid, fx, fy) in enumerate(panels):
    x0 = 760 + i * pitch; w = pitch - gap + (200 if i == 2 else 0)
    ph = grade(crop(op(pid), w + s, H, fx, fy))
    m = Image.new("L", (W * SS, H * SS), 0); md = ImageDraw.Draw(m)
    md.polygon([((x0 + s) * SS, 0), ((x0 + s + w) * SS, 0), ((x0 + w) * SS, H * SS), (x0 * SS, H * SS)], fill=255)
    m = m.resize((W, H), Image.LANCZOS); layer = Image.new("RGBA", (W, H)); layer.paste(ph, (x0, 0)); layer.putalpha(m)
    base = Image.alpha_composite(base, layer)
# blend first photo into navy and add a slight vignette at the bottom
grad = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gp = grad.load()
for x in range(700, 1050):
    a = int(200 * (1 - (x - 700) / 350) ** 1.6)
    for y in range(H): gp[x, y] = (10, 36, 69, a)
base = Image.alpha_composite(base, grad)
# gold hairlines along the slants
ln = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); ld = ImageDraw.Draw(ln)
for i in range(3):
    x0 = 760 + i * pitch; ld.line(((x0 + s) * SS, 0, x0 * SS, H * SS), fill=(214, 164, 62, 255), width=5)
ld.rectangle((0, (H - 8) * SS, W * SS, H * SS), fill=(214, 164, 62, 255))
base = Image.alpha_composite(base, ln.resize((W, H), Image.LANCZOS))
base.convert("RGB").save("assets/cover.jpg", quality=90, optimize=True, subsampling=0)

# Parenting card: ParentApp logo on a clean warm canvas
Wc, Hc = 1600, 900; c = Image.new("RGB", (Wc, Hc)); p = c.load()
for y in range(Hc):
    for x in range(Wc):
        t = (x / Wc * .5 + y / Hc * .5); p[x, y] = (255, int(250 - 14 * t), int(244 - 34 * t))
logo = Image.open("src/parentapp-logo.png").convert("RGB"); k = 2.7
logo = logo.resize((int(logo.width * k), int(logo.height * k)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))
card = Image.new("RGBA", (logo.width + 160, logo.height + 120), (255, 255, 255, 255)); card.paste(logo, (80, 60))
mask = Image.new("L", card.size, 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0) + card.size, 36, fill=255); card.putalpha(mask)
sh = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); cx, cy = (Wc - card.width) // 2, (Hc - card.height) // 2 - 10
ImageDraw.Draw(sh).rounded_rectangle((cx, cy + 18, cx + card.width, cy + 18 + card.height), 36, fill=(120, 60, 20, 70))
c = Image.alpha_composite(c.convert("RGBA"), sh.filter(ImageFilter.GaussianBlur(26))); c.alpha_composite(card, (cx, cy))
bar = ImageDraw.Draw(c); bar.rectangle((0, Hc - 16, Wc // 2, Hc), fill=(217, 65, 30)); bar.rectangle((Wc // 2, Hc - 16, Wc, Hc), fill=(245, 168, 0))
c.convert("RGB").save("assets/parent.jpg", quality=90, optimize=True)
