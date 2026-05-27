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
def draw_weather_icon(draw, cx, cy, icon_key, size=42):
    """Draw clean weather icons. cx,cy = center. size = radius/scale."""
    s = size

    def cloud(ox=0, oy=0, scale=1.0):
        """Draw a proper cloud using polygon — no overlap lines."""
        w, h = int(s*1.4*scale), int(s*0.7*scale)
        pts = []
        # Bottom flat part
        for a in range(180, 361, 8):
            pts.append((ox+cx + int(w/2 * math.cos(math.radians(a))),
                        oy+cy + int(h/2 * math.sin(math.radians(a)))))
        # Right bump
        rb = int(h*0.6*scale)
        for a in range(0, 181, 8):
            pts.append((ox+cx + int(w*0.25) + int(rb * math.cos(math.radians(a))),
                        oy+cy - int(h*0.2) + int(rb * math.sin(math.radians(a)))))
        # Center bump (tallest)
        cb = int(h*0.75*scale)
        for a in range(0, 181, 8):
            pts.append((ox+cx + int(cb * math.cos(math.radians(a))),
                        oy+cy - int(h*0.3) + int(cb * math.sin(math.radians(a)))))
        # Left bump
        lb = int(h*0.55*scale)
        for a in range(0, 181, 8):
            pts.append((ox+cx - int(w*0.25) + int(lb * math.cos(math.radians(a))),
                        oy+cy - int(h*0.1) + int(lb * math.sin(math.radians(a)))))
        draw.polygon(pts, fill=255, outline=0)

    if icon_key == "sun":
        # Circle + 8 rays
        r = s // 2
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=255, outline=0, width=3)
        for a in range(0, 360, 45):
            rad = math.radians(a)
            draw.line([cx+(r+4)*math.cos(rad), cy+(r+4)*math.sin(rad),
                       cx+(r+13)*math.cos(rad), cy+(r+13)*math.sin(rad)], fill=0, width=3)

    elif icon_key == "sun_cloud":
        # Small sun top-left, cloud bottom-right
        sr = s // 3
        scx, scy = cx - s//3, cy - s//4
        draw.ellipse([scx-sr, scy-sr, scx+sr, scy+sr], fill=255, outline=0, width=2)
        for a in range(0, 360, 60):
            rad = math.radians(a)
            draw.line([scx+(sr+3)*math.cos(rad), scy+(sr+3)*math.sin(rad),
                       scx+(sr+9)*math.cos(rad), scy+(sr+9)*math.sin(rad)], fill=0, width=2)
        cloud(s//5, s//5, 0.85)

    elif icon_key == "cloud":
        cloud()

    elif icon_key == "cloud_rain":
        cloud(0, -s//5, 0.9)
        for i, ox in enumerate([-s//3, -s//8, s//8, s//3]):
            draw.line([cx+ox, cy+s//4, cx+ox-4, cy+s//2+4], fill=0, width=2)

    elif icon_key == "cloud_snow":
        cloud(0, -s//5, 0.9)
        for ox in [-s//3, -s//8, s//8, s//3]:
            x, y = cx+ox, cy+s//3
            # Draw snowflake star
            for a in [0, 60, 120]:
                rad = math.radians(a)
                draw.line([x-6*math.cos(rad), y-6*math.sin(rad),
                           x+6*math.cos(rad), y+6*math.sin(rad)], fill=0, width=2)

    elif icon_key == "thunder":
        cloud(0, -s//4, 0.9)
        # Lightning bolt
        pts = [(cx+4, cy+s//6), (cx-6, cy+s//2),
               (cx+2, cy+s//2), (cx-8, cy+s)]
        draw.line(pts, fill=0, width=3)

ICON_FUNCS = {
    "sun": lambda d,x,y: draw_weather_icon(d,x,y,"sun"),
    "sun_cloud": lambda d,x,y: draw_weather_icon(d,x,y,"sun_cloud"),
    "cloud": lambda d,x,y: draw_weather_icon(d,x,y,"cloud"),
    "cloud_rain": lambda d,x,y: draw_weather_icon(d,x,y,"cloud_rain"),
    "cloud_snow": lambda d,x,y: draw_weather_icon(d,x,y,"cloud_snow"),
    "thunder": lambda d,x,y: draw_weather_icon(d,x,y,"thunder"),
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

    # Numbers: 12, 3, 6, 9
    num_font = get_font(max(12, r // 4))
    for num, angle_deg in [(12, -90), (3, 0), (6, 90), (9, 180)]:
        angle = math.radians(angle_deg)
        nx = cx + (r - 18) * math.cos(angle)
        ny = cy + (r - 18) * math.sin(angle)
        draw.text((nx, ny), str(num), font=num_font, fill=0, anchor="mm")

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
    import random, os
    W, H = 800, 480
    img = Image.new("L", (W, H), color=0)
    draw = ImageDraw.Draw(img)

    # Stars
    random.seed(42)
    for _ in range(60):
        x = random.randint(20, W-20)
        y = random.randint(20, H-20)
        size = random.choice([1, 1, 2, 2, 3])
        draw.ellipse([x-size, y-size, x+size, y+size], fill=255)

    # Moon (crescent) top left
    mx, my, mr = 100, 90, 55
    draw.ellipse([mx-mr, my-mr, mx+mr, my+mr], fill=255)
    draw.ellipse([mx-mr+16, my-mr-12, mx+mr+16, my-mr-12+mr*2], fill=0)

    # Sleeping image - right side, white lines on black
    sleeping_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sleeping.png")
    if os.path.exists(sleeping_path):
        try:
            sleeping = Image.open(sleeping_path).convert("L")
            mask = sleeping.point(lambda p: 255 if p < 128 else 0)
            white_lines = Image.new("L", sleeping.size, 255)
            black_bg = Image.new("L", sleeping.size, 0)
            result = Image.composite(white_lines, black_bg, mask)
            sw, sh = 380, 280
            result = result.resize((sw, sh), Image.LANCZOS)
            mask_r = mask.resize((sw, sh), Image.LANCZOS)
            img.paste(result, (W - sw - 20, (H - sh) // 2), mask=mask_r)
        except Exception as e:
            print(f"Sleeping image error: {e}")

    # Text on left side
    font_large  = get_font(72)
    font_medium = get_font(44)
    text_cx = (W - 380 - 40) // 2
    draw.text((text_cx, H//2 - 30), "זְמַן לִישׁוֹן", font=font_large, fill=255, anchor="mm")
    draw.text((text_cx, H//2 + 55), "לַיְלָה טוֹב", font=font_medium, fill=180, anchor="mm")

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
    real_m = m  # Keep real minutes for analog clock

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

    font_large  = get_font(100)
    font_medium = get_font(58)
    font_small  = get_font(34)

    # ── Layout B: small clock top-center, big text below ──
    # Analog clock top center (small)
    clock_cx = W // 2
    clock_cy = PAD2 + 75
    clock_r  = 68
    draw_analog_clock(draw, clock_cx, clock_cy, clock_r, h24, real_m)

    # Time text below clock — 20% bigger fonts
    text_start_y = clock_cy + clock_r + 15
    text_area_h = H - 110 - text_start_y

    n = len(time_lines)
    line_h = 95
    total_h = n * line_h
    ty = text_start_y + (text_area_h - total_h) // 2 + 10

    for i, line in enumerate(time_lines):
        # Auto-shrink font if text too wide
        f = font_large
        while True:
            bbox = draw.textbbox((0,0), line, font=f)
            if (bbox[2] - bbox[0]) < (W - 60):
                break
            current_size = f.size if hasattr(f, "size") else 100
            if current_size <= 40:
                break
            f = get_font(current_size - 6)
        draw.text((W//2, ty + i*line_h), line, font=f, fill=0, anchor="mm")

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
    # Date on LEFT section
    left_cx = (bar_left + div_x) // 2
    draw.text((left_cx, bar_cy - 14), day_name, font=font_small, fill=0, anchor="mm")
    draw.text((left_cx, bar_cy + 14), date_str, font=font_small, fill=0, anchor="mm")
    # Period (בערב/בבוקר) in MIDDLE section
    mid_x = (div_x + div_x2) // 2
    if period_line:
        draw.text((mid_x, bar_cy), period_line, font=font_small, fill=0, anchor="mm")

    # RIGHT: weather
    weather = get_weather()
    if weather:
        temp = weather["temp"]
        desc = weather.get("desc", "לא ידוע")
        icon_key = weather.get("icon_key", "cloud")
        font_num = get_font(40)
        # Right section boundaries
        right_start = div_x2
        right_end = W - PAD2 - 8
        right_cx = (right_start + right_end) // 2
        # Icon left side of right section
        icon_x = right_start + (right_end - right_start) // 4
        icon_y = bar_cy
        draw_weather_icon(draw, icon_x, icon_y, icon_key, size=34)
        # Temp + desc right side
        text_x = right_start + 3*(right_end - right_start) // 4
        draw.text((text_x, bar_cy - 14), f"{temp}°", font=font_num, fill=0, anchor="mm")
        draw.text((text_x, bar_cy + 16), desc, font=font_small, fill=0, anchor="mm")

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
