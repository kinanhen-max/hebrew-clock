#!/usr/bin/env python3
"""
Hebrew Word Clock Server - Cloud version
Serves a 800x480 PNG image of the current time in Hebrew words.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image, ImageDraw, ImageFont
import datetime
import io
import os
import urllib.request
import sys

PORT = int(os.environ.get("PORT", 8765))

HOURS = [
    "אחת", "שתיים", "שלוש", "ארבע", "חמש", "שש",
    "שבע", "שמונה", "תשע", "עשר", "אחת עשרה", "שתים עשרה"
]

HOURS_LAMED = [
    "לאחת", "לשתיים", "לשלוש", "לארבע", "לחמש", "לשש",
    "לשבע", "לשמונה", "לתשע", "לעשר", "לאחת עשרה", "לשתים עשרה"
]

MINUTE_PREFIX = {
    0: "", 5: "וחמש דקות", 10: "ועשר דקות",
    15: "ורבע", 20: "ועשרים", 25: "ועשרים וחמש",
    30: "וחצי", 35: "ושלושים וחמש",
}

SUBTRACT_MINUTES = {
    40: "עשרים", 45: "רבע", 50: "עשרה", 55: "חמישה",
}

def get_time_period(hour):
    if 6 <= hour < 12:  return "בבוקר"
    if 12 <= hour < 18: return "בצהריים"
    if 18 <= hour < 24: return "בערב"
    return "בלילה"

def round_to_5(minute):
    return (minute // 5) * 5

def get_time_lines(hour24, minute):
    minute = round_to_5(minute)
    hour12 = hour24 % 12 or 12
    period = get_time_period(hour24)

    if minute in SUBTRACT_MINUTES:
        next_hour = (hour12 % 12)
        prefix = SUBTRACT_MINUTES[minute]
        return [prefix + " " + HOURS_LAMED[next_hour], period]
    elif minute == 0:
        return [HOURS[hour12 - 1], period]
    else:
        min_part = MINUTE_PREFIX.get(minute, "")
        return [HOURS[hour12 - 1] + " " + min_part, period]

FONT_DIR = "/tmp"
FONT_FILE = os.path.join(FONT_DIR, "NotoSansHebrew-Bold.ttf")

# Google Fonts CDN URLs for Noto Sans Hebrew Bold (these are stable)
FONT_URLS = [
    "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansHebrew/NotoSansHebrew-Bold.ttf",
    "https://github.com/notofonts/hebrew/raw/main/fonts/NotoSansHebrew/hinted/ttf/NotoSansHebrew-Bold.ttf",
    "https://fonts.gstatic.com/s/notosanshebrew/v46/of0pUkAVDdv1ti_aB8GNvD7AzgL3lHGZpL_X.ttf",
]

def download_font():
    """Download Hebrew font on first run."""
    if os.path.exists(FONT_FILE) and os.path.getsize(FONT_FILE) > 10000:
        print(f"Font already exists at {FONT_FILE}")
        return True
    
    for url in FONT_URLS:
        try:
            print(f"Trying to download font from: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()
                if len(data) > 10000:  # Sanity check - real font is at least 10KB
                    with open(FONT_FILE, 'wb') as f:
                        f.write(data)
                    print(f"Font downloaded successfully ({len(data)} bytes)")
                    return True
                else:
                    print(f"Downloaded file too small: {len(data)} bytes")
        except Exception as e:
            print(f"Failed: {e}")
            continue
    
    print("WARNING: Could not download Hebrew font!")
    return False

FONT_AVAILABLE = False

def find_font(size):
    global FONT_AVAILABLE
    if FONT_AVAILABLE and os.path.exists(FONT_FILE):
        try:
            return ImageFont.truetype(FONT_FILE, size)
        except Exception as e:
            print(f"Font load error: {e}")
    
    # Fallbacks
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    ]:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    return ImageFont.load_default()

def get_israel_time():
    utc_now = datetime.datetime.utcnow()
    is_dst = 3 <= utc_now.month <= 10
    offset_hours = 3 if is_dst else 2
    return utc_now + datetime.timedelta(hours=offset_hours)

def generate_clock_image():
    now = get_israel_time()
    hour24, minute = now.hour, now.minute

    W, H = 800, 480
    img = Image.new("L", (W, H), color=255)
    draw = ImageDraw.Draw(img)

    lines = get_time_lines(hour24, minute)
    font_large = find_font(95)
    font_small = find_font(50)

    line_height = 130
    total_h = len(lines) * line_height
    start_y = (H - total_h) // 2 + 50

    for i, line in enumerate(lines):
        is_period = line in ["בבוקר", "בצהריים", "בערב", "בלילה"]
        font = font_small if is_period else font_large
        y = start_y + i * line_height
        draw.text((W // 2, y), line, font=font, fill=0, anchor="mm")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()

class ClockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/clock.png", "/clock", "/"):
            try:
                img_bytes = generate_clock_image()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(img_bytes)))
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(img_bytes)
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

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    print(f"Starting Hebrew Clock Server on port {PORT}", flush=True)
    FONT_AVAILABLE = download_font()
    print(f"Font available: {FONT_AVAILABLE}", flush=True)
    HTTPServer(("0.0.0.0", PORT), ClockHandler).serve_forever()
