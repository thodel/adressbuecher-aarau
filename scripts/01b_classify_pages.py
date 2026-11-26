"""01b_classify_pages.py — jede Seite eines Bandes einem Teil zuordnen (qwen3.8, nur Seitenart, kein Lesen).

    set -a; . ~/.gpustack.env; set +a
    python3 scripts/01b_classify_pages.py --pages <ordner mit 1901_p001.jpeg …> --out classify_1901.csv

Für Bände ohne PDF (1901, 1913 von der DNB als TIFF). Je Seite ein Bild von 600 px Breite; qwen3.8-27b
(GPUStack, Schlüssel aus der Umgebung, nie ausgegeben) nennt den Teil. Die Seitenbereiche in 01_pages.csv
setzt danach ein Mensch nach Prüfung am Bild; die Zuordnung ist nur ein Vorschlag. Fortsetzbar.
"""
from __future__ import annotations

import argparse
import base64
import csv
import io
import json
import os
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PARTS = ("gebaeude", "einwohner", "berufe", "behoerden", "inserate", "vorspann", "leer")
PROMPT = """Du siehst eine Seite aus einem Adressbuch der Stadt Aarau (um 1900). Antworte NUR mit einem JSON-Objekt,
ohne Markdown: {"teil": "...", "spalten": 1 oder 2}.
teil, genau eines von:
- "gebaeude": Verzeichnis der Gebäude und ihrer Bewohner, nach Hausnummern (Haus-Nr. links, darunter die Bewohner)
- "einwohner": alphabetisches Verzeichnis der Einwohner und Firmen (Familienname, Vorname, Beruf, Adresse)
- "berufe": Verzeichnis nach Berufen, Gewerben oder Branchen (Zwischentitel sind Berufe)
- "behoerden": Behörden, Ämter, Vereine, Kirchen, Schulen, Zeitungen, Tarife, Kalender
- "inserate": ganzseitige Anzeigen oder Reklame
- "vorspann": Titelblatt, Inhaltsverzeichnis, Vorwort, Strassenverzeichnis, Karte
- "leer": leere Seite oder Einband
spalten: Zahl der Textspalten der Einträge."""


def small(path: Path) -> str:
    from PIL import Image
    im = Image.open(path).convert("RGB")
    im.thumbnail((600, 1200))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def ask(b64: str) -> dict:
    base = os.environ["GPUSTACK_BASE_URL"].rstrip("/")
    body = {"model": "qwen3.8-27b", "temperature": 0, "max_tokens": 60,
            "chat_template_kwargs": {"enable_thinking": False},
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                {"type": "text", "text": PROMPT}]}]}
    req = urllib.request.Request(f"{base}/chat/completions", data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {os.environ['GPUSTACK_API_KEY']}",
                                          "Content-Type": "application/json"})
    for i in range(4):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                text = json.loads(r.read())["choices"][0]["message"].get("content") or ""
            m = re.search(r"\{.*\}", text, re.S)
            d = json.loads(m.group()) if m else {}
            part = d.get("teil", "")
            return {"part": part if part in PARTS else "vorspann", "columns": str(d.get("spalten", ""))}
        except (OSError, ValueError):
            if i == 3:
                return {"part": "", "columns": ""}
            time.sleep(30 * (i + 1))
    return {"part": "", "columns": ""}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pages", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    done = {}
    if a.out.exists():
        done = {r["key"]: r for r in csv.DictReader(open(a.out, encoding="utf-8")) if r["part"]}
    todo = [p for p in sorted(a.pages.glob("*.jpeg")) if p.stem not in done]

    def one(p: Path) -> dict:
        return {"key": p.stem, "page": int(p.stem.split("_p")[1]), **ask(small(p))}

    with ThreadPoolExecutor(4) as ex:
        for r in ex.map(one, todo):
            done[r["key"]] = r
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["key", "page", "part", "columns"])
        w.writeheader(); w.writerows(sorted(done.values(), key=lambda r: int(r["page"])))
    print(f"{a.out}: {len(done)} Seiten")


if __name__ == "__main__":
    main()
