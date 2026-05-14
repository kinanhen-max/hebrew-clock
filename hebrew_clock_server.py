#!/usr/bin/env python3
"""
Hebrew Word Clock Server - Full version matching Yanir Tzabary's design
Serves a 800x480 PNG with niqud, exact minute words, and animal of the day.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image, ImageDraw, ImageFont
import datetime, io, os, urllib.request, sys

PORT = int(os.environ.get("PORT", 8765))

# ── Hours (with niqud) ────────────────────────────────
HOURS = [
    "אַחַת", "שְׁתַּיִם", "שָׁלוֹשׁ", "אַרְבַּע", "חָמֵשׁ", "שֵׁשׁ",
    "שֶׁבַע", "שְׁמוֹנֶה", "תֵּשַׁע", "עֶשֶׂר", "אַחַת עֶשְׂרֵה", "שְׁתֵּים עֶשְׂרֵה"
]

HOURS_LAMED = [
    "לְאַחַת", "לִשְׁתַּיִם", "לְשָׁלוֹשׁ", "לְאַרְבַּע", "לְחָמֵשׁ", "לְשֵׁשׁ",
    "לְשֶׁבַע", "לִשְׁמוֹנֶה", "לְתֵשַׁע", "לְעֶשֶׂר", "לְאַחַת עֶשְׂרֵה", "לִשְׁתֵּים עֶשְׂרֵה"
]

# ── All 60 minute prefixes (with niqud) ───────────────
MINUTE_PREFIX = [
    "",                               # :00
    "וְדַקָּה אַחַת",                # :01
    "וּשְׁתֵּי דַקּוֹת",             # :02
    "וְשָׁלוֹשׁ דַקּוֹת",            # :03
    "וְאַרְבַּע דַקּוֹת",            # :04
    "וְחָמֵשׁ דַקּוֹת",              # :05
    "וְשֵׁשׁ דַקּוֹת",               # :06
    "וְשֶׁבַע דַקּוֹת",              # :07
    "וּשְׁמוֹנֶה דַקּוֹת",           # :08
    "וְתֵשַׁע דַקּוֹת",              # :09
    "וְעֶשֶׂר דַקּוֹת",              # :10
    "וְאַחַת עֶשְׂרֵה דַּקּוֹת",     # :11
    "וּשְׁתֵּים עֶשְׂרֵה דַּקּוֹת",  # :12
    "וּשְׁלוֹשׁ עֶשְׂרֵה דַּקּוֹת",  # :13
    "וְאַרְבַּע עֶשְׂרֵה דַּקּוֹת",  # :14
    "וָרֶבַע",                       # :15
    "וְשֵׁשׁ עֶשְׂרֵה דַּקּוֹת",     # :16
    "וּשְׁבַע עֶשְׂרֵה דַּקּוֹת",    # :17
    "וּשְׁמוֹנֶה עֶשְׂרֵה דַּקּוֹת", # :18
    "וּתְשַׁע עֶשְׂרֵה דַּקּוֹת",    # :19
    "וְעֶשְׂרִים דַקּוֹת",           # :20
    "וְעֶשְׂרִים וְאַחַת",           # :21
    "וְעֶשְׂרִים וּשְׁתַּיִם",       # :22
    "וְעֶשְׂרִים וְשָׁלוֹשׁ",        # :23
    "וְעֶשְׂרִים וְאַרְבַּע",        # :24
    "וְעֶשְׂרִים וְחָמֵשׁ",          # :25
    "וְעֶשְׂרִים וְשֵׁשׁ",           # :26
    "וְעֶשְׂרִים וְשֶׁבַע",          # :27
    "וְעֶשְׂרִים וּשְׁמוֹנֶה",       # :28
    "וְעֶשְׂרִים וְתֵשַׁע",          # :29
    "וָחֵצִי",                       # :30
    "וּשְׁלוֹשִׁים וְאַחַת",         # :31
    "וּשְׁלוֹשִׁים וּשְׁתַּיִם",     # :32
    "וּשְׁלוֹשִׁים וְשָׁלוֹשׁ",      # :33
    "וּשְׁלוֹשִׁים וְאַרְבַּע",      # :34
    "וּשְׁלוֹשִׁים וְחָמֵשׁ",        # :35
    "וּשְׁלוֹשִׁים וְשֵׁשׁ",         # :36
    "וּשְׁלוֹשִׁים וְשֶׁבַע",        # :37
    "וּשְׁלוֹשִׁים וּשְׁמוֹנֶה",     # :38
    "וּשְׁלוֹשִׁים וְתֵשַׁע",        # :39
    "",                               # :40 (subtract)
    "וְאַרְבָּעִים וְאַחַת",         # :41
    "וְאַרְבָּעִים וּשְׁתַּיִם",     # :42
    "וְאַרְבָּעִים וְשָׁלוֹשׁ",      # :43
    "וְאַרְבָּעִים וְאַרְבַּע",      # :44
    "",                               # :45 (subtract)
    "וְאַרְבָּעִים וְשֵׁשׁ",         # :46
    "וְאַרְבָּעִים וְשֶׁבַע",        # :47
    "וְאַרְבָּעִים וּשְׁמוֹנֶה",     # :48
    "וְאַרְבָּעִים וְתֵשַׁע",        # :49
    "",                               # :50 (subtract)
    "וַחֲמִשִּׁים וְאַחַת",          # :51
    "וַחֲמִשִּׁים וּשְׁתַּיִם",      # :52
    "וַחֲמִשִּׁים וְשָׁלוֹשׁ",       # :53
    "וַחֲמִשִּׁים וְאַרְבַּע",       # :54
    "",                               # :55 (subtract)
    "וַחֲמִשִּׁים וְשֵׁשׁ",          # :56
    "וַחֲמִשִּׁים וְשֶׁבַע",         # :57
    "וַחֲמִשִּׁים וּשְׁמוֹנֶה",      # :58
    "וַחֲמִשִּׁים וְתֵשַׁע",         # :59
]

SUBTRACT_AMOUNT = {
    40: "עֶשְׂרִים",
    45: "רֶבַע",
    50: "עֲשָׂרָה",
    55: "חֲמִשָּׁה",
}

def is_subtract(m):
    return m in SUBTRACT_AMOUNT

def get_time_period(hour):
    if 6 <= hour < 12:  return "בַּבֹּקֶר"
    if 12 <= hour < 18: return "בַּצָּהֳרַיִם"
    if 18 <= hour < 24: return "בָּעֶרֶב"
    if 0 <= hour < 4:   return "בַּלַּיְלָה"
    return "לִפְנוֹת בֹּקֶר"

def get_time_lines(hour24, minute):
    hour12 = hour24 % 12 or 12
    period = get_time_period(hour24)

    if is_subtract(minute):
        next_hour = hour12 % 12  # 12 → 0 → HOURS_LAMED[0]
        line1 = SUBTRACT_AMOUNT[minute] + " " + HOURS_LAMED[next_hour]
        return [line1, period]
    elif minute == 0:
        return [HOURS[hour12 - 1], period]
    else:
        min_part = MINUTE_PREFIX[minute]
        hour_part = HOURS[hour12 - 1]
        combined = hour_part + " " + min_part
        # If combined is very long, split to two lines
        if len(combined) > 25:
            return [hour_part, min_part, period]
        return [combined, period]

# ── Animals (with niqud) ─────────────────────────────
ANIMALS = [
    ("כֶּלֶב",        "הֶחָבֵר הֲכִי טוֹב שֶׁל הָאָדָם"),
    ("חָתוּל",        "חַיָּה עַצְמָאִית שֶׁאוֹהֶבֶת לִישֹׁן"),
    ("אַרְנָב",       "בַּעַל אָזְנַיִם אֲרֻכּוֹת"),
    ("אוֹגֵר",        "אוֹגֶרֶת אֹכֶל בַּלְּחָיַיִם"),
    ("סוּס",          "חַיָּה חֲזָקָה לִרְכֹּב עָלֶיהָ"),
    ("פָּרָה",        "נוֹתֶנֶת לָנוּ חָלָב"),
    ("כִּבְשָׂה",     "צֶמֶר מְתֻלְתָּל וְנָעִים"),
    ("תַּרְנְגוֹל",   "מֵעִיר אֶת כֻּלָּם בַּבֹּקֶר"),
    ("בַּרְוָז",      "אוֹהֵב לִשְׂחוֹת בָּאֲגַם"),
    ("אַרְיֵה",       "מֶלֶךְ הַחַיּוֹת"),
    ("פִּיל",         "הַחַיָּה הַגְּדוֹלָה בְּיוֹתֵר"),
    ("גִּ׳ירָפָה",    "צַוָּאר אָרֹךְ לְהַגִּיעַ לְעָלִים"),
    ("זֶבְּרָה",      "פַּסִּים שָׁחֹר וְלָבָן"),
    ("קוֹף",          "אוֹהֵב בָּנָנוֹת וְעֵצִים"),
    ("נָמֵר",         "חָתוּל גָּדוֹל וּמְנֻמָּר"),
    ("הִיפּוֹפּוֹטָם", "אוֹהֵב לִרְבֹּץ בַּמַּיִם"),
    ("קַרְנַף",       "קֶרֶן גְּדוֹלָה עַל הָאַף"),
    ("לִוְיָתָן",     "עֲנַק הָאוֹקְיָנוֹס"),
    ("דּוֹלְפִין",    "קוֹפֵץ מֵעַל הַגַּלִּים"),
    ("כָּרִישׁ",      "טוֹרֵף הַיָּם"),
    ("צַב יָם",       "שׂוֹחֶה לְאַט עִם שִׁרְיוֹן"),
    ("תְּמָנוּן",     "שְׁמוֹנֶה זְרוֹעוֹת"),
    ("דַּג זָהָב",    "דָּג קָטָן בְּאַקְוַרְיוּם"),
    ("דֹּב",          "אוֹהֵב דְּבַשׁ וְשֵׁנָה"),
    ("שׁוּעָל",       "חָכָם עִם זָנָב פַּרְוָתִי"),
    ("סְנָאִי",       "אוֹסֵף אֱגוֹזִים עַל עֵצִים"),
    ("צְבִי",         "רָץ מַהֵר עִם קַרְנַיִם"),
    ("קִפּוֹד",       "קוֹצִים מְגַנִּים עָלָיו"),
    ("זְאֵב",         "צוֹרֵחַ אֶל הַיָּרֵחַ"),
    ("יַנְשׁוּף",     "צִפּוֹר לַיְלָה עִם עֵינַיִם גְּדוֹלוֹת"),
]

def get_animal(hour24, minute):
    half_hour = hour24 * 2 + (1 if minute >= 30 else 0)
    return ANIMALS[half_hour % len(ANIMALS)]

# ── Font handling ─────────────────────────────────────
FONT_PATH = "/tmp/NotoSerifHebrew-Bold.ttf"
FONT_URLS = [
    "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSerifHebrew/NotoSerifHebrew-Bold.ttf",
    "https://github.com/notofonts/hebrew/raw/main/fonts/NotoSerifHebrew/hinted/ttf/NotoSerifHebrew-Bold.ttf",
    "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansHebrew/NotoSansHebrew-Bold.ttf",
]

FONT_AVAILABLE = False

def download_font():
    global FONT_AVAILABLE
    if os.path.exists(FONT_PATH) and os.path.getsize(FONT_PATH) > 10000:
        FONT_AVAILABLE = True
        return
    for url in FONT_URLS:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                if len(data) > 10000:
                    with open(FONT_PATH, 'wb') as f:
                        f.write(data)
                    print(f"Font downloaded: {len(data)} bytes from {url}")
                    FONT_AVAILABLE = True
                    return
        except Exception as e:
            print(f"Font download failed ({url}): {e}")

def get_font(size):
    if FONT_AVAILABLE and os.path.exists(FONT_PATH):
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except:
            pass
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(path):
            try: return ImageFont.truetype(path, size)
            except: pass
    return ImageFont.load_default()

# ── Time ──────────────────────────────────────────────
def get_israel_time():
    utc = datetime.datetime.utcnow()
    is_dst = 3 <= utc.month <= 10
    return utc + datetime.timedelta(hours=3 if is_dst else 2)

# ── Image generation ──────────────────────────────────
def generate_clock_image():
    now = get_israel_time()
    hour24 = now.hour
    minute = (now.minute // 5) * 5

    W, H = 800, 480
    img = Image.new("L", (W, H), color=255)
    draw = ImageDraw.Draw(img)

    lines = get_time_lines(hour24, minute)
    period_words = ["בַּבֹּקֶר", "בַּצָּהֳרַיִם", "בָּעֶרֶב", "בַּלַּיְלָה", "לִפְנוֹת בֹּקֶר"]

    font_large = get_font(90)
    font_medium = get_font(55)
    font_small = get_font(28)

    # Draw time lines
    time_lines = [l for l in lines if l not in period_words]
    period_line = next((l for l in lines if l in period_words), "")

    n = len(time_lines)
    line_h = 110
    total_h = n * line_h
    start_y = (H - 60 - total_h) // 2 + 20

    for i, line in enumerate(time_lines):
        y = start_y + i * line_h
        draw.text((W // 2, y), line, font=font_large, fill=0, anchor="mm")

    # Period (בבוקר etc)
    if period_line:
        period_y = start_y + n * line_h + 15
        draw.text((W // 2, period_y), period_line, font=font_medium, fill=0, anchor="mm")

    # Animal at bottom
    animal_name, animal_desc = get_animal(hour24, minute)
    draw.line([(40, H - 70), (W - 40, H - 70)], fill=180, width=1)
    draw.text((W // 2, H - 48), animal_name + " - " + animal_desc, font=font_small, fill=80, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()

# ── Server ────────────────────────────────────────────
class ClockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/clock.png", "/clock", "/"):
            try:
                img = generate_clock_image()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(img)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(img)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode())
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    print(f"Starting Hebrew Clock Server on port {PORT}", flush=True)
    download_font()
    HTTPServer(("0.0.0.0", PORT), ClockHandler).serve_forever()
