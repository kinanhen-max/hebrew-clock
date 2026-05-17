#!/usr/bin/env python3
"""
Hebrew Word Clock + Weather + Analog Clock
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image, ImageDraw, ImageFont
import datetime, io, os, urllib.request, json, sys, math

PORT = int(os.environ.get("PORT", 8765))

# ── Hebrew time tables ────────────────────────────────
HOURS = [
    "אַחַת", "שְׁתַּיִם", "שָׁלוֹשׁ", "אַרְבַּע", "חָמֵשׁ", "שֵׁשׁ",
    "שֶׁבַע", "שְׁמוֹנֶה", "תֵּשַׁע", "עֶשֶׂר", "אַחַת עֶשְׂרֵה", "שְׁתֵּים עֶשְׂרֵה"
]
HOURS_LAMED = [
    "לְאַחַת", "לִשְׁתַּיִם", "לְשָׁלוֹשׁ", "לְאַרְבַּע", "לְחָמֵשׁ", "לְשֵׁשׁ",
    "לְשֶׁבַע", "לִשְׁמוֹנֶה", "לְתֵשַׁע", "לְעֶשֶׂר", "לְאַחַת עֶשְׂרֵה", "לִשְׁתֵּים עֶשְׂרֵה"
]
MINUTE_PREFIX = [
    "", "וְדַקָּה אַחַת", "וּשְׁתֵּי דַקּוֹת", "וְשָׁלוֹשׁ דַקּוֹת",
    "וְאַרְבַּע דַקּוֹת", "וְחָמֵשׁ דַקּוֹת", "וְשֵׁשׁ דַקּוֹת", "וְשֶׁבַע דַקּוֹת",
    "וּשְׁמוֹנֶה דַקּוֹת", "וְתֵשַׁע דַקּוֹת", "וְעֶשֶׂר דַקּוֹת",
    "וְאַחַת עֶשְׂרֵה דַּקּוֹת", "וּשְׁתֵּים עֶשְׂרֵה דַּקּוֹת",
    "וּשְׁלוֹשׁ עֶשְׂרֵה דַּקּוֹת", "וְאַרְבַּע עֶשְׂרֵה דַּקּוֹת",
    "וָרֶבַע", "וְשֵׁשׁ עֶשְׂרֵה דַּקּוֹת", "וּשְׁבַע עֶשְׂרֵה דַּקּוֹת",
    "וּשְׁמוֹנֶה עֶשְׂרֵה דַּקּוֹת", "וּתְשַׁע עֶשְׂרֵה דַּקּוֹת",
    "וְעֶשְׂרִים דַקּוֹת", "וְעֶשְׂרִים וְאַחַת", "וְעֶשְׂרִים וּשְׁתַּיִם",
    "וְעֶשְׂרִים וְשָׁלוֹשׁ", "וְעֶשְׂרִים וְאַרְבַּע", "וְעֶשְׂרִים וְחָמֵשׁ",
    "וְעֶשְׂרִים וְשֵׁשׁ", "וְעֶשְׂרִים וְשֶׁבַע", "וְעֶשְׂרִים וּשְׁמוֹנֶה",
    "וְעֶשְׂרִים וְתֵשַׁע", "וָחֵצִי", "וּשְׁלוֹשִׁים וְאַחַת",
    "וּשְׁלוֹשִׁים וּשְׁתַּיִם", "וּשְׁלוֹשִׁים וְשָׁלוֹשׁ", "וּשְׁלוֹשִׁים וְאַרְבַּע",
    "וּשְׁלוֹשִׁים וְחָמֵשׁ", "וּשְׁלוֹשִׁים וְשֵׁשׁ", "וּשְׁלוֹשִׁים וְשֶׁבַע",
    "וּשְׁלוֹשִׁים וּשְׁמוֹנֶה", "וּשְׁלוֹשִׁים וְתֵשַׁע", "",
    "וְאַרְבָּעִים וְאַחַת", "וְאַרְבָּעִים וּשְׁתַּיִם", "וְאַרְבָּעִים וְשָׁלוֹשׁ",
    "וְאַרְבָּעִים וְאַרְבַּע", "", "וְאַרְבָּעִים וְשֵׁשׁ", "וְאַרְבָּעִים וְשֶׁבַע",
    "וְאַרְבָּעִים וּשְׁמוֹנֶה", "וְאַרְבָּעִים וְתֵשַׁע", "",
    "וַחֲמִשִּׁים וְאַחַת", "וַחֲמִשִּׁים וּשְׁתַּיִם", "וַחֲמִשִּׁים וְשָׁלוֹשׁ",
    "וַחֲמִשִּׁים וְאַרְבַּע", "", "וַחֲמִשִּׁים וְשֵׁשׁ", "וַחֲמִשִּׁים וְשֶׁבַע",
    "וַחֲמִשִּׁים וּשְׁמוֹנֶה", "וַחֲמִשִּׁים וְתֵשַׁע",
]
SUBTRACT_AMOUNT = {40: "עֶשְׂרִים", 45: "רֶבַע", 50: "עֲשָׂרָה", 55: "חֲמִשָּׁה"}

def get_time_period(h):
    if 6 <= h < 12:  return "בַּבֹּקֶר"
    if 12 <= h < 16: return "בַּצָּהֳרַיִם"
    if 16 <= h < 18: return "אַחַר הַצָּהֳרַיִם"
    if 18 <= h < 21: return "בָּעֶרֶב"
    if 21 <= h < 24: return "בַּלַּיְלָה"
    if 0 <= h < 3:   return "בַּלַּיְלָה"
    return "לִפְנוֹת בֹּקֶר"

def get_time_lines(h24, m):
    m = (m // 5) * 5
    h12 = h24 % 12 or 12
    period = get_time_period(h24)
    if m in SUBTRACT_AMOUNT:
        return [SUBTRACT_AMOUNT[m] + " " + HOURS_LAMED[h12 % 12], period]
    elif m == 0:
        return [HOURS[h12 - 1], period]
    else:
        mp = MINUTE_PREFIX[m]
        hp = HOURS[h12 - 1]
        if len(hp + mp) > 25:
            return [hp, mp, period]
        return [hp + " " + mp, period]

# ── Weather ───────────────────────────────────────────
WMO_CODES = {
    0: ("שָׁמְשִׁי", "sun"), 1: ("בָּהִיר", "sun"), 2: ("מְעֻנָּן חֶלְקִי", "sun_cloud"),
    3: ("מְעֻנָּן", "cloud"), 45: ("עֲרָפֶל", "cloud"), 48: ("עֲרָפֶל", "cloud"),
    51: ("טִפְטוּף", "cloud_rain"), 53: ("טִפְטוּף", "cloud_rain"), 55: ("טִפְטוּף", "cloud_rain"),
    61: ("גֶּשֶׁם קַל", "cloud_rain"), 63: ("גֶּשֶׁם", "cloud_rain"), 65: ("גֶּשֶׁם כָּבֵד", "cloud_rain"),
    71: ("שֶׁלֶג", "cloud_snow"), 73: ("שֶׁלֶג", "cloud_snow"), 75: ("שֶׁלֶג", "cloud_snow"),
    80: ("מִקְלָחוֹת", "cloud_rain"), 81: ("מִקְלָחוֹת", "cloud_rain"), 82: ("מִקְלָחוֹת", "cloud_rain"),
    95: ("סוּפַת רְעָמִים", "thunder"), 96: ("סוּפַת רְעָמִים", "thunder"), 99: ("סוּפַת רְעָמִים", "thunder"),
}

_weather_cache = {"data": None, "time": None, "last_fail": None}

def get_weather():
    global _weather_cache
    now = datetime.datetime.utcnow()
    if _weather_cache.get("time") and (now - _weather_cache["time"]).total_seconds() < 1800:
        return _weather_cache.get("data")
    if _weather_cache.get("last_fail") and (now - _weather_cache["last_fail"]).total_seconds() < 600:
        return _weather_cache.get("data")
    try:
        url = "https://wttr.in/Tel+Aviv?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            cc = data["current_condition"][0]
            temp = round(float(cc["temp_C"]))
            code = int(cc["weatherCode"])
            if code == 113: icon = "sun"
            elif code == 116: icon = "sun_cloud"
            elif code in [119, 122]: icon = "cloud"
            elif code in [176, 293, 296, 299, 302, 305, 308, 353, 356, 359]: icon = "cloud_rain"
            elif code in [179, 182, 185, 227, 230, 323, 326, 329, 332, 335, 338, 368, 371, 374, 377]: icon = "cloud_snow"
            elif code in [200, 386, 389, 392, 395]: icon = "thunder"
            else: icon = "cloud"
            desc_map = {"sun": "שָׁמְשִׁי", "sun_cloud": "מְעֻנָּן חֶלְקִי",
                        "cloud": "מְעֻנָּן", "cloud_rain": "גֶּשֶׁם",
                        "cloud_snow": "שֶׁלֶג", "thunder": "סוּפָה"}
            result = {"temp": temp, "icon_key": icon, "desc": desc_map.get(icon, "מְעֻנָּן")}
            _weather_cache = {"data": result, "time": now, "last_fail": None}
            print(f"Weather OK: {temp}C {icon}", flush=True)
            return result
    except Exception as e:
        print(f"Weather error: {e}", file=sys.stderr)
        _weather_cache["last_fail"] = datetime.datetime.utcnow()
        return _weather_cache.get("data")

# ── Draw weather icons ────────────────────────────────
def draw_sun(draw, cx, cy, r=22):
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=0, width=3)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x1 = cx + (r+5) * math.cos(rad)
        y1 = cy + (r+5) * math.sin(rad)
        x2 = cx + (r+12) * math.cos(rad)
        y2 = cy + (r+12) * math.sin(rad)
        draw.line([x1, y1, x2, y2], fill=0, width=2)

def draw_cloud_shape(draw, cx, cy, w=60, h=28):
    # Flat bottom, bumpy top cloud
    # Step 1: fill all white
    draw.rectangle([cx-w//2, cy-h//2, cx+w//2, cy+h//2+4], fill=255)
    # Top bumps (white filled circles)
    bumps = [
        (cx - w//3, cy - h//4, h//2),     # left bump
        (cx,        cy - h//2, h//2 + 3), # center bump (tallest)
        (cx + w//3, cy - h//4, h//2 - 2), # right bump
    ]
    for bx, by, br in bumps:
        draw.ellipse([bx-br, by-br, bx+br, by+br], fill=255)
    # Step 2: draw outlines
    for bx, by, br in bumps:
        draw.ellipse([bx-br, by-br, bx+br, by+br], outline=0, width=2)
    # Flat bottom line
    draw.line([cx-w//2, cy+h//2+2, cx+w//2, cy+h//2+2], fill=0, width=2)
    # Left and right sides
    draw.line([cx-w//2, cy-2, cx-w//2, cy+h//2+2], fill=0, width=2)
    draw.line([cx+w//2, cy-2, cx+w//2, cy+h//2+2], fill=0, width=2)
    # Cover internal bump lines with white
    draw.rectangle([cx-w//2+3, cy-h//4, cx+w//2-3, cy+h//2], fill=255)

def draw_sun_cloud(draw, cx, cy):
    draw_sun(draw, cx-18, cy-12, r=16)
    draw_cloud_shape(draw, cx+12, cy+8, w=50, h=24)

def draw_cloud(draw, cx, cy):
    draw_cloud_shape(draw, cx, cy, w=60, h=28)

def draw_cloud_rain(draw, cx, cy):
    draw_cloud_shape(draw, cx, cy-8, w=58, h=26)
    for i, offset in enumerate([-18, -5, 8, 21]):
        draw.line([cx+offset, cy+16, cx+offset-5, cy+30], fill=0, width=2)

def draw_cloud_snow(draw, cx, cy):
    draw_cloud_shape(draw, cx, cy-8, w=58, h=26)
    for offset in [-18, -5, 8, 21]:
        x, y = cx+offset, cy+24
        draw.ellipse([x-3, y-3, x+3, y+3], fill=0)

def draw_thunder(draw, cx, cy):
    draw_cloud_shape(draw, cx, cy-8, w=58, h=26)
    pts = [(cx+5, cy+12), (cx-4, cy+26), (cx+3, cy+26), (cx-7, cy+42)]
    draw.line(pts, fill=0, width=3)

ICON_FUNCS = {
    "sun": draw_sun, "sun_cloud": draw_sun_cloud, "cloud": draw_cloud,
    "cloud_rain": draw_cloud_rain, "cloud_snow": draw_cloud_snow, "thunder": draw_thunder,
}

# ── Draw analog clock ────────────────────────────────
def draw_analog_clock(draw, cx, cy, r, h24, m):
    # Face
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=0, width=3)
    
    # Hour marks
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        if i % 3 == 0:
            x1 = cx + (r-4) * math.cos(angle)
            y1 = cy + (r-4) * math.sin(angle)
            x2 = cx + (r-12) * math.cos(angle)
            y2 = cy + (r-12) * math.sin(angle)
            draw.line([x1, y1, x2, y2], fill=0, width=3)
        else:
            x1 = cx + (r-4) * math.cos(angle)
            y1 = cy + (r-4) * math.sin(angle)
            x2 = cx + (r-9) * math.cos(angle)
            y2 = cy + (r-9) * math.sin(angle)
            draw.line([x1, y1, x2, y2], fill=0, width=2)

    # Hour hand
    h12 = h24 % 12
    hour_angle = math.radians((h12 + m/60) * 30 - 90)
    hx = cx + (r * 0.55) * math.cos(hour_angle)
    hy = cy + (r * 0.55) * math.sin(hour_angle)
    draw.line([cx, cy, hx, hy], fill=0, width=4)

    # Minute hand
    min_angle = math.radians(m * 6 - 90)
    mx2 = cx + (r * 0.75) * math.cos(min_angle)
    my2 = cy + (r * 0.75) * math.sin(min_angle)
    draw.line([cx, cy, mx2, my2], fill=0, width=2)

    # Center dot
    draw.ellipse([cx-4, cy-4, cx+4, cy+4], fill=0)

# ── Font ──────────────────────────────────────────────
FONT_AVAILABLE = False
BUNDLED_FONT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "NotoSansHebrew-Bold.ttf")

def download_font():
    global FONT_AVAILABLE
    if os.path.exists(BUNDLED_FONT) and os.path.getsize(BUNDLED_FONT) > 10000:
        print(f"Using bundled font: {BUNDLED_FONT}", flush=True)
        FONT_AVAILABLE = True
    else:
        print(f"Font not found at {BUNDLED_FONT}", flush=True)

def get_font(size):
    if FONT_AVAILABLE and os.path.exists(BUNDLED_FONT):
        try: return ImageFont.truetype(BUNDLED_FONT, size)
        except: pass
    for p in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

def get_israel_time():
    utc = datetime.datetime.utcnow()
    return utc + datetime.timedelta(hours=3 if 3 <= utc.month <= 10 else 2)

# ── Main image ────────────────────────────────────────
def generate_night_image():
    W, H = 800, 480
    img = Image.new("L", (W, H), color=0)  # Black background
    draw = ImageDraw.Draw(img)

    # Stars
    import random
    random.seed(42)
    for _ in range(80):
        x = random.randint(20, W-20)
        y = random.randint(20, H//2)
        size = random.choice([1, 1, 1, 2, 2, 3])
        draw.ellipse([x-size, y-size, x+size, y+size], fill=255)

    # Moon (crescent) - top right
    mx, my, mr = 650, 100, 60
    draw.ellipse([mx-mr, my-mr, mx+mr, my+mr], fill=255)
    draw.ellipse([mx-mr+18, my-mr-10, mx+mr+18, my-mr-10+mr*2], fill=0)

    font_large  = get_font(106)
    font_medium = get_font(60)
    font_small  = get_font(32)

    # Main text - white on black
    draw.text((W//2, H//2 - 40), "לְכוּ לִישׁוֹן!", font=font_large, fill=255, anchor="mm")
    draw.text((W//2, H//2 + 55), "לַיְלָה טוֹב", font=font_medium, fill=200, anchor="mm")

    # Small stars around text
    for sx, sy in [(150, 280), (620, 320), (100, 380), (680, 260)]:
        draw.ellipse([sx-3, sy-3, sx+3, sy+3], fill=180)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()

def generate_quiet_image():
    W, H = 800, 480
    img = Image.new("L", (W, H), color=255)
    draw = ImageDraw.Draw(img)
    PAD1, PAD2 = 8, 16
    draw.rectangle([PAD1, PAD1, W-PAD1, H-PAD1], outline=0, width=3)
    draw.rectangle([PAD2, PAD2, W-PAD2, H-PAD2], outline=0, width=1)
    font_large = get_font(72)
    font_medium = get_font(55)
    font_small = get_font(38)
    draw.text((W//2, H//2 - 50), "לֹא לְהָעִיר אַף אֶחָד!", font=font_large, fill=0, anchor="mm")
    # Draw Zzz instead of emoji
    draw.text((W//2 - 60, H//2 + 30), "z", font=font_large, fill=0, anchor="mm")
    draw.text((W//2, H//2 + 20), "z", font=font_medium, fill=0, anchor="mm")
    draw.text((W//2 + 50, H//2 + 10), "z", font=font_small, fill=0, anchor="mm")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()

def generate_clock_image():
    now = get_israel_time()
    h24, m = now.hour, now.minute

    # Night mode: 21:00 - 06:00
    if h24 >= 21 or h24 < 6:
        return generate_night_image()
    # Quiet mode: 06:00 - 07:30
    if h24 == 6 or (h24 == 7 and m < 30):
        return generate_quiet_image()

    W, H = 800, 480
    img = Image.new("L", (W, H), color=255)
    draw = ImageDraw.Draw(img)

    # Double border
    PAD1, PAD2 = 8, 16
    draw.rectangle([PAD1, PAD1, W-PAD1, H-PAD1], outline=0, width=3)
    draw.rectangle([PAD2, PAD2, W-PAD2, H-PAD2], outline=0, width=1)

    # Time text
    period_words = {"בַּבֹּקֶר","בַּצָּהֳרַיִם","בָּעֶרֶב","בַּלַּיְלָה","לִפְנוֹת בֹּקֶר"}
    lines = get_time_lines(h24, m)
    time_lines = [l for l in lines if l not in period_words]
    period_line = next((l for l in lines if l in period_words), "")

    font_large  = get_font(106)
    font_medium = get_font(60)
    font_small  = get_font(36)

    # ── Layout B: small clock top-center, big text below ──
    # Analog clock top center (small)
    clock_cx = W // 2
    clock_cy = PAD2 + 20 + 45  # small clock at top
    clock_r  = 45
    draw_analog_clock(draw, clock_cx, clock_cy, clock_r, h24, m)

    # Time text below clock — 20% bigger fonts
    text_start_y = clock_cy + clock_r + 20
    text_area_h = H - 110 - text_start_y

    n = len(time_lines)
    line_h = 108
    total_h = n * line_h
    ty = text_start_y + (text_area_h - total_h) // 2 + 50

    for i, line in enumerate(time_lines):
        draw.text((W//2, ty + i*line_h), line, font=font_large, fill=0, anchor="mm")
    if period_line:
        draw.text((W//2, ty + n*line_h + 8), period_line, font=font_medium, fill=0, anchor="mm")

    # Bottom bar
    sep_y = H - 105
    draw.line([(PAD2+8, sep_y), (W-PAD2-8, sep_y)], fill=0, width=1)
    bar_cy = H - 52

    bar_left = PAD2 + 8
    bar_right = W - PAD2 - 8
    bar_width = bar_right - bar_left
    div_x = bar_left + bar_width // 3
    div_x2 = bar_left + 2 * bar_width // 3

    draw.line([(div_x, H - 92), (div_x, H - 15)], fill=0, width=1)
    draw.line([(div_x2, H - 92), (div_x2, H - 15)], fill=0, width=1)

    MONTHS_HE = [
        "בְּיָנוּאָר", "בְּפֶבְּרוּאָר", "בְּמָרְץ", "בְּאַפְּרִיל",
        "בְּמַאי", "בְּיוּנִי", "בְּיוּלִי", "בְּאוֹגוּסְט",
        "בְּסֶפְּטֶמְבֶּר", "בְּאוֹקְטוֹבֶּר", "בְּנוֹבֶמְבֶּר", "בְּדֶצֶמְבֶּר"
    ]
    DAYS_HE = [
        "יוֹם שֵׁנִי", "יוֹם שְׁלִישִׁי", "יוֹם רְבִיעִי",
        "יוֹם חֲמִישִׁי", "יוֹם שִׁישִּׁי", "שַׁבָּת", "יוֹם רִאשׁוֹן"
    ]
    day_name = DAYS_HE[now.weekday()]
    date_str = f"{now.day} {MONTHS_HE[now.month - 1]}"
    mid_x = (div_x + div_x2) // 2
    draw.text((mid_x, bar_cy - 14), day_name, font=font_small, fill=0, anchor="mm")
    draw.text((mid_x, bar_cy + 14), date_str, font=font_small, fill=0, anchor="mm")

    # Left section: empty (was clock, now clock moved to top)
    draw.text(((bar_left + div_x) // 2, bar_cy), "—", font=font_small, fill=180, anchor="mm")

    # RIGHT: weather
    weather = get_weather()
    if weather:
        temp = weather["temp"]
        desc = weather.get("desc", "לא ידוע")
        icon_key = weather.get("icon_key", "cloud")
        font_num = get_font(40)
        right_cx = (div_x2 + W - PAD2 - 8) // 2
        draw.text((right_cx, bar_cy - 14), f"{temp}°", font=font_num, fill=0, anchor="mm")
        draw.text((right_cx, bar_cy + 16), desc, font=font_small, fill=0, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()

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

    def log_message(self, fmt, *args): pass

if __name__ == "__main__":
    print(f"Starting Hebrew Clock + Weather on port {PORT}", flush=True)
    download_font()
    HTTPServer(("0.0.0.0", PORT), ClockHandler).serve_forever()
