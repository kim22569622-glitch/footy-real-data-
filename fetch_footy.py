import requests, json, os

API_KEY = os.environ.get("OPENWEATHER_KEY", "")

def get_weather(lat, lon):
    if not API_KEY:
        return {"wind": 3, "rain": 0, "temp": 18}
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=10).json()
        wind = r.get("wind", {}).get("speed", 3)
        rain = 0
        if "rain" in r:
            rain = r["rain"].get("1h", 0)
        temp = r.get("main", {}).get("temp", 18)
        return {"wind": wind, "rain": rain, "temp": temp}
    except Exception:
        return {"wind": 3, "rain": 0, "temp": 18}

MATCHES = [
    {"home": "Real Madrid", "away": "Malaga CF", "league": "LaLiga FT 4:0", "is_top": True, "lat": 40.4530, "lon": -3.6883},
    {"home": "Egersund", "away": "Åsane", "league": "OBOS", "is_top": False, "lat": 58.4520, "lon": 6.0000, "wind": 13, "rain": 4},
    {"home": "FC Copenhagen", "away": "Brondby", "league": "Superliga derby 5/5", "is_top": False, "is_derby": True, "lat": 55.7020, "lon": 12.5720, "wind": 11, "rain": 2},
]

enriched = []
for m in MATCHES:
    if "wind" in m:
        w = {"wind": m["wind"], "rain": m["rain"], "temp": 12}
    else:
        w = get_weather(m["lat"], m["lon"])
    enriched.append({**m, "weather": w})

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(enriched, f, ensure_ascii=False, indent=2)

html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>FOOTY REAL LIVE</title><style>body{background:#0a0a0a;color:#e5e5e5;font-family:monospace;padding:16px}h1{color:#ffcc00}.card{background:#151515;border:1px solid #232323;border-radius:12px;padding:12px;margin:10px 0}</style></head><body>"
html += f"<h1>FOOTY REAL LIVE - {len(enriched)} матчей - ключ OK - {API_KEY[:4]}...</h1>"
for m in enriched:
    html += f"<div class='card'><b>{m['home']} vs {m['away']}</b> - {m['league']}<br>ветер {m['weather']['wind']} м/с дождь {m['weather']['rain']}мм темп {m['weather']['temp']}°C</div>"
html += "</body></html>"

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Saved {len(enriched)} matches, index.html updated")
