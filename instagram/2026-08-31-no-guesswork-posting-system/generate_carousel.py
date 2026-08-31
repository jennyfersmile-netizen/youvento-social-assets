from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import math
import zipfile

ROOT = Path(__file__).resolve().parent
W, H = 1080, 1350
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAVY = (5, 18, 47)
NAVY_2 = (8, 31, 76)
PANEL = (11, 42, 91)
WHITE = (247, 251, 255)
MUTED = (178, 202, 231)
CYAN = (61, 211, 255)
BLUE = (62, 125, 255)
ICE = (207, 242, 255)


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def wrap(draw, text, fnt, max_width):
    lines, line = [], ""
    for word in text.split():
        trial = word if not line else f"{line} {word}"
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def text_block(draw, x, y, text, fnt, fill, max_width, spacing=10):
    for line in wrap(draw, text, fnt, max_width):
        draw.text((x, y), line, font=fnt, fill=fill)
        box = draw.textbbox((x, y), line, font=fnt)
        y += box[3] - box[1] + spacing
    return y


def background(index):
    im = Image.new("RGB", (W, H), NAVY)
    px = im.load()
    for y in range(H):
        for x in range(W):
            glow = max(0.0, 1.0 - math.hypot(x - (810 - index * 45), y - (130 + index * 125)) / 840)
            line = 1 if ((x + index * 37) % 180 < 2 or (y + index * 53) % 180 < 2) else 0
            px[x, y] = (
                min(255, int(NAVY[0] + 7 * glow + line * 5)),
                min(255, int(NAVY[1] + 24 * glow + line * 9)),
                min(255, int(NAVY[2] + 55 * glow + line * 18)),
            )
    im = im.convert("RGBA")
    halo = Image.new("RGBA", im.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.ellipse((650, -170 + index * 55, 1210, 390 + index * 55), fill=(33, 139, 255, 60))
    hd.ellipse((-230, 940 - index * 40, 310, 1480 - index * 40), fill=(22, 213, 255, 38))
    im.alpha_composite(halo.filter(ImageFilter.GaussianBlur(95)))
    return im


def place_logo(im):
    logo = Image.open(ROOT / "youvento_logo_white.png").convert("RGBA")
    width = 180
    height = round(logo.height * width / logo.width)
    im.alpha_composite(logo.resize((width, height), Image.Resampling.LANCZOS), (70, H - 94))


def chrome(im, number, action="SWIPE"):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, 58, 296, 108), 25, fill=(6, 29, 68, 238), outline=(61, 211, 255, 170), width=2)
    d.text((183, 83), "CONTENT SYSTEM", font=font(15, True), fill=ICE, anchor="mm")
    d.text((1010, 83), f"{number}/5", font=font(21, True), fill=MUTED, anchor="ra")
    d.text((1010, H - 67), f"{action}  ->", font=font(18, True), fill=MUTED, anchor="ra")
    place_logo(im)


def panel(im, box, radius=34):
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 10, y0 + 18, x1 + 10, y1 + 18), radius, fill=(0, 5, 23, 125))
    im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(22)))
    ImageDraw.Draw(im).rounded_rectangle(box, radius, fill=(*PANEL, 236), outline=(73, 176, 255, 180), width=2)


def node(draw, cx, cy, number, label, active=True):
    color = CYAN if active else (79, 113, 159)
    draw.ellipse((cx - 54, cy - 54, cx + 54, cy + 54), fill=(7, 31, 73), outline=color, width=4)
    draw.text((cx, cy - 6), number, font=font(23, True), fill=WHITE, anchor="mm")
    draw.text((cx, cy + 84), label, font=font(18, True), fill=color, anchor="mm")


def slide1():
    im = background(0)
    d = ImageDraw.Draw(im)
    d.text((70, 178), "A FAMILIAR BLANK", font=font(25, True), fill=CYAN)
    text_block(d, 70, 230, "You opened the calendar. Again.", font(64, True), WHITE, 910, 8)
    d.text((70, 455), "And still don't know what to post.", font=font(32), fill=MUTED)
    panel(im, (70, 600, 1010, 1075))
    d = ImageDraw.Draw(im)
    d.text((112, 650), "THE", font=font(22, True), fill=CYAN)
    text_block(d, 112, 700, "no-guesswork posting system", font(67, True), WHITE, 815, 7)
    d.line((112, 975, 800, 975), fill=BLUE, width=6)
    d.text((112, 1005), "Four decisions. Made in the right order.", font=font(24, True), fill=ICE)
    chrome(im, 1)
    return im


def slide2():
    im = background(1)
    d = ImageDraw.Draw(im)
    d.text((70, 178), "STEP 01", font=font(26, True), fill=CYAN)
    text_block(d, 70, 230, "Give the post one job.", font(64, True), WHITE, 900, 8)
    d.text((70, 425), "Do not ask one post to do everything.", font=font(29), fill=MUTED)
    panel(im, (70, 555, 1010, 1080))
    d = ImageDraw.Draw(im)
    options = [
        ("RECOGNITION", "I see myself here"),
        ("UNDERSTANDING", "Now this makes sense"),
        ("BELIEF", "I trust this more"),
        ("ACTION", "I know what to do"),
    ]
    y = 610
    for i, (label, meaning) in enumerate(options, 1):
        d.rounded_rectangle((112, y, 968, y + 91), 24, fill=(7, 31, 73), outline=(38, 112, 205), width=2)
        d.text((150, y + 46), f"0{i}", font=font(18, True), fill=CYAN, anchor="mm")
        d.text((205, y + 18), label, font=font(22, True), fill=WHITE)
        d.text((205, y + 50), meaning, font=font(19), fill=MUTED)
        y += 108
    chrome(im, 2)
    return im


def slide3():
    im = background(2)
    d = ImageDraw.Draw(im)
    d.text((70, 178), "STEP 02", font=font(26, True), fill=CYAN)
    text_block(d, 70, 230, "Choose the message before the format.", font(60, True), WHITE, 930, 8)
    panel(im, (70, 555, 1010, 1078))
    d = ImageDraw.Draw(im)
    items = [
        ("01", "ONE USEFUL IDEA", "What should the person understand?"),
        ("02", "ONE SUPPORTING DETAIL", "What makes the idea concrete?"),
        ("03", "THE CLEAREST FORMAT", "Single image, carousel, or video?"),
    ]
    y = 615
    for num, title, body in items:
        d.ellipse((112, y, 198, y + 86), fill=(6, 28, 68), outline=CYAN, width=3)
        d.text((155, y + 43), num, font=font(19, True), fill=WHITE, anchor="mm")
        d.text((235, y + 5), title, font=font(23, True), fill=CYAN)
        d.text((235, y + 44), body, font=font(22), fill=WHITE)
        if num != "03":
            d.line((155, y + 88, 155, y + 132), fill=(62, 125, 255), width=4)
        y += 141
    d.text((112, 1020), "Let the message choose the container.", font=font(25, True), fill=ICE)
    chrome(im, 3)
    return im


def slide4():
    im = background(3)
    d = ImageDraw.Draw(im)
    d.text((70, 178), "STEP 03", font=font(26, True), fill=CYAN)
    text_block(d, 70, 230, "End with one next step.", font(64, True), WHITE, 900, 8)
    d.text((70, 426), "A clear ending is kinder than four competing asks.", font=font(28), fill=MUTED)
    panel(im, (70, 570, 1010, 1068))
    d = ImageDraw.Draw(im)
    labels = [("SAVE", "for later"), ("REPLY", "with an answer"), ("VISIT", "for details"), ("ENQUIRE", "when ready")]
    for i, (label, detail) in enumerate(labels):
        x = 112 + (i % 2) * 438
        y = 625 + (i // 2) * 190
        d.rounded_rectangle((x, y, x + 408, y + 156), 30, fill=(7, 31, 73), outline=CYAN if i == 2 else (47, 102, 179), width=3)
        d.text((x + 28, y + 31), label, font=font(30, True), fill=WHITE)
        d.text((x + 28, y + 85), detail, font=font(21), fill=MUTED)
    d.text((112, 1018), "Choose the one the post has earned.", font=font(25, True), fill=ICE)
    chrome(im, 4)
    return im


def slide5():
    im = background(4)
    d = ImageDraw.Draw(im)
    d.text((70, 178), "THE REPEATABLE SEQUENCE", font=font(25, True), fill=CYAN)
    text_block(d, 70, 230, "Four decisions. Then you can design.", font(58, True), WHITE, 930, 8)
    panel(im, (70, 540, 1010, 1015))
    d = ImageDraw.Draw(im)
    xs = [165, 415, 665, 915]
    for i in range(3):
        d.line((xs[i] + 58, 715, xs[i + 1] - 58, 715), fill=BLUE, width=5)
    for i, (num, label) in enumerate([("01", "JOB"), ("02", "MESSAGE"), ("03", "FORMAT"), ("04", "NEXT STEP")]):
        node(d, xs[i], 715, num, label)
    d.text((112, 875), "The format can change.", font=font(28, True), fill=WHITE)
    d.text((112, 920), "The order of decisions stays steady.", font=font(28, True), fill=ICE)
    d.rounded_rectangle((70, 1060, 1010, 1185), 32, fill=(17, 74, 142), outline=CYAN, width=3)
    d.text((112, 1088), "WANT THE MONTH MAPPED FOR YOU?", font=font(20, True), fill=CYAN)
    d.text((112, 1125), "Explore the 1-Month Content Plan · link in bio", font=font(25, True), fill=WHITE)
    chrome(im, 5, "LINK IN BIO")
    return im


def main():
    slides = [slide1(), slide2(), slide3(), slide4(), slide5()]
    rgb = []
    for i, slide in enumerate(slides, 1):
        final = ImageOps.posterize(slide.convert("RGB"), 6)
        final.save(ROOT / f"{i:02}.png", optimize=True)
        rgb.append(final)

    # Reopen each export and composite a pre-rendered label. Keeping this
    # outside the posterization pass prevents intermittent loss of the small
    # anti-aliased type in optimized PNGs.
    label = Image.new("RGBA", (226, 50), (0, 0, 0, 0))
    ld = ImageDraw.Draw(label)
    ld.text((113, 25), "CONTENT SYSTEM", font=font(15, True), fill=(*ICE, 255), anchor="mm")
    for i in range(1, 6):
        with Image.open(ROOT / f"{i:02}.png") as opened:
            fixed = opened.convert("RGBA")
        fixed.alpha_composite(label, (70, 58))
        fixed = fixed.convert("RGB")
        fixed.save(ROOT / f"{i:02}.png", optimize=True)
        rgb[i - 1] = fixed

    thumb_w, thumb_h = 240, 300
    preview = Image.new("RGB", (thumb_w * 5, thumb_h), NAVY)
    for i, slide in enumerate(rgb):
        preview.paste(slide.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS), (i * thumb_w, 0))
    preview.save(ROOT / "preview_all.png", optimize=True)

    bundle = ROOT / "Youvento_The_No_Guesswork_Posting_System_Carousel.zip"
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
        for i in range(1, 6):
            archive.write(ROOT / f"{i:02}.png", f"{i:02}.png")
        archive.write(ROOT / "caption.txt", "caption.txt")
        archive.write(ROOT / "source.md", "source.md")


if __name__ == "__main__":
    main()
