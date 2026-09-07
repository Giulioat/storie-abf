#!/usr/bin/env python3
"""Costruisce la sezione "Reference" dell'Impaginatore Storie ABF.

Legge le catture giornaliere in Intelligence/market/abf-stories/data/*.json
(prodotte dal task schedulato abf-stories-daily-pull via Instagram Graph API),
raggruppa le storie in SEQUENZE (stesso giorno locale, gap <= 3h tra una storia
e la successiva), ordina per risposte totali e salva le prime 5 in
~/Documents/storie-abf-site/top/top-stories.json con i thumbnail ridotti.

Poi build-site.sh pusha tutto su GitHub Pages: il tool legge top/top-stories.json.
"""
import json, glob, os, shutil, subprocess, sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from PIL import Image

VAULT = os.path.expanduser("~/Second Brain")
DATA = os.path.join(VAULT, "Intelligence/market/abf-stories/data")
MEDIA = os.path.join(VAULT, "Intelligence/market/abf-stories/media")
SITE = os.path.expanduser("~/Documents/storie-abf-site")
OUT = os.path.join(SITE, "top")
ROME = ZoneInfo("Europe/Rome")
TOP_N = 5
GAP_H = 3

def load_stories():
    """Una voce per story id: tiene la cattura con più risposte (le insights crescono finché la storia è attiva)."""
    best = {}
    for f in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        day = os.path.basename(f)[:-5]
        try:
            d = json.load(open(f))
        except Exception as e:
            print("skip", f, e, file=sys.stderr); continue
        for s in d.get("stories", []):
            sid = s.get("id")
            if not sid or not s.get("timestamp"): continue
            ins = s.get("insights") or {}
            rec = {**s, "reach": s.get("reach", ins.get("reach")), "replies": s.get("replies", ins.get("replies")), "navigation": s.get("navigation", ins.get("navigation")), "capture_day": day}
            cur = best.get(sid)
            if cur is None or (rec.get("replies") or 0) > (cur.get("replies") or 0) or (
                (rec.get("replies") or 0) == (cur.get("replies") or 0) and (rec.get("reach") or 0) > (cur.get("reach") or 0)):
                best[sid] = rec
    out = []
    for s in best.values():
        ts = datetime.strptime(s["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(ROME)
        s["local"] = ts
        out.append(s)
    out.sort(key=lambda s: s["local"])
    return out

def find_media(sid, capture_day):
    for day in [capture_day] + sorted(os.listdir(MEDIA), reverse=True):
        for ext in ("jpg", "jpeg", "png", "mp4"):
            p = os.path.join(MEDIA, day, f"{sid}.{ext}")
            if os.path.exists(p): return p
    return None

def thumb(src, dst, h=960):
    if src.endswith(".mp4"):
        tmp = dst + ".frame.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "1", "-i", src, "-frames:v", "1", tmp], check=False)
        if not os.path.exists(tmp): return False
        src = tmp
    try:
        im = Image.open(src).convert("RGB"); im.thumbnail((h * 9 // 16 + 40, h)); im.save(dst, quality=82)
    except Exception as e:
        print("thumb fail", src, e, file=sys.stderr); return False
    finally:
        if src.endswith(".frame.jpg"): os.remove(src)
    return True

def sequences(stories):
    seqs = []
    for s in stories:
        if seqs and s["local"].date() == seqs[-1][-1]["local"].date() and (s["local"] - seqs[-1][-1]["local"]).total_seconds() <= GAP_H * 3600:
            seqs[-1].append(s)
        else:
            seqs.append([s])
    return seqs

def main():
    stories = load_stories()
    seqs = sequences(stories)
    scored = []
    for seq in seqs:
        replies = sum(s.get("replies") or 0 for s in seq)
        if replies <= 0: continue
        reach = max(s.get("reach") or 0 for s in seq)
        scored.append((replies, reach, seq))
    scored.sort(key=lambda t: (t[0], t[1]), reverse=True)
    top = scored[:TOP_N]
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT, exist_ok=True)
    result = {"updated": datetime.now(ROME).isoformat(timespec="minutes"), "total_stories": len(stories), "total_sequences": len(seqs), "sequences": []}
    for rank, (replies, reach, seq) in enumerate(top, 1):
        items = []
        for s in seq:
            src = find_media(s["id"], s["capture_day"])
            fn = f"{s['id']}.jpg"
            ok = bool(src) and thumb(src, os.path.join(OUT, fn))
            items.append({
                "id": s["id"], "type": s.get("media_type"), "time": s["local"].strftime("%H:%M"),
                "replies": s.get("replies") or 0, "reach": s.get("reach") or 0, "navigation": s.get("navigation") or 0,
                "permalink": s.get("permalink"), "img": f"top/{fn}" if ok else None,
            })
        result["sequences"].append({
            "rank": rank, "date": seq[0]["local"].strftime("%Y-%m-%d"), "label": seq[0]["local"].strftime("%d/%m/%Y"),
            "from": seq[0]["local"].strftime("%H:%M"), "to": seq[-1]["local"].strftime("%H:%M"),
            "replies": replies, "reach": reach, "count": len(seq), "stories": items,
        })
    json.dump(result, open(os.path.join(OUT, "top-stories.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{len(stories)} storie, {len(seqs)} sequenze, top {len(top)} salvate in {OUT}")
    for sq in result["sequences"]:
        print(f"  #{sq['rank']} {sq['label']} {sq['from']}-{sq['to']} · {sq['count']} storie · {sq['replies']} risposte · reach max {sq['reach']}")

if __name__ == "__main__":
    main()
