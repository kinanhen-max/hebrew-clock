#!/usr/bin/env python3
"""
Hebrew Word Clock Server - Cloud version
Serves a 800x480 PNG image of the current time in Hebrew words.
Deploy on Render.com (free tier).
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image, ImageDraw, ImageFont
import datetime
import io
import os

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

def find_font(size):
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoSerifHebrew-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansHebrew-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "fonts/NotoSerifHebrew-Bold.ttf",
        "NotoSerifHebrew-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
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
                print(f"Error: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    print(f"Starting Hebrew Clock Server on port {PORT}")
    HTTPServer(("0.0.0.0", PORT), ClockHandler).serve_forever()
