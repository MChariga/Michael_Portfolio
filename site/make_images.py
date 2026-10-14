"""Designs the project card images: browser-frame mockups of real screenshots/figures and a report cover mockup."""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H = 1600, 900
F = lambda s, b=False: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if b else ""), s)

def bg():
    im = Image.new("RGB", (W, H)); px = im.load()
    for y in range(H):
        for x in range(0, W):
            t = (x / W * .6 + y / H * .4); px[x, y] = (int(11 + (29 - 11) * t), int(37 + (78 - 37) * t), int(69 + (137 - 69) * t))
    return im

def shadow(base, box, r=18, blur=28, off=16, alpha=120):
    s = Image.new("RGBA", base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(s)
    x0, y0, x1, y1 = box; d.rounded_rectangle((x0, y0 + off, x1, y1 + off), r, fill=(0, 0, 0, alpha))
    base.paste(Image.alpha_composite(base.convert("RGBA"), s.filter(ImageFilter.GaussianBlur(blur))).convert("RGB"))

def browser(src, url, out, pad=34, trim=None):
    im = Image.open(src).convert("RGB")
    if trim: im = im.crop(trim)
    base = bg(); bar = 54
    mw, mh = W - 2 * pad, H - 2 * pad - 10
    r = min(mw / im.width, (mh - bar) / im.height); iw, ih = int(im.width * r), int(im.height * r)
    wx0 = (W - iw) // 2; wy0 = (H - (ih + bar)) // 2; wx1, wy1 = wx0 + iw, wy0 + ih + bar
    shadow(base, (wx0, wy0, wx1, wy1)); d = ImageDraw.Draw(base)
    d.rounded_rectangle((wx0, wy0, wx1, wy1), 18, fill="white")
    d.rounded_rectangle((wx0, wy0, wx1, wy0 + bar + 18), 18, fill="#eef2f7"); d.rectangle((wx0, wy0 + bar - 2, wx1, wy0 + bar + 18), fill="white")
    d.line((wx0, wy0 + bar, wx1, wy0 + bar), fill="#d9e1ec", width=2)
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")): d.ellipse((wx0 + 22 + i * 28, wy0 + 19, wx0 + 38 + i * 28, wy0 + 35), fill=c)
    ux0 = wx0 + 120; ux1 = wx1 - 30; d.rounded_rectangle((ux0, wy0 + 11, ux1, wy0 + 43), 16, fill="white", outline="#d9e1ec")
    d.text((ux0 + 18, wy0 + 17), url, font=F(15), fill="#55627a")
    mask = Image.new("L", (iw, ih), 255); base.paste(im.resize((iw, ih), Image.LANCZOS), (wx0, wy0 + bar))
    d.rounded_rectangle((wx0, wy0, wx1, wy1), 18, outline="#cfd8e6", width=2)
    base.save(out, quality=88, optimize=True)

def report(cover, page, out):
    base = bg(); c = Image.open(cover).convert("RGB"); p = Image.open(page).convert("RGB")
    ph = 760; p = p.resize((int(p.width * ph / p.height), ph), Image.LANCZOS); ch = 840; c = c.resize((int(c.width * ch / c.height), ch), Image.LANCZOS)
    px0 = W // 2 + 40; py0 = 70
    shadow(base, (px0, py0, px0 + p.width, py0 + ph), r=6); base.paste(p, (px0, py0))
    cx0 = W // 2 - c.width + 80; cy0 = 30
    shadow(base, (cx0, cy0, cx0 + c.width, cy0 + ch), r=6, alpha=150); base.paste(c, (cx0, cy0)); base.save(out, quality=88, optimize=True)

browser("src/dash-network.png", "CFHF farmer practice dashboard: baseline to endline", "assets/card-farmer-dashboard.jpg")
browser("/home/claude/fig/p14-000.jpg", "CFHF baseline and endline: farmer practice change", "assets/card-farmer-practice.jpg")
report("/home/claude/fig/cover-01.png", "/home/claude/fig/pg14-14.png", "assets/card-field-report.jpg")

def slides(front, back, out):
    base = bg(); a = Image.open(back).convert("RGB"); b = Image.open(front).convert("RGB")
    aw = 1020; a = a.resize((aw, int(a.height * aw / a.width)), Image.LANCZOS); b = b.resize((aw, int(b.height * aw / b.width)), Image.LANCZOS)
    ax, ay = W - aw - 90, 90; bx, by = 90, H - b.height - 90
    shadow(base, (ax, ay, ax + aw, ay + a.height), r=8); base.paste(a, (ax, ay))
    shadow(base, (bx, by, bx + aw, by + b.height), r=8, alpha=150); base.paste(b, (bx, by)); base.save(out, quality=88, optimize=True)

report("/home/claude/fig2/t1-01.png", "/home/claude/fig2/t6-06.png", "assets/card-tephrosia-report.jpg")
report("/home/claude/fig2/m15-15.png", "/home/claude/fig2/m17-17.png", "assets/card-migori-report.jpg")
slides("/home/claude/fig2/s1-01.png", "/home/claude/fig2/s6-06.png", "assets/card-fermented-feeds.jpg")
