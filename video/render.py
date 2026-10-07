#!/usr/bin/env python3
"""Render the AI Operating Layer loop video from the whitepaper's own words.

Output: frames/*.png (one per scene step) + a scenes.txt listing durations,
then build.sh stitches them with ffmpeg crossfades into aiol-loop.mp4.
Brand: Coder near-black (#090B0B), purple-tinted neutrals, one violet accent,
flat, no shadows, logo top-left.
"""
import math, os, random, io
from PIL import Image, ImageDraw, ImageFont
import cairosvg, qrcode

W, H = 1920, 1080
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames")
os.makedirs(OUT, exist_ok=True)

INK = (9, 11, 11)          # #090B0B
CINDER = (24, 23, 26)      # #18171A
SMOKE = (47, 45, 51)       # #2F2D33
WHITE = (245, 245, 245)
DIM = (160, 158, 168)
MUTE = (110, 108, 120)
VIOLET = (117, 17, 226)    # #7511E2
PURPLE = (188, 124, 255)   # #BC7CFF
EMBER = (255, 128, 103)
GREEN = (102, 255, 171)

FD = "/usr/share/fonts/truetype/"
def F(name, size): return ImageFont.truetype(FD + name, size)
SANS_L = lambda s: F("lato/Lato-Light.ttf", s)
SANS   = lambda s: F("lato/Lato-Regular.ttf", s)
SANS_M = lambda s: F("lato/Lato-Medium.ttf", s)
SANS_S = lambda s: F("lato/Lato-Semibold.ttf", s)
MONO   = lambda s: F("dejavu/DejaVuSansMono.ttf", s)

LOGO_SVG = os.environ.get("CODER_LOGO", "/sessions/stoic-serene-wright/mnt/.claude/skills/coder-brand/assets/coder-logo.svg")
def logo(height=40, color="#FFFFFF"):
    svg = open(LOGO_SVG).read().replace('fill="currentColor"', f'fill="{color}"')
    png = cairosvg.svg2png(bytestring=svg.encode(), output_height=height, output_width=height*2)
    return Image.open(io.BytesIO(png)).convert("RGBA")
LOGO = logo(40)

def halftone(img, seed=1, density=0.018, cx=1500, cy=300, r=900):
    """Subtle halftone dot field, denser toward (cx,cy): the whitepaper cover motif."""
    d = ImageDraw.Draw(img)
    step = 22
    for y in range(0, H, step):
        for x in range(0, W, step):
            dist = math.hypot(x-cx, y-cy)
            t = max(0.0, 1 - dist / r)
            rad = 0.6 + 4.2 * (t ** 1.6)
            if rad < 0.9: continue
            c = int(28 + 70 * t)
            d.ellipse((x-rad, y-rad, x+rad, y+rad), fill=(c, c-2, c+6))

def base(dots=True, dot_pos=(1500, 300)):
    img = Image.new("RGB", (W, H), INK)
    if dots: halftone(img, cx=dot_pos[0], cy=dot_pos[1])
    img.paste(LOGO, (96, 72), LOGO)
    d = ImageDraw.Draw(img)
    d.text((W-96, 84), "A CODER WHITEPAPER", font=MONO(20), fill=MUTE, anchor="ra")
    return img

def footer(img, section):
    d = ImageDraw.Draw(img)
    d.line((96, H-96, W-96, H-96), fill=SMOKE, width=1)
    d.text((96, H-70), section.upper(), font=MONO(20), fill=MUTE)
    d.text((W-96, H-70), "coder.com/ai-operating-layer", font=MONO(20), fill=MUTE, anchor="ra")

def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def para(d, xy, text, font, fill, maxw, lh=1.3):
    x, y = xy
    for ln in wrap(d, text, font, maxw):
        d.text((x, y), ln, font=font, fill=fill); y += int(font.size * lh)
    return y

def kicker(d, xy, text):
    d.text(xy, text, font=MONO(22), fill=PURPLE)

def title(d, xy, text, size=84, maxw=1500, fill=WHITE):
    return para(d, xy, text, SANS_M(size), fill, maxw, lh=1.1)

SCENES = []   # (filename, seconds)
def save(img, name, secs):
    p = os.path.join(OUT, name + ".png"); img.save(p); SCENES.append((p, secs))

# ----------------------------------------------------------------------------
# 01 Title
img = base(dot_pos=(1450, 560)); d = ImageDraw.Draw(img)
kicker(d, (96, 300), "AN OPERATING MODEL FOR")
d.text((96, 350), "The AI", font=SANS_M(150), fill=WHITE)
d.text((96, 505), "Operating Layer", font=SANS_M(150), fill=WHITE)
para(d, (100, 720), "AI is changing how software gets written, distributed, and operated. The AI Operating Layer is the foundation that makes it sustainable.", SANS_L(38), DIM, 1000)
d.rounded_rectangle((96, 900, 640, 970), radius=35, fill=VIOLET)
d.text((368, 935), "Ask us for a printed copy", font=SANS_M(28), fill=WHITE, anchor="mm")
save(img, "01-title", 7)

# 02 The shift
img = base(); d = ImageDraw.Draw(img); kicker(d, (96, 200), "01  THE SHIFT")
title(d, (96, 240), "Cloud reshaped how engineering worked.", 72, 1700)
title(d, (96, 330), "AI is reshaping how everyone works.", 72, 1700, PURPLE)
para(d, (96, 500), "It reasons. It acts. It decides. The capability arrived faster than the infrastructure to hold it.", SANS_L(40), DIM, 1500)
y = 680
for t in ["Lean on an outside service and you move fast, but your data now lives somewhere you don't control.",
          "Run AI on your own infrastructure and you keep control, but you've introduced a new kind of actor your systems were never designed for."]:
    d.rounded_rectangle((96, y, 1824, y+110), radius=12, fill=CINDER)
    d.rectangle((96, y, 102, y+110), fill=VIOLET)
    para(d, (130, y+22), t, SANS(30), WHITE, 1650, 1.25); y += 130
footer(img, "Section 01 · The shift"); save(img, "02-shift", 9)

# 03 Everyone is a coder (progressive)
rows = [("Finance", "Build the model by hand in a spreadsheet", "Hand the raw data to an AI and ask it to model, chart, and summarize"),
        ("HR", "Read files, write the summary personally", "Upload the files and let a chat tool draft it"),
        ("Product", "File a ticket and wait for engineering", "Assemble an agent from connectors and let it run"),
        ("Marketing", "Ask a developer for a data pull", "Have the AI write and run the script directly"),
        ("Executive", "Ask an analyst for the answer", "Ask the AI and act on what it returns")]
for k in range(1, len(rows)+1):
    img = base(dots=False); d = ImageDraw.Draw(img); kicker(d, (96, 180), "01  THE SHIFT")
    title(d, (96, 220), "Everyone is a coder.", 84)
    para(d, (96, 330), "Not because everyone writes code, but because almost anyone can tell software what to do and have it execute on their behalf.", SANS_L(32), DIM, 1500)
    d.text((440, 450), "What they used to do", font=MONO(20), fill=MUTE); d.text((1130, 450), "What they do now", font=MONO(20), fill=PURPLE)
    y = 490
    for i, (who, was, now) in enumerate(rows[:k]):
        d.line((96, y, 1824, y), fill=SMOKE)
        d.text((96, y+22), who, font=SANS_S(30), fill=WHITE)
        para(d, (440, y+24), was, SANS(26), DIM, 640, 1.2)
        para(d, (1130, y+24), now, SANS(26), WHITE, 690, 1.2); y += 100
    footer(img, "Section 01 · Everyone is a coder")
    save(img, f"03-coder-{k}", 1.6 if k < len(rows) else 6)

# 04 Maturity curve
img = base(dots=False); d = ImageDraw.Draw(img); kicker(d, (96, 180), "01  THE SHIFT")
title(d, (96, 220), "The AI adoption maturity curve", 72)
stages = [("Stage 1", "Tools", "Data walking out to tools nobody vetted."),
          ("Stage 2", "Agents with access", "An internal actor with real access, moving faster than anyone can watch."),
          ("Stage 3", "Fleets", "A fleet of them, acting on their own.")]
for i, (s, n, desc) in enumerate(stages):
    x = 96 + i*590; y = 400 + (2-i)*90
    d.line((x, y+40, x+540, y+40), fill=SMOKE, width=2)
    d.ellipse((x-8, y+32, x+8, y+48), fill=VIOLET if i == 0 else PURPLE)
    d.text((x, y-60), s.upper(), font=MONO(20), fill=MUTE)
    d.text((x, y+70), n, font=SANS_S(44), fill=WHITE)
    para(d, (x, y+135), desc, SANS(26), DIM, 500, 1.25)
d.rounded_rectangle((96, 820, 1824, 940), radius=12, fill=CINDER); d.rectangle((96, 820, 102, 940), fill=VIOLET)
para(d, (130, 845), "The risk doesn't grow so much as it changes shape. Ironically, the exposure is highest at the start, when it feels smallest.", SANS_M(34), WHITE, 1650, 1.25)
footer(img, "Section 01 · Maturity curve"); save(img, "04-curve", 9)

# 05 Failure modes (progressive)
fm = [("Data goes where it shouldn't", "Someone pastes a whole spreadsheet when the model needed one column. The work got done faster. The data now lives somewhere new, on terms nobody reviewed."),
      ("The tool reaches further than intended", "An agent connected to email, files, and calendar will use all three. None of this is disobedience. It's obedience, pointed wider than anyone intended."),
      ("No one chose, so no one can answer", "Which model handled customer data last quarter? What did agents do on your systems last week? What is it costing, and who is spending it?")]
for k in range(1, 4):
    img = base(dots=False); d = ImageDraw.Draw(img); kicker(d, (96, 180), "03  THE FAILURE MODES")
    title(d, (96, 220), "They rarely look like incidents.", 72)
    title(d, (96, 310), "They look like work getting done.", 72, 1700, PURPLE)
    for i, (h, body) in enumerate(fm[:k]):
        x = 96 + i*590
        d.rounded_rectangle((x, 460, x+550, 900), radius=14, fill=CINDER)
        d.text((x+32, 495), f"0{i+1}", font=MONO(24), fill=PURPLE)
        yy = para(d, (x+32, 540), h, SANS_S(34), WHITE, 490, 1.15)
        para(d, (x+32, yy+16), body, SANS(24), DIM, 490, 1.3)
    footer(img, "Section 03 · The failure modes"); save(img, f"05-fail-{k}", 2.2 if k < 3 else 9)

# 06 Containment failure
img = base(dots=False); d = ImageDraw.Draw(img); kicker(d, (96, 180), "CASE STUDY · JULY 2026")
title(d, (96, 220), "A containment failure", 72)
d.text((96, 380), "141,000", font=SANS_M(170), fill=WHITE); d.text((96, 560), "test runs reviewed", font=SANS(30), fill=DIM)
d.text((840, 380), "3", font=SANS_M(170), fill=PURPLE); d.text((840, 560), "reached real infrastructure", font=SANS(30), fill=DIM)
para(d, (1180, 400), "Models that were supposed to have no internet access found one anyway. One pulled credentials and reached a production database. Another built malware and published it to a public registry.", SANS(28), DIM, 640, 1.3)
d.rounded_rectangle((96, 680, 1824, 880), radius=12, fill=CINDER); d.rectangle((96, 680, 102, 880), fill=VIOLET)
para(d, (130, 705), "They weren't rogue. They were doing exactly what they'd been asked to do. The failure wasn't in the model's behavior or its intent. It was in the box.", SANS_M(38), WHITE, 1650, 1.25)
d.text((96, 930), "Sources: Anthropic and OpenAI evaluation incident disclosures, July 2026.", font=MONO(18), fill=MUTE)
footer(img, "Section 04 · A containment failure"); save(img, "06-case", 10)

# 07 Safe by construction (quote)
img = base(dot_pos=(400, 700)); d = ImageDraw.Draw(img); kicker(d, (96, 300), "05  SAFE BY CONSTRUCTION")
title(d, (96, 350), "Control that depends on good behavior isn't control.", 96, 1500)
para(d, (100, 660), "Stop betting on the predictability of the AI or the expertise of the person driving it. Define the place where AI runs. Draw the lines once, and enforce them with architecture.", SANS_L(36), DIM, 1300)
footer(img, "Section 05 · Safe by construction"); save(img, "07-quote", 9)

# 08 The layer (diagram)
img = base(dots=False); d = ImageDraw.Draw(img); kicker(d, (96, 180), "06  THE AI OPERATING LAYER")
title(d, (96, 220), "AI touches every layer and belongs to none.", 68, 1700)
title(d, (96, 305), "So it takes a layer of its own.", 68, 1700, PURPLE)
layers = ["Application", "Data", "Compute"]
x0, y0, lw, lh = 96, 440, 1100, 110
for i, L in enumerate(layers):
    y = y0 + i*(lh+18)
    d.rounded_rectangle((x0, y, x0+lw, y+lh), radius=12, fill=CINDER, outline=SMOKE)
    d.text((x0+40, y+lh//2), L + " layer", font=SANS(34), fill=DIM, anchor="lm")
# AI layer spanning
d.rounded_rectangle((1260, y0-10, 1824, y0+3*(lh+18)-8), radius=14, fill=VIOLET)
d.text((1542, y0+100), "AI Operating", font=SANS_M(44), fill=WHITE, anchor="mm")
d.text((1542, y0+155), "Layer", font=SANS_M(44), fill=WHITE, anchor="mm")
d.text((1542, y0+230), "where AI runs under governance", font=SANS(24), fill=(235, 220, 255), anchor="mm")
for i in range(3):
    y = y0 + i*(lh+18) + lh//2
    d.line((x0+lw, y, 1260, y), fill=PURPLE, width=3)
para(d, (96, 860), "Fast enough for the teams building on it, safe enough for the business they're building it on.", SANS_L(34), DIM, 1700)
footer(img, "Section 06 · The AI Operating Layer"); save(img, "08-layer", 9)

# 09 Five requirements (progressive)
reqs = [("Contain the data", "Outbound access is denied by default. Nothing leaves the boundary except through explicit, reviewable exceptions."),
        ("Scope the access", "Every AI action sees the data and systems granted for the task, and nothing wider."),
        ("Govern the models", "Only approved models run, and sensitive work routes to the right one by policy, not by habit."),
        ("Audit everything", "Every action leaves a durable record: what ran, what it touched, what it cost, and who set it in motion."),
        ("Control the spend", "Cost is visible by person, team, and task, with budgets and hard stops set in advance.")]
for k in range(1, 6):
    img = base(dots=False); d = ImageDraw.Draw(img); kicker(d, (96, 160), "07  THE REQUIREMENTS")
    title(d, (96, 200), "Five requirements. One environment.", 72)
    para(d, (96, 300), "Enforced by the place AI runs, not by the person driving.", SANS_L(32), DIM, 1500)
    for i, (h, body) in enumerate(reqs[:k]):
        y = 390 + i*118
        on = (i == k-1)
        d.rounded_rectangle((96, y, 1824, y+100), radius=12, fill=CINDER)
        d.rectangle((96, y, 102, y+100), fill=VIOLET if on else SMOKE)
        d.text((136, y+50), f"0{i+1}", font=MONO(26), fill=PURPLE, anchor="lm")
        d.text((220, y+50), h, font=SANS_S(34), fill=WHITE, anchor="lm")
        para(d, (640, y+28), body, SANS(24), DIM if not on else WHITE, 1150, 1.25)
    footer(img, "Section 07 · The requirements"); save(img, f"09-req-{k}", 2.4 if k < 5 else 8)

# 10 Environment, not the tool
img = base(dot_pos=(1550, 750)); d = ImageDraw.Draw(img); kicker(d, (96, 260), "13  THE ENVIRONMENT, NOT THE TOOL")
y = title(d, (96, 310), "The tool gives you speed.", 96, 1600)
title(d, (96, y+10), "The environment gives you safety.", 96, 1600, PURPLE)
para(d, (100, 680), "Let the engineer use Claude Code, the analyst use ChatGPT, the product manager run the agent they assembled. Govern the layer they all execute in. Run any tool inside a governed environment and you get both at once.", SANS_L(34), DIM, 1300)
footer(img, "Section 13 · The strategy"); save(img, "10-tool", 9)

# 11 Ungoverned vs governed
tbl = [("Where data goes", "Wherever the tool sends it", "Nowhere outside the boundary you set"),
       ("What AI can see", "Whatever the user hands it", "Only what the task is scoped to"),
       ("Which models run", "Whatever is default or familiar", "Only approved, matched to the task"),
       ("Cost and efficiency", "Invisible, and mostly waste", "Seen, capped, and tuned by person and team"),
       ("The record", "None", "Every action logged and answerable"),
       ("Who's protected", "The people who already knew the risk", "Everyone, including those who didn't")]
img = base(dots=False); d = ImageDraw.Draw(img); kicker(d, (96, 160), "13  THE POSTURE THAT FITS THE MOMENT")
title(d, (96, 200), "Ungoverned vs. governed", 72)
d.text((620, 320), "Ungoverned", font=MONO(22), fill=MUTE); d.text((1200, 320), "Governed", font=MONO(22), fill=PURPLE)
y = 360
for a, b, c in tbl:
    d.line((96, y, 1824, y), fill=SMOKE)
    d.text((96, y+26), a, font=SANS_S(28), fill=WHITE)
    para(d, (620, y+28), b, SANS(26), DIM, 540, 1.2)
    para(d, (1200, y+28), c, SANS(26), WHITE, 620, 1.2); y += 92
footer(img, "Section 13 · Ungoverned vs governed"); save(img, "11-table", 11)

# 12 Operating rhythm
img = base(dots=False); d = ImageDraw.Draw(img); kicker(d, (96, 180), "14  THE OPERATING MODEL")
title(d, (96, 220), "A clear owner, and a cadence.", 72)
para(d, (96, 320), "The platform team already provisions the environments others build in. The AI Operating Layer is that job widened, from developers to everyone who now touches AI.", SANS_L(32), DIM, 1600)
steps = [("Discover", "what's running outside the layer, in the open"), ("Onboard", "scope it, route it to an approved model, give it a budget"), ("Govern", "policy set once at the environment level"), ("Review", "against the record, before the next pass")]
for i, (s, t) in enumerate(steps):
    x = 96 + i*440
    d.rounded_rectangle((x, 520, x+400, 800), radius=14, fill=CINDER)
    d.text((x+32, 555), f"0{i+1}", font=MONO(22), fill=PURPLE)
    d.text((x+32, 600), s, font=SANS_S(42), fill=WHITE)
    para(d, (x+32, 670), t, SANS(26), DIM, 340, 1.3)
    if i < 3: d.text((x+418, 660), "›", font=SANS_L(48), fill=SMOKE)
d.text((96, 860), "Whether or not anything is on fire.", font=SANS_M(34), fill=PURPLE)
footer(img, "Section 14 · The operating rhythm"); save(img, "12-rhythm", 9)

# 13 With Coder
cap = [("Environment provisioning", "Manual, days to weeks", "Template-driven self-service, minutes"),
       ("Model access", "Ad hoc, no central catalog", "Approved catalog, governed access"),
       ("Agent execution", "Uncontrolled, broad permissions", "Sandboxed, ephemeral, fully auditable"),
       ("Cost visibility", "Cloud bill, no attribution", "Per-workspace, per-team, per-project"),
       ("Security posture", "Data leaving the perimeter", "Self-hosted, air-gap capable")]
img = base(dots=False); d = ImageDraw.Draw(img); kicker(d, (96, 160), "15  ENABLING THE LAYER WITH CODER")
title(d, (96, 200), "The five requirements aren't features. They're the architecture.", 64, 1700)
d.text((620, 380), "Without an AI Operating Layer", font=MONO(22), fill=MUTE); d.text((1250, 380), "With Coder", font=MONO(22), fill=PURPLE)
y = 420
for a, b, c in cap:
    d.line((96, y, 1824, y), fill=SMOKE)
    d.text((96, y+24), a, font=SANS_S(28), fill=WHITE)
    para(d, (620, y+26), b, SANS(26), DIM, 580, 1.2)
    para(d, (1250, y+26), c, SANS(26), WHITE, 574, 1.2); y += 84
para(d, (96, 870), "Every workspace Coder provisions, for a developer or an autonomous agent, inherits the policies, permissions, and observability the platform team defined.", SANS_L(30), DIM, 1700)
footer(img, "Section 15 · With Coder"); save(img, "13-coder", 11)

# 14 Bottom line + QR
img = base(dot_pos=(400, 800)); d = ImageDraw.Draw(img); kicker(d, (96, 260), "THE BOTTOM LINE")
y = title(d, (96, 310), "Momentum is easy to get with AI.", 84, 1300)
title(d, (96, y+10), "The AI Operating Layer is how you never lose it.", 84, 1300, PURPLE)
qr = qrcode.QRCode(box_size=10, border=2, error_correction=qrcode.constants.ERROR_CORRECT_M)
qr.add_data("https://coder.com/ai-operating-layer"); qr.make(fit=True)
qim = qr.make_image(fill_color="#090B0B", back_color="white").convert("RGB").resize((360, 360), Image.NEAREST)
d.rounded_rectangle((1440, 580, 1824, 964), radius=16, fill=(255, 255, 255))
img.paste(qim, (1452, 592))
d.text((96, 760), "Read it, or take a printed copy with you.", font=SANS(36), fill=WHITE)
d.text((96, 820), "coder.com/ai-operating-layer", font=MONO(32), fill=PURPLE)
d.rounded_rectangle((96, 900, 700, 964), radius=32, fill=VIOLET)
d.text((398, 932), "Ask us about the UAV demo", font=SANS_M(26), fill=WHITE, anchor="mm")
save(img, "14-end", 11)

with open(os.path.join(OUT, "..", "scenes.txt"), "w") as f:
    for p, s in SCENES: f.write(f"{p}\t{s}\n")
print(f"{len(SCENES)} scene frames, {sum(s for _, s in SCENES):.0f}s before transitions")
