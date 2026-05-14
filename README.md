# Hebrew Clock Server

Serves a 800x480 PNG image of the current time in Hebrew words for use with SenseCraft e-ink displays.

## Deploy to Render.com (Free)

1. Create a GitHub account at github.com
2. Create a new public repo called `hebrew-clock`
3. Upload these three files to the repo:
   - `hebrew_clock_server.py`
   - `requirements.txt`
   - `README.md`
4. Go to render.com and sign up
5. Click "New +" → "Web Service"
6. Connect your GitHub account and select the `hebrew-clock` repo
7. Settings:
   - Build Command: `pip install -r requirements.txt && apt-get update && apt-get install -y fonts-noto-hebrew`
   - Start Command: `python hebrew_clock_server.py`
   - Plan: Free
8. Click "Create Web Service"
9. Wait for it to deploy (~3 min)
10. Copy the URL Render gives you (something like `https://hebrew-clock-xxxx.onrender.com`)
11. In SenseCraft, add a page from URL: `https://hebrew-clock-xxxx.onrender.com/clock.png`

## Local Testing

```
pip install -r requirements.txt
python hebrew_clock_server.py
```

Then visit http://localhost:8765/clock.png
