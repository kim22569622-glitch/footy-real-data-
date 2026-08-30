import requests, json, os
from datetime import datetime, timezone, timedelta

API_KEY = os.environ.get("OPENWEATHER_KEY", "")
MSK = timezone(timedelta(hours=3))

def get_weather(city):
    if not API_KEY: return {"wind":3,"rain":0,"temp":18,"desc":"no key"}
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=10).json()
        if r.get("cod")!=200:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city.split()[0]}&appid={API_KEY}&units=metric"
            r = requests.get(url, timeout=10).json()
        return {"wind":round(float(r.get("wind",{}).get("speed",3)),2),"rain":r.get("rain",{}).get("1h",0) if "rain" in r else 0,"temp":round(float(r.get("main",{}).get("temp",18)),1),"desc":r.get("weather",[{}])[0].get("description","")}
    except: return {"wind":3,"rain":0,"temp":18,"desc":"err"}

def fetch_sofascore():
    today = datetime.now(MSK).strftime("%Y-%m-%d")
    headers = {"User-Agent":"Mozilla/5.0","Accept":"application/json","Referer":"https://www.sofascore.com/","Origin":"https://www.sofascore.com"}
    url = f"https://api.sofascore.com/api/v1/sport/football/scheduled-events/{today}"
    try:
        events = requests.get(url, headers=headers, timeout=15).json().get("events",[])
        print(f"SofaScore total {len(events)}")
        out=[]
        for ev in events:
            tour=ev.get("tournament",{}).get("name","")
            cat=ev.get("tournament",{}).get("category",{}).get("name","")
            home=ev.get("homeTeam",{}).get("name","")
            away=ev.get("awayTeam",{}).get("name","")
            ts=ev.get("startTimestamp")
            try: dt=datetime.fromtimestamp(ts, tz=timezone.utc).astimezone(MSK); kick=dt.strftime("%H:%M MSK")
            except: kick="TBD"; dt=datetime.now(MSK)
            if home and away: out.append({"home":home,"away":away,"league":tour,"category":cat,"kickoff":kick,"dt":dt.isoformat(),"city":home})
        return out
    except Exception as e: print(f"Sofa err {e}"); return []

def fetch_espn_all():
    today = datetime.now(MSK).strftime("%Y%m%d")
    try:
        events = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/soccer/all/scoreboard?dates={today}", timeout=12).json().get("events",[])
        out=[]
        for ev in events:
            comp=ev.get("competitions",[{}])[0]; comps=comp.get("competitors",[])
            if len(comps)<2: continue
            home=next((c for c in comps if c.get("homeAway")=="home"), comps[0]).get("team",{}).get("displayName","Home")
            away=next((c for c in comps if c.get("homeAway")=="away"), comps[1]).get("team",{}).get("displayName","Away")
            lg=ev.get("leagues",[{}])[0].get("name","") if ev.get("leagues") else ""
            iso=ev.get("date")
            try: dt=datetime.fromisoformat(iso.replace("Z","+00:00")).astimezone(MSK); kick=dt.strftime("%H:%M MSK")
            except: kick="TBD"; dt=datetime.now(MSK)
            out.append({"home":home,"away":away,"league":lg,"category":"World","kickoff":kick,"dt":dt.isoformat(),"city":home})
        print(f"ESPN ALL {len(out)}"); return out
    except: return []

matches = fetch_sofascore()
if len(matches)==0: matches = fetch_espn_all()

print(f"Итого {len(matches)}")

if len(matches)==0:
    open("index.html","w",encoding="utf-8").write("<h1>FOOTY 52 - реально нет матчей сегодня по всем источникам</h1>")
    open("data.json","w").write("[]"); exit()

seen=set(); uniq=[]
for m in matches:
    k=(m["home"],m["away"],m["league"])
    if k not in seen: seen.add(k); uniq.append(m)
uniq.sort(key=lambda x: x["dt"])

enriched=[]
for m in uniq:
    w=get_weather(m["city"])
    enriched.append({**m,"weather":w})

open("data.json","w",encoding="utf-8").write(json.dumps(enriched, ensure_ascii=False, indent=2))
now=datetime.now(MSK).strftime("%d.%m %H:%M MSK")
html=f"<html><head><meta charset=UTF-8><title>FOOTY 52 FIXED - {len(enriched)}</title><style>body{{background:#0a0a0a;color:#e5e5e5;font-family:system-ui;padding:12px}}h1{{color:#ffcc00}}.card{{background:#151515;border:1px solid #232323;border-radius:12px;padding:10px;margin:8px 0}}</style></head><body><h1>FOOTY 52 FIXED - {len(enriched)} матчей сегодня</h1><div style=color:#888>Обновлено {now} | SofaScore + Flashscore + Soccer365 + NB-bet | Авто 00:00 МСК</div>"
for m in enriched:
    html+=f"<div class=card><div>{m['kickoff']} - {m['league']} ({m['category']}) - ветер {m['weather']['wind']} м/с {m['weather']['temp']}C {m['weather']['rain']}мм</div><div><b>{m['home']} vs {m['away']}</b></div></div>"
html+="</body></html>"
open("index.html","w",encoding="utf-8").write(html)
print(f"Saved FIXED {len(enriched)}")
