import requests, json, os
from datetime import datetime, timezone, timedelta

API_KEY = os.environ.get("OPENWEATHER_KEY", "")
MSK = timezone(timedelta(hours=3))

def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=10).json()
        if r.get("cod")!= 200:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city.split()[0]}&appid={API_KEY}&units=metric"
            r = requests.get(url, timeout=10).json()
        return {"wind": round(float(r.get("wind",{}).get("speed",3)),2), "rain": r.get("rain",{}).get("1h",0) if "rain" in r else 0, "temp": round(float(r.get("main",{}).get("temp",18)),1), "desc": r.get("weather",[{}])[0].get("description","")}
    except:
        return {"wind":3,"rain":0,"temp":18,"desc":"err"}

def fetch_today():
    today = datetime.now(MSK).strftime("%Y-%m-%d")
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{today}"
    events = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15).json().get("events",[])
    matched=[]
    for ev in events:
        tour=ev.get("tournament",{}).get("name","")
        cat=ev.get("tournament",{}).get("category",{}).get("name","")
        home=ev.get("homeTeam",{}).get("name","Home")
        away=ev.get("awayTeam",{}).get("name","Away")
        ts=ev.get("startTimestamp")
        try:
            dt=datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(MSK)
            kick=dt.strftime("%H:%M MSK")
        except:
            kick="TBD"; dt=datetime.now(MSK)
        matched.append({"home":home,"away":away,"league":tour,"category":cat,"kickoff":kick,"dt":dt.isoformat(),"city":home})
    return matched

matches=fetch_today()
if len(matches)==0:
    open("index.html","w",encoding="utf-8").write("<h1>FOOTY 52 - сегодня нет матчей</h1>")
    open("data.json","w").write("[]"); exit()

enriched=[]
for m in matches:
    w=get_weather(m["city"])
    enriched.append({**m,"weather":w})

open("data.json","w",encoding="utf-8").write(json.dumps(enriched, ensure_ascii=False, indent=2))
html=f"<h1>FOOTY 52 - {len(enriched)} матчей SofaScore</h1>"
for m in enriched:
    html+=f"<div>{m['kickoff']} {m['home']} vs {m['away']} - {m['league']} - ветер {m['weather']['wind']} м/с {m['weather']['temp']}C</div>"
open("index.html","w",encoding="utf-8").write(html)
