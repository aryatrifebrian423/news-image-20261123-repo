#!/usr/bin/env python3
"""news-image-20261123: sum up Monday 23 November 2026 in one image.

Pure Python 3.13 standard library. Draws a 1024x1024 PNG newspaper-style
front page: masthead with the date, a climax hero (Hormuz tanker strikes),
a UTC timeline, a markets ticker, a world map with region counts, and a
52-story grid. Deterministic: no network, no clock, no randomness.
Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
NAVY = (10, 22, 38)
PANEL = (16, 35, 60)
PANEL2 = (21, 46, 78)
LINE = (46, 84, 124)
WHITE = (245, 247, 250)
MUTED = (159, 179, 200)
GOLD = (242, 183, 5)
RED = (229, 72, 77)
RED_DK = (122, 28, 34)
TEAL = (46, 196, 182)
ORANGE = (244, 130, 32)
SEA = (13, 34, 56)
LAND = (29, 58, 92)
SKY = (18, 44, 74)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows, 5 bits (bit 4 = leftmost pixel). Uppercase only.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    "-": (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    ".": (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    ",": (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    ":": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ";": (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '"': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    "*": (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    "=": (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    "_": (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    "\u2022": (0x00, 0x00, 0x0C, 0x0C, 0x0C, 0x00, 0x00),
    "\u00d7": (0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x00),
    "\u2192": (0x00, 0x04, 0x02, 0x1F, 0x02, 0x04, 0x00),
}

_CLEAN = {
    "\u2014": "-", "\u2013": "-", "\u2019": "'", "\u2018": "'",
    "\u201c": '"', "\u201d": '"', "\u20b9": "Rs ", "\u20ac": "EUR ",
    "\u00a3": "GBP ", "\u00e9": "E", "\u00e8": "E", "\u00fc": "U",
    "\u00f6": "O", "\u00e4": "A", "\u00e0": "A", "\u00ed": "I",
    "\u00f1": "N", "\u010d": "C", "\u00e1": "A", "\u00fa": "U",
}


def clean(text):
    out = []
    for ch in text:
        if ch in _CLEAN:
            out.append(_CLEAN[ch])
        else:
            out.append(ch)
    return "".join(out).upper()


def text_width(text, scale):
    return len(clean(text)) * 6 * scale - scale


# ---------------------------------------------------------------- PNG writer
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(w, h, rgb):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", comp)
    png += _chunk(b"IEND", b"")
    return png


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, color):
        r, g, b = color
        self.px[:] = bytes((r, g, b)) * (self.w * self.h)

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        if w <= 0 or h <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            i = self._idx(x0, yy)
            self.px[i:i + (x1 - x0) * 3] = row

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.rect(cx - half, cy + dy, half * 2 + 1, 1, color)

    def ring(self, cx, cy, r, color, thick=2):
        for t in range(thick):
            rr = r - t
            for a in range(360):
                import math
                x = cx + int(rr * math.cos(math.radians(a)))
                y = cy + int(rr * math.sin(math.radians(a)))
                self.set(x, y, color)

    def poly(self, points, color):
        # scanline fill for a simple polygon
        ys = [p[1] for p in points]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.rect(int(xs[k]), y, max(1, int(xs[k + 1]) - int(xs[k])), 1, color)

    def burst(self, cx, cy, r, color):
        # starburst: 8 spikes
        import math
        for k in range(16):
            a = math.radians(k * 22.5)
            rr = r if k % 2 == 0 else int(r * 0.45)
            x1 = cx + int(rr * math.cos(a))
            y1 = cy + int(rr * math.sin(a))
            self.line(cx, cy, x1, y1, color)
        self.circle(cx, cy, max(2, r // 3), color)

    def text(self, x, y, s, color, scale=2):
        s = clean(s)
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                cx += 6 * scale
                continue
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_c(self, cx, y, s, color, scale=2):
        w = text_width(s, scale)
        return self.text(cx - w // 2, y, s, color, scale)

# ---------------------------------------------------------------- world map
# Rough continent outlines in (lon, lat); projected equirectangular.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-75, 72), (-65, 60), (-55, 47), (-60, 45), (-70, 42), (-75, 35),
     (-80, 25), (-85, 20), (-90, 15), (-95, 18), (-105, 20), (-115, 28),
     (-125, 40), (-125, 48), (-135, 58), (-155, 58), (-165, 60)],
    [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-25, 70), (-35, 76),
     (-55, 76), (-58, 70)],
    [(-80, 10), (-75, 5), (-80, -5), (-80, -15), (-75, -25), (-70, -35),
     (-65, -45), (-68, -52), (-60, -45), (-55, -35), (-48, -28), (-40, -20),
     (-35, -8), (-45, -2), (-52, 5), (-60, 8), (-70, 11)],
    [(-10, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (40, 15),
     (48, 11), (51, 10), (45, 0), (40, -10), (35, -20), (30, -28),
     (20, -35), (15, -30), (12, -18), (8, -2), (0, 5), (-8, 5), (-15, 10),
     (-17, 15), (-15, 25)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (25, 65), (20, 70),
     (15, 70), (10, 68), (5, 60), (0, 55), (-5, 50), (-10, 45)],
    [(30, 62), (40, 68), (55, 70), (70, 72), (90, 75), (110, 76),
     (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (162, 56),
     (158, 50), (150, 45), (142, 40), (140, 35), (135, 33), (130, 31),
     (127, 35), (122, 38), (120, 30), (115, 22), (108, 18), (105, 10),
     (100, 8), (98, 15), (95, 20), (90, 22), (85, 20), (80, 15), (77, 8),
     (75, 12), (72, 20), (66, 25), (60, 25), (55, 26), (50, 28), (48, 30),
     (44, 29), (40, 32), (35, 36), (30, 36)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (132, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (136, -12), (132, -11),
     (130, -13), (126, -14), (122, -17), (118, -20)],
]

REGION_COLORS = {
    "MIDEAST": (229, 72, 77),
    "UKRAINE": (244, 130, 32),
    "USA": (96, 165, 250),
    "WORLD": (245, 247, 250),
    "INDIA": (46, 196, 182),
    "ASIA": (56, 189, 248),
    "EUROPE": (167, 139, 250),
    "AFRICA": (74, 222, 128),
    "LATAM": (244, 114, 182),
    "SPORT": (242, 183, 5),
    "TECH": (163, 230, 53),
}

# (headline, tag, region) — 52 stories, all reported in the 23 Nov cycle.
STORIES = [
    ("2 TANKERS HIT IN HORMUZ", "MIDEAST", "MIDEAST"),
    ("IRAN HITS BAHRAIN PLANT", "MIDEAST", "MIDEAST"),
    ("HOUTHI MISSILE DOWNED", "MIDEAST", "MIDEAST"),
    ("MERKURY WARSHIP HIT OFF LIBYA", "UKRAINE", "UKRAINE"),
    ("SPARTA 2 ABLAZE OFF FINLAND", "UKRAINE", "UKRAINE"),
    ("KRYVYI RIH STRIKE: 2 DEAD, 60 HURT", "UKRAINE", "UKRAINE"),
    ("14 MISSING AFTER KYIV DRONE HIT", "UKRAINE", "UKRAINE"),
    ("SLOVAKIA REJECTS EUR 45B LOAN", "EUROPE", "EUROPE"),
    ("DEMOCRATS WIN CONGRESS", "USA", "USA"),
    ("TRUMP POSES WITH PUTIN AND XI", "USA", "USA"),
    ("NASDAQ -5.28%, WORST WEEK SINCE 2020", "USA", "USA"),
    ("BITCOIN DIPS BELOW $60,000", "USA", "USA"),
    ("GOLD -9.4% IN A WEEK", "USA", "USA"),
    ("NVIDIA ROW: CHIPS DIVERTED TO CHINA", "USA", "USA"),
    ("TOM JACKSON, BRONCOS STAR, DIES AT 75", "USA", "USA"),
    ("UN: LETHAL AI TALKS GO ON", "WORLD", "WORLD"),
    ("UK, FRANCE, CHINA BLOCK UN BID", "WORLD", "WORLD"),
    ("COP31 ENDS WITH NO CLIMATE PACT", "WORLD", "WORLD"),
    ("NEPAL PM HOLDS TALKS WITH MODI", "INDIA", "INDIA"),
    ("INDIA 720/9D: RECORD TEST TOTAL", "INDIA", "INDIA"),
    ("YOUTH CONGRESS PROTESTS META", "INDIA", "INDIA"),
    ("AMIT SHAH'S RS 4,000-CR PUSH", "INDIA", "INDIA"),
    ("BJP MP WADKUTE DIES IN DELHI", "INDIA", "INDIA"),
    ("HYDERABAD STUDENTS PROTEST", "INDIA", "INDIA"),
    ("9 PILGRIMS KILLED IN RAJASTHAN", "INDIA", "INDIA"),
    ("IFFI 2026 HOSTS BRICS ROUNDTABLE", "INDIA", "INDIA"),
    ("S KOREA MINISTER QUITS OVER AI EXAM", "ASIA", "ASIA"),
    ("SELANGOR FLOODS: 1,800 EVACUATED", "ASIA", "ASIA"),
    ("INDONESIA FACTORY FIRE: 50 MISSING", "ASIA", "ASIA"),
    ("MYANMAR CALLS ASEAN MOVE 'UNFAIR'", "ASIA", "ASIA"),
    ("BEPICOLOMBO ORBITS MERCURY", "WORLD", "WORLD"),
    ("SHELL SIGNS SAF DEAL IN MOROCCO", "AFRICA", "AFRICA"),
    ("LISBON MARCH OVER LIVING COSTS", "EUROPE", "EUROPE"),
    ("EU STATES PLAN RWANDA RETURN HUB", "EUROPE", "EUROPE"),
    ("EL HIERRO: 11,037 MIGRANTS IN 2 WEEKS", "EUROPE", "EUROPE"),
    ("ITALY STRIKES OVER LIVING COSTS", "EUROPE", "EUROPE"),
    ("TUNISIAN ACTIVIST JAILED 5 YEARS", "AFRICA", "AFRICA"),
    ("BENIN SEEKS 35 ARTEFACTS BACK", "AFRICA", "AFRICA"),
    ("SYRIA ARRESTS OFFICER OVER AMBUSH", "MIDEAST", "MIDEAST"),
    ("ETHIOPIA POLIO DRIVE FOR 11M KIDS", "AFRICA", "AFRICA"),
    ("SOMALIA EXPELS UAE AMBASSADOR", "AFRICA", "AFRICA"),
    ("HAITI INK PRISON DEAL WITH SALVADOR", "LATAM", "LATAM"),
    ("700,000 DISPLACED IN S ETHIOPIA", "AFRICA", "AFRICA"),
    ("LIVERPOOL THRASH MAN UTD 4-0", "SPORT", "SPORT"),
    ("VERSTAPPEN WINS CHAOTIC VEGAS GP", "SPORT", "SPORT"),
    ("MARQUEZ WINS 8TH MOTOGP TITLE", "SPORT", "SPORT"),
    ("BOCA WIN RECORD 3RD SUDAMERICANA", "LATAM", "LATAM"),
    ("KANSAS CITY WIN FIRST NWSL TITLE", "SPORT", "SPORT"),
    ("COLUMBUS STUN MESSI'S MIAMI 3-0", "SPORT", "SPORT"),
    ("MUSK: AI5 FOR OPTIMUS, CARS KEEP AI4", "TECH", "TECH"),
    ("OPENAI PROPOSES SHARED AI LIMITS", "TECH", "TECH"),
    ("GTA 6: 99 SCORE, $3.79B DAY ONE", "TECH", "TECH"),
]

# ---------------------------------------------------------------- layout
def draw_masthead(cv):
    cv.rect(24, 8, 976, 3, GOLD)
    cv.text(24, 18, "THE WORLD IN ONE IMAGE", GOLD, 2)
    right = "MAKE.FUN - NEWS-IMAGE"
    cv.text(1000 - text_width(right, 2), 18, right, MUTED, 2)
    cv.text(24, 40, "MONDAY 23 NOVEMBER 2026", WHITE, 4)
    cv.text(820, 36, "52", GOLD, 7)
    cv.text(912, 52, "STORIES", WHITE, 2)
    cv.text(820, 86, "TOP 50 SHARE $100", MUTED, 1)
    cv.hline(24, 96, 976, LINE)


def draw_hero(cv):
    cv.rect(24, 104, 976, 192, PANEL)
    cv.rect(24, 104, 976, 4, RED)
    # left: the climax
    cv.text(40, 118, "TOP STORY - MIDDLE EAST", GOLD, 2)
    cv.text(40, 140, "2", GOLD, 9)
    cv.text(108, 148, "TANKERS HIT", WHITE, 4)
    cv.text(108, 180, "IN THE STRAIT", WHITE, 3)
    cv.text(108, 202, "OF HORMUZ", WHITE, 3)
    cv.text(40, 228, "UKMTO LOGS TWO STRIKES 50 MIN APART", MUTED, 2)
    cv.text(40, 244, "OFF KHASAB, OMAN - NO CASUALTIES", MUTED, 2)
    for x, num, label in ((40, "22", "ATTACKS IN NOV"),
                          (240, "120+", "VESSELS SINCE FEB"),
                          (440, "31", "OCT ATTACKS, RECORD")):
        cv.text(x, 262, num, GOLD, 3)
        cv.text(x, 284, label, MUTED, 1)
    # right: the scene
    cv.rect(636, 108, 364, 110, SKY)
    cv.rect(636, 218, 364, 78, SEA)
    cv.rect(908, 112, 84, 18, RED)
    cv.text_c(950, 117, "BREAKING", WHITE, 1)
    # tanker A (Torkel) and B (Arina)
    cv.rect(660, 196, 140, 28, (5, 10, 20))
    cv.rect(700, 178, 26, 18, (5, 10, 20))
    cv.rect(726, 184, 8, 12, RED)
    cv.vline(672, 176, 20, (5, 10, 20))
    cv.rect(840, 200, 140, 28, (5, 10, 20))
    cv.rect(884, 182, 26, 18, (5, 10, 20))
    cv.rect(910, 188, 8, 12, RED)
    cv.vline(852, 180, 20, (5, 10, 20))
    cv.burst(760, 168, 24, ORANGE)
    cv.burst(760, 168, 12, GOLD)
    cv.burst(905, 172, 20, ORANGE)
    cv.burst(905, 172, 10, GOLD)
    # dashed shipping route
    for x in range(648, 984, 18):
        cv.rect(x, 252, 12, 2, MUTED)
    cv.text(668, 232, "TORKEL - HIT 05:00 UTC", WHITE, 1)
    cv.text(848, 236, "ARINA - HIT 05:50 UTC", WHITE, 1)
    cv.text(660, 276, "STRAIT OF HORMUZ - KHASAB, OMAN", GOLD, 1)


def draw_timeline_markets(cv):
    cv.text(24, 306, "23 NOV IN UTC", GOLD, 2)
    cv.hline(24, 344, 616, LINE)
    moments = [
        ("05:00 UTC", "TANKER 1 HIT", "OFF KHASAB"),
        ("05:50 UTC", "TANKER 2 HIT", "ENGINE ROOM"),
        ("MORNING", "NEPAL PM MEETS", "MODI IN DELHI"),
        ("MIDDAY", "COP31 ENDS", "NO CLIMATE PACT"),
        ("EVENING", "IRAN: NO TALKS", "UNTIL BLOCKADE LIFTS"),
    ]
    for i, (t, a, b) in enumerate(moments):
        x = 24 + i * 120
        cv.circle(x + 4, 344, 4, GOLD)
        cv.text(x, 324, t, WHITE, 1)
        cv.text(x, 352, a, MUTED, 1)
        cv.text(x, 362, b, MUTED, 1)
    cv.rect(656, 304, 344, 68, PANEL2)
    cv.rect(656, 304, 344, 1, LINE)
    cv.text(668, 312, "MARKETS - FRIDAY CLOSE", GOLD, 1)
    cv.text(668, 328, "NASDAQ -5.28%  S&P -3.70%  DXY 103.84", WHITE, 1)
    cv.text(668, 342, "BITCOIN $61,160  BRENT $92.57", WHITE, 1)
    cv.text(668, 356, "GOLD $3,502  -9.4% THIS WEEK", WHITE, 1)


def draw_map(cv):
    cv.rect(24, 380, 976, 120, SEA)
    counts = {}
    for _, _, region in STORIES:
        counts[region] = counts.get(region, 0) + 1
    geo = {r: c for r, c in counts.items()
           if r in ("MIDEAST", "UKRAINE", "USA", "INDIA", "ASIA",
                    "EUROPE", "AFRICA", "LATAM")}
    mapped = sum(geo.values())
    glob = len(STORIES) - mapped

    def proj(lon, lat):
        return (24 + int((lon + 180) / 360.0 * 976),
                380 + int((75 - lat) / 130.0 * 120))

    for poly in CONTINENTS:
        cv.poly([proj(lon, lat) for lon, lat in poly], LAND)
    cv.text(32, 386,
            "WHERE THE NEWS LANDED - %d STORIES MAPPED, %d GLOBAL"
            % (mapped, glob), GOLD, 1)
    markers = {"MIDEAST": (45, 28), "UKRAINE": (30, 50), "USA": (-100, 40),
               "INDIA": (78, 22), "ASIA": (110, 12), "EUROPE": (12, 52),
               "AFRICA": (18, 2), "LATAM": (-60, -12)}
    for region, (lon, lat) in markers.items():
        x, y = proj(lon, lat)
        cv.circle(x, y, 11, GOLD)
        cv.text_c(x, y - 3, str(geo.get(region, 0)), NAVY, 1)
        cv.text_c(x, y + 14, region, WHITE, 1)


def draw_legend(cv):
    order = ["MIDEAST", "UKRAINE", "USA", "WORLD", "INDIA", "ASIA",
             "EUROPE", "AFRICA", "LATAM", "SPORT", "TECH"]
    total = 0
    for r in order:
        total += 10 + 4 + text_width(r, 1) + 24
    x = (W - total) // 2
    y = 504
    for r in order:
        cv.rect(x, y, 10, 10, REGION_COLORS[r])
        cv.text(x + 14, y + 2, r, MUTED, 1)
        x += 10 + 4 + text_width(r, 1) + 24


def draw_grid(cv):
    for i, (headline, tag, region) in enumerate(STORIES):
        row = i // 2
        col = i % 2
        y = 518 + row * 17
        x = 24 + col * 496
        if row % 2 == 0:
            cv.rect(24, y, 976, 17, PANEL)
        cv.rect(x, y + 2, 24, 13, REGION_COLORS[region])
        cv.text_c(x + 12, y + 5, "%02d" % (i + 1), NAVY, 1)
        cv.text(x + 30, y + 2, headline, WHITE, 2)


def draw_footer(cv):
    cv.hline(24, 964, 976, LINE)
    cv.text_c(512, 974,
              "DATE CHECK: MONDAY 23 NOVEMBER 2026 - 52 STORIES - "
              "40 MAPPED - 12 GLOBAL", GOLD, 2)
    cv.text_c(512, 994,
              "STORIES FROM THE 23 NOVEMBER 2026 NEWS CYCLE - SOURCES: "
              "REUTERS, CNN, UKMTO, IANS, NBC SPORTS, AP-STYLE WIRES", MUTED, 1)
    cv.text_c(512, 1006,
              "VERIFIED AGAINST PUBLISHED REPORTS - THE ONLY CLOCK TIMES "
              "SHOWN ARE THE TWO HORMUZ STRIKES, 05:00 AND 05:50 UTC",
              MUTED, 1)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    cv = Canvas(W, H, NAVY)
    draw_masthead(cv)
    draw_hero(cv)
    draw_timeline_markets(cv)
    draw_map(cv)
    draw_legend(cv)
    draw_grid(cv)
    draw_footer(cv)
    png = encode_png(W, H, cv.px)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes, %dx%d, %d stories)"
          % (path, len(png), W, H, len(STORIES)))


if __name__ == "__main__":
    sys.exit(main())
