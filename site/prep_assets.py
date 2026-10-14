"""One-off: crops placeholder images from the design mockup and your report PDFs.
Replace anything in assets/ with your own photo and dashboard screenshots (same filenames)."""
from PIL import Image
M = Image.open("mockup.png").convert("RGB"); W, H = M.size
def crop(box, name, w=900):
    x0, y0, x1, y1 = box
    im = M.crop((int(x0/1536*W), int(y0/1024*H), int(x1/1536*W), int(y1/1024*H)))
    im.thumbnail((w, w)); im.save(f"assets/{name}", quality=82, optimize=True)
crop((392, 58, 780, 360), "hero.jpg", 1100)
crop((48, 424, 217, 523), "dash-farmer.jpg", 700)
crop((238, 424, 407, 523), "dash-network.jpg", 700)
def fromimg(src, box, name, w=900):
    im = Image.open(src).convert("RGB"); a, b = im.size
    im.crop((int(box[0]*a), int(box[1]*b), int(box[2]*a), int(box[3]*b))).resize((w, int(w*(box[3]-box[1])*b/((box[2]-box[0])*a)))).save(f"assets/{name}", quality=80, optimize=True)
fromimg("src/rfrn.jpg", (0, .55, 1, .97), "report-rfrn.jpg")
fromimg("src/migori.jpg", (.12, .65, .89, .84), "report-migori.jpg")
fromimg("src/aspire.jpg", (.1, .03, .9, .65), "aspire-cert.jpg", 700)
