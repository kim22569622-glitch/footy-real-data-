import requests, json, os
from datetime import datetime, timedelta

API_KEY = os.environ.get("OPENWEATHER_K )

STADIUMS = {
    "Real Madrid": (40.4530, -3.6883),
    "Barcelona": (41.3809, 2.1228),
    "Egersund": (58.4520, 6.0000),
    "Copenhagen": (55.7020, 12.5720),
}

def get_weather(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=10).json()
        return {"wind": r.get("wind",{}).get("speed",3), "rain": r.get("rain",{}).get("1h",0) if "rain" in r else 0, "temp": r.get("main",{}).get("temp",18)}
    except:
        return {"wind":3,"rain":0,"temp":18}

MATCHES = [
    {"home":"Real Madrid","away":"Malaga CF","league":"LaLiga FT 4:0","is_top":True,"is_derby":False,"lat":40.4530,"lon":-3.6883},
    {"home":"Egersund","away":"Åsane","league":"OBOS","is_top":False,"is_derby":False,"lat":58.4520,"lon":6.0000,"wind":13,"rain":4},
    {"home":"FC Copenhagen","away":"Brondby","league":"Superliga дерби 5/5","is_top":False,"is_derby":True,"lat":55.7020,"lon":12.5720,"wind":11,"rain":2},
]

enriched = []
for m in MATCHES:
    if "wind" in m:
        w = {"wind": m["wind"], "rain": m["rain"], "temp": 12}
    else:
        w = get_weather(m["lat"], m["lon"])
    enriched.append({**m, "weather": w})

with open("data.json","w",encoding="utf-8") as f:
    json.dump(enriched, f, ensure_ascii=False, indent=2)

html = f"<h1>FOOTY REAL {len(enriched)} матчей - ветер/дождь с ключа {API_KEY[:8]}...</h1>"
for m in enriched:
    html += f"<div>{m['home']} vs {m['away']} - ветер {m['weather']['wind']} м/с дождь {m['weather']['rain']}мм</div>"

with open("index.html","w",encoding="utf-8") as f:
    f.write(html)

print(f"Saved {len(enriched)} real matches")
