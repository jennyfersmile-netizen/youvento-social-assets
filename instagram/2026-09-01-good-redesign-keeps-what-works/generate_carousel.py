from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import zipfile

ROOT = Path(__file__).resolve().parent
W, H = 1080, 1350
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

WHITE = (255, 250, 255)
MUTED = (231, 215, 244)
INK = (35, 12, 65)
PANEL = (65, 20, 100)
PINK = (255, 86, 176)
CORAL = (255, 117, 122)
VIOLET = (151, 83, 255)
BLUE = (57, 174, 255)


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REG, size)


def wrap(draw, text, fnt, max_width):
    lines, line = [], ""
    for word in text.split():
        trial = word if not line else line + " " + word
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def block(draw, x, y, text, fnt, fill, width, spacing=9):
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        box = draw.textbbox((x, y), line, font=fnt)
        y += box[3] - box[1] + spacing
    return y


def gradient(seed):
    palettes = [
        ((45, 9, 78), (188, 39, 146), (33, 122, 218)),
        ((35, 12, 82), (118, 49, 186), (231, 60, 146)),
        ((53, 10, 78), (201, 46, 135), (41, 132, 222)),
        ((33, 13, 78), (92, 54, 192), (227, 61, 151)),
        ((46, 8, 75), (162, 40, 158), (42, 143, 225)),
    ]
    a, b, c = palettes[seed]
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        for x in range(W):
            t = (x / W * .58 + y / H * .42)
            left, right = (a, b) if t < .5 else (b, c)
            u = t * 2 if t < .5 else (t - .5) * 2
            px[x, y] = tuple(int(left[i] * (1 - u) + right[i] * u) for i in range(3))
    im = im.convert("RGBA")
    glow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((650, -210, 1240, 380), fill=(255, 150, 220, 78))
    gd.ellipse((-260, 870, 360, 1490), fill=(61, 187, 255, 72))
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(100)))
    return im


def glass(im, box, radius=38, fill=(59, 19, 93, 235)):
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x0 + 9, y0 + 18, x1 + 9, y1 + 18), radius, fill=(20, 3, 42, 115))
    im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(22)))
    ImageDraw.Draw(im).rounded_rectangle(box, radius, fill=fill, outline=(234, 203, 255, 205), width=2)


def place_logo(im):
    logo = Image.open(ROOT / "youvento_logo_white.png").convert("RGBA")
    width = 180
    height = round(logo.height * width / logo.width)
    im.alpha_composite(logo.resize((width, height), Image.Resampling.LANCZOS), (70, H - 94))


def chrome(im, number, action="SWIPE"):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, 58, 298, 108), 25, fill=(48, 16, 82, 245), outline=(239, 204, 255, 210), width=2)
    d.text((184, 83), "BEFORE / AFTER", font=font(15, True), fill=WHITE, anchor="mm")
    d.text((1010, 83), f"{number}/5", font=font(21, True), fill=MUTED, anchor="ra")
    d.text((1010, H - 67), f"{action}  ->", font=font(18, True), fill=MUTED, anchor="ra")
    place_logo(im)


def fictional(draw, x=70, y=132):
    draw.rounded_rectangle((x, y, x + 216, y + 38), 19, fill=(255, 244, 255), outline=(255, 255, 255), width=1)
    draw.text((x + 108, y + 19), "FICTIONAL EXAMPLE", font=font(13, True), fill=(95, 30, 118), anchor="mm")


def profile_card(draw, box, after=False):
    x0, y0, x1, y1 = box
    compact = (x1 - x0) < 460
    draw.rounded_rectangle(box, 30, fill=(250, 241, 252), outline=(255, 255, 255), width=2)
    draw.ellipse((x0 + 28, y0 + 34, x0 + 116, y0 + 122), fill=CORAL)
    draw.text((x0 + 72, y0 + 78), "L", font=font(35, True), fill=WHITE, anchor="mm")
    draw.text((x0 + 138, y0 + 36), "LUMA STUDIO", font=font(22, True), fill=INK)
    draw.text((x0 + 138, y0 + 72), "Fictional interiors brand", font=font(16), fill=(104, 75, 121))
    if after:
        if compact:
            draw.text((x0 + 30, y0 + 153), "Warm interiors for", font=font(18, True), fill=INK)
            draw.text((x0 + 30, y0 + 184), "small city homes.", font=font(18, True), fill=INK)
            draw.text((x0 + 30, y0 + 221), "Room plans · styling · sourcing", font=font(14), fill=(95, 65, 114))
        else:
            draw.text((x0 + 30, y0 + 155), "Warm interiors for small city homes.", font=font(20, True), fill=INK)
            draw.text((x0 + 30, y0 + 195), "Room plans · styling · sourcing", font=font(17), fill=(95, 65, 114))
        draw.rounded_rectangle((x0 + 30, y0 + 240, x1 - 30, y0 + 296), 20, fill=(102, 51, 150))
        draw.text(((x0 + x1) // 2, y0 + 268), "VIEW SERVICES", font=font(17, True), fill=WHITE, anchor="mm")
        draw.text((x0 + 30, y0 + 326), '“She made the room feel like us.”', font=font(17, True), fill=(120, 55, 117))
    else:
        if compact:
            draw.text((x0 + 30, y0 + 153), "Design · styling · ideas", font=font(17, True), fill=INK)
            draw.text((x0 + 30, y0 + 184), "homes · more", font=font(17, True), fill=INK)
            draw.text((x0 + 30, y0 + 221), "Beautiful spaces · DM / email / shop", font=font(13), fill=(95, 65, 114))
        else:
            draw.text((x0 + 30, y0 + 155), "Design · styling · ideas · homes · more", font=font(18, True), fill=INK)
            draw.text((x0 + 30, y0 + 195), "Making spaces beautiful ✦ DM / email / shop", font=font(16), fill=(95, 65, 114))
        tags = ["BOOK", "SHOP", "EMAIL"]
        for i, tag in enumerate(tags):
            gap = 108 if compact else 135
            bw = 96 if compact else 116
            bx = x0 + 30 + i * gap
            draw.rounded_rectangle((bx, y0 + 240, bx + bw, y0 + 292), 18, fill=(213, 188, 225))
            draw.text((bx + bw // 2, y0 + 266), tag, font=font(13 if compact else 14, True), fill=(80, 43, 96), anchor="mm")
        draw.text((x0 + 30, y0 + 326), '“She made the room feel like us.”', font=font(17, True), fill=(120, 55, 117))


def slide1():
    im = gradient(0)
    d = ImageDraw.Draw(im)
    fictional(d, 70, 150)
    block(d, 70, 225, "You want the profile to feel clearer.", font(57, True), WHITE, 930, 7)
    d.text((70, 420), "You do not want it to stop feeling like yours.", font=font(29), fill=MUTED)
    glass(im, (70, 570, 1010, 1078))
    d = ImageDraw.Draw(im)
    d.text((112, 624), "A GOOD REDESIGN", font=font(23, True), fill=(255, 180, 225))
    block(d, 112, 688, "keeps what already works", font(69, True), WHITE, 820, 7)
    d.line((112, 960, 827, 960), fill=BLUE, width=6)
    d.text((112, 1000), "Refresh the system. Keep the recognition.", font=font(24, True), fill=WHITE)
    chrome(im, 1)
    return im


def slide2():
    im = gradient(1)
    d = ImageDraw.Draw(im)
    fictional(d)
    d.text((70, 195), "BEFORE YOU CHANGE IT", font=font(26, True), fill=(255, 180, 225))
    block(d, 70, 245, "Notice what people may already recognise.", font(56, True), WHITE, 920, 7)
    glass(im, (70, 548, 1010, 1092))
    d = ImageDraw.Draw(im)
    profile_card(d, (112, 598, 620, 1000), after=False)
    d.text((665, 610), "KEEP", font=font(20, True), fill=BLUE)
    items = [("CORAL", "the familiar visual cue"), ("VOICE", "the warm, simple tone"), ("PROOF", "the line people remember")]
    y = 666
    for title, body in items:
        d.ellipse((665, y, 697, y + 32), fill=PINK)
        d.text((712, y - 2), title, font=font(19, True), fill=WHITE)
        d.text((712, y + 27), body, font=font(17), fill=MUTED)
        y += 101
    d.text((665, 1017), "The good parts are clues.", font=font(22, True), fill=WHITE)
    chrome(im, 2)
    return im


def slide3():
    im = gradient(2)
    d = ImageDraw.Draw(im)
    d.text((70, 180), "THE REDESIGN RULE", font=font(26, True), fill=(135, 220, 255))
    block(d, 70, 235, "Keep the truth. Remove the friction.", font(60, True), WHITE, 920, 7)
    glass(im, (70, 555, 1010, 1075))
    d = ImageDraw.Draw(im)
    cols = [
        (112, "KEEP", PINK, ["recognisable colour", "human voice", "honest proof"]),
        (554, "CLARIFY", BLUE, ["what you offer", "who it helps", "one next step"]),
    ]
    for x, title, colour, rows in cols:
        d.rounded_rectangle((x, 615, x + 414, 980), 30, fill=(74, 27, 111), outline=colour, width=3)
        d.text((x + 30, 650), title, font=font(25, True), fill=colour)
        y = 720
        for row in rows:
            d.text((x + 33, y), "✓", font=font(22, True), fill=colour)
            d.text((x + 78, y + 2), row, font=font(21, True), fill=WHITE)
            y += 73
    d.text((112, 1018), "Start with an inventory—not an empty page.", font=font(24, True), fill=MUTED)
    chrome(im, 3)
    return im


def slide4():
    im = gradient(3)
    d = ImageDraw.Draw(im)
    fictional(d)
    d.text((70, 195), "SAME FICTIONAL BUSINESS", font=font(25, True), fill=(135, 220, 255))
    block(d, 70, 245, "A clearer version—not a replacement.", font(56, True), WHITE, 930, 7)
    glass(im, (70, 535, 1010, 1088))
    d = ImageDraw.Draw(im)
    d.text((112, 580), "BEFORE", font=font(19, True), fill=(255, 180, 225))
    d.text((570, 580), "AFTER", font=font(19, True), fill=(135, 220, 255))
    profile_card(d, (112, 620, 526, 1015), after=False)
    profile_card(d, (554, 620, 968, 1015), after=True)
    d.text((112, 1041), "The coral cue and warm voice stay. The path becomes clearer.", font=font(20, True), fill=WHITE)
    chrome(im, 4)
    return im


def slide5():
    im = gradient(4)
    d = ImageDraw.Draw(im)
    d.text((70, 180), "THE BETTER QUESTION", font=font(26, True), fill=(255, 180, 225))
    block(d, 70, 235, "What deserves to stay?", font(68, True), WHITE, 900, 7)
    glass(im, (70, 520, 1010, 1005))
    d = ImageDraw.Draw(im)
    prompts = [
        ("01", "What do people already recognise?"),
        ("02", "Which sentence is already clear?"),
        ("03", "What proof already feels believable?"),
    ]
    y = 585
    for num, text in prompts:
        d.rounded_rectangle((112, y, 968, y + 104), 27, fill=(74, 27, 111), outline=(223, 188, 250), width=2)
        d.text((154, y + 52), num, font=font(19, True), fill=BLUE, anchor="mm")
        d.text((205, y + 32), text, font=font(24, True), fill=WHITE)
        y += 124
    d.rounded_rectangle((70, 1055, 1010, 1182), 32, fill=(118, 42, 155), outline=(255, 181, 227), width=3)
    d.text((112, 1083), "NEED A CLEARER VERSION OF YOUR PROFILE?", font=font(18, True), fill=(255, 190, 230))
    d.text((112, 1122), "DM us. We will help you keep what feels like yours.", font=font(24, True), fill=WHITE)
    chrome(im, 5, "DM US")
    return im


def main():
    slides = [slide1(), slide2(), slide3(), slide4(), slide5()]
    exports = []
    for i, slide in enumerate(slides, 1):
        final = ImageOps.posterize(slide.convert("RGB"), 6)
        # Reapply compact navigation type after palette reduction.
        fd = ImageDraw.Draw(final)
        fd.text((184, 83), "BEFORE / AFTER", font=font(15, True), fill=WHITE, anchor="mm")
        final.save(ROOT / f"{i:02}.png")
        exports.append(final)

    preview = Image.new("RGB", (1200, 300), (34, 10, 60))
    for i, slide in enumerate(exports):
        preview.paste(slide.resize((240, 300), Image.Resampling.LANCZOS), (i * 240, 0))
    preview.save(ROOT / "preview_all.png", optimize=True)

    bundle = ROOT / "Youvento_A_Good_Redesign_Keeps_What_Already_Works_Carousel.zip"
    with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
        for i in range(1, 6):
            archive.write(ROOT / f"{i:02}.png", f"{i:02}.png")
        archive.write(ROOT / "caption.txt", "caption.txt")
        archive.write(ROOT / "source.md", "source.md")


if __name__ == "__main__":
    main()
