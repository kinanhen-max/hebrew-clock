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
    if 12 <= h < 18: return "בַּצָּהֳרַיִם"
    if 18 <= h < 24: return "בָּעֶרֶב"
    if 0 <= h < 4:   return "בַּלַּיְלָה"
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
    0: ("שמשי", "sun"), 1: ("בהיר", "sun"), 2: ("מעונן חלקי", "sun_cloud"),
    3: ("מעונן", "cloud"), 45: ("ערפל", "cloud"), 48: ("ערפל", "cloud"),
    51: ("טפטוף", "cloud_rain"), 53: ("טפטוף", "cloud_rain"), 55: ("טפטוף", "cloud_rain"),
    61: ("גשם קל", "cloud_rain"), 63: ("גשם", "cloud_rain"), 65: ("גשם כבד", "cloud_rain"),
    71: ("שלג", "cloud_snow"), 73: ("שלג", "cloud_snow"), 75: ("שלג", "cloud_snow"),
    80: ("מקלחות", "cloud_rain"), 81: ("מקלחות", "cloud_rain"), 82: ("מקלחות", "cloud_rain"),
    95: ("סופת רעמים", "thunder"), 96: ("סופת רעמים", "thunder"), 99: ("סופת רעמים", "thunder"),
}

_weather_cache = {"data": None, "time": None}

def get_weather():
    global _weather_cache
    now = datetime.datetime.utcnow()
    if _weather_cache["time"] and (now - _weather_cache["time"]).seconds < 900:
        return _weather_cache["data"]
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=32.07&longitude=34.79&current_weather=true&timezone=Asia/Jerusalem&forecast_days=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            cw = data["current_weather"]
            result = {"temp": round(cw["temperature"]), "code": cw["weathercode"]}
            _weather_cache = {"data": result, "time": now}
            return result
    except Exception as e:
        print(f"Weather error: {e}", file=sys.stderr)
        return None

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
    # Draw filled white ellipses first, then outline on top
    draw.ellipse([cx-w//2, cy-h//2, cx+w//2, cy+h//2], fill=255, outline=0, width=2)
    draw.ellipse([cx-w//4, cy-h, cx+w//4, cy+4], fill=255, outline=0, width=2)
    draw.ellipse([cx+w//8, cy-h*2//3, cx+w//2+8, cy+h//4], fill=255, outline=0, width=2)
    # Cover internal lines with white fill
    draw.rectangle([cx-w//2+2, cy-h//2+2, cx+w//2-2, cy+h//2-2], fill=255, outline=None)
    draw.rectangle([cx-w//4+2, cy-h+2, cx+w//4-2, cy+4-2], fill=255, outline=None)
    draw.rectangle([cx+w//8+2, cy-h*2//3+2, cx+w//2+6, cy+h//4-2], fill=255, outline=None)

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
FONT_PATH = "/tmp/NotoSerifHebrew-Bold.ttf"
FONT_URLS = [
    "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansHebrew/NotoSansHebrew-Bold.ttf",
    "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSerifHebrew/NotoSerifHebrew-Bold.ttf",
]
FONT_AVAILABLE = False

def download_font():
    global FONT_AVAILABLE
    # Force re-download if file exists but might be wrong font
    if os.path.exists(FONT_PATH):
        os.remove(FONT_PATH)
    for url in FONT_URLS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                if len(data) > 10000:
                    with open(FONT_PATH, "wb") as f: f.write(data)
                    FONT_AVAILABLE = True
                    return
        except Exception as e:
            print(f"Font fail: {e}")

def get_font(size):
    if FONT_AVAILABLE and os.path.exists(FONT_PATH):
        try: return ImageFont.truetype(FONT_PATH, size)
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
def generate_clock_image():
    now = get_israel_time()
    h24, m = now.hour, now.minute

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

    font_large  = get_font(88)
    font_medium = get_font(50)
    font_small  = get_font(30)

    n = len(time_lines)
    line_h = 100
    total_h = n * line_h
    start_y = (H * 3 // 4 - total_h) // 2 + 30

    for i, line in enumerate(time_lines):
        draw.text((W//2, start_y + i*line_h), line, font=font_large, fill=0, anchor="mm")
    if period_line:
        draw.text((W//2, start_y + n*line_h + 10), period_line, font=font_medium, fill=0, anchor="mm")

    # Bottom separator
    sep_y = H - 105
    draw.line([(PAD2+8, sep_y), (W-PAD2-8, sep_y)], fill=0, width=1)

    # Bottom bar height = 105px, center = H - 52
    bar_cy = H - 52

    # LEFT: analog clock
    clock_cx = PAD2 + 50
    clock_r  = 38
    draw_analog_clock(draw, clock_cx, bar_cy, clock_r, h24, m)

    # Divider
    div_x = PAD2 + 105
    draw.line([(div_x, H - 95), (div_x, H - 12)], fill=180, width=1)

    # RIGHT: weather icon + temp + desc
    weather = get_weather()
    if weather:
        code = weather["code"]
        temp = weather["temp"]
        desc, icon_key = WMO_CODES.get(code, ("לא ידוע", "cloud"))

        # Weather icon on the right side
        icon_cx = W - PAD2 - 55
        icon_cy = bar_cy
        icon_func = ICON_FUNCS.get(icon_key, draw_cloud)
        icon_func(draw, icon_cx, icon_cy)

        # Temperature to the left of icon
        # Hebrew number words for temperature
        def temp_to_hebrew(t):
            tens = {2:"עשרים", 3:"שלושים", 4:"ארבעים"}
            ones = {1:"אחת", 2:"שתיים", 3:"שלוש", 4:"ארבע", 5:"חמש",
                    6:"שש", 7:"שבע", 8:"שמונה", 9:"תשע"}
            if t <= 0: return "קר"
            if t < 10: return ones.get(t, str(t))
            if t == 10: return "עשר"
            if t == 20: return "עשרים"
            if t == 30: return "שלושים"
            ten = (t // 10) * 10
            one = t % 10
            if one == 0: return tens.get(t//10, str(t))
            return tens.get(ten//10, "") + " ו" + ones.get(one, str(one))

        font_num = get_font(38)
        draw.text((W - PAD2 - 70, bar_cy - 18), f"{temp}", font=font_num, fill=0, anchor="rm")
        draw.text((W - PAD2 - 70, bar_cy + 14), desc, font=font_small, fill=0, anchor="rm")

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
