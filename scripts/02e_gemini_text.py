"""02e_gemini_text.py — Seiten der DNB-Bände (1901/1913) mit Gemini als Text lesen, im Format der qwen-Läufe.

    uv run -q --with google-genai python scripts/02e_gemini_text.py --images DIR --pages 1913:148,215 --run aarau-dnb-gemini-1913
    uv run -q --with google-genai python scripts/02e_gemini_text.py --images DIR --section 1913:einwohner --run aarau-dnb-gemini-1913

Anlass: Stichprobe 1913 (Einwohner, qwen3.8-27b) 29 von 39 voll korrekt, fast nur Lesefehler in Orts- und Allianznamen
(#9). Schreibt data/atr/<run>/<model>/<Band>_p<Seite>.json wie die atr-batch-Läufe (Feld `text`), damit 04_parse.py und
05_buildings.py unverändert lesen (`--run <run> --reader <model>`), dazu Token und Preis je Seite (Listenpreis
$1.50 / $9.00 je Mio. Token Ein-/Ausgabe, Denken = Ausgabe, wie in adressbuecher-bern). Vorhandene Seiten werden
übersprungen. Schutz: Halt, wenn nach 10 Seiten der Mittelwert über 0.08 $ je Seite oder der Lauf über `--budget` liegt.
Schlüssel aus GEMINI_API_KEY oder ~/Repos/adressbuecher-bern-frueh/.env; er wird nie ausgegeben."""
from __future__ import annotations

import argparse
import csv
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PRICE_IN, PRICE_OUT = 1.50e-6, 9.00e-6

PROMPT = """Du siehst eine Seite aus dem Adressbuch der Stadt Aarau ({vol}), Antiqua-Satz, Einwohnerverzeichnis in alphabetischer Ordnung.
Schreib den Text der Seite ab, genau wie gedruckt, von oben nach unten, eine gedruckte Zeile pro Ausgabezeile.

Regeln:
- Buchstabe für Buchstabe wie gedruckt. Nichts modernisieren und nichts verbessern: «Ue», «Oe», «Ae» bleiben («Ueberlingen», nicht «Überlingen»), «ß» bleibt «ß», «th» bleibt «th», Abkürzungen und Satzzeichen wie gedruckt.
- Nur lateinische Buchstaben mit den deutschen und französischen Akzenten; keine kyrillischen oder griechischen Zeichen.
- Der Gedankenstrich am Zeilenanfang («— Marie, …», «— -Häfeli, Gottfried, …») wiederholt den Familiennamen der Zeile darüber: ihn immer als «—» abschreiben, nie weglassen.
- Eine eingerückte Folgezeile desselben Eintrags beginnt mit zwei Leerzeichen. Die Silbentrennung am Zeilenende stehen lassen («Spi-»).
- Das Telefonzeichen (Hörer, Hand oder Pfeil) als «[tel]» schreiben. Sternchen «*» vor dem Namen behalten.
- Die Kopfzeile (Seitenzahl, Kolumnentitel) als erste Zeile wie gedruckt.
- Orts- und Familiennamen besonders genau lesen; sie sind oft selten (Eggiwil, Hägglingen, Hilfiker, Wartau).
- Wortreste vom Rand der Nachbarseite weglassen. Unlesbares als [?].
- Nur den Text ausgeben, kein Markdown, kein Kommentar."""


def api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    env = Path.home() / "Repos" / "adressbuecher-bern-frueh" / ".env"
    if not key and env.exists():
        for ln in env.read_text().splitlines():
            k, _, v = ln.partition("=")
            if k.strip() in ("GEMINI_API_KEY", "GOOGLE_API_KEY") and v.strip():
                key = v.strip().strip('"').strip("'")
    if not key:
        raise SystemExit("kein Gemini-Schlüssel")
    return key


def read_page(path: Path, vol: str, model: str, client) -> dict:
    from google.genai import types
    cfg = types.GenerateContentConfig(temperature=0, max_output_tokens=16000,
                                      thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW))
    t0 = time.time()
    r = client.models.generate_content(model=model, config=cfg, contents=[
        types.Part.from_bytes(data=path.read_bytes(), mime_type="image/jpeg"), PROMPT.format(vol=vol)])
    u = r.usage_metadata
    tin, tout, tthink = (u.prompt_token_count or 0), (u.candidates_token_count or 0), (getattr(u, "thoughts_token_count", 0) or 0)
    fin = str(r.candidates[0].finish_reason) if r.candidates else ""
    return {"schema": "atr-batch/1", "model": model, "model_version": getattr(r, "model_version", ""),
            "source": {"key": path.stem, "name": path.name}, "text": (r.text or "").strip("\n"),
            "truncated": "MAX_TOKENS" in fin, "finish": fin, "timing_ms": int((time.time() - t0) * 1000),
            "usage": {"input": tin, "output": tout, "thoughts": tthink},
            "cost_usd": round(tin * PRICE_IN + (tout + tthink) * PRICE_OUT, 5),
            "settings": "prompt-02e-v1+think-low|max16000", "recognised_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--images", type=Path, required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--model", default="gemini-3.5-flash")
    ap.add_argument("--pages", default="", help="Band:Seite,Seite (z. B. 1913:148,215)")
    ap.add_argument("--section", default="", help="Band:Abschnitt aus 01_pages.csv (z. B. 1913:einwohner)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--budget", type=float, default=12.0)
    a = ap.parse_args()
    keys = []
    if a.pages:
        vol, pp = a.pages.split(":")
        keys = [f"{vol}_p{int(p):03d}" for p in pp.split(",")]
    if a.section:
        vol, sec = a.section.split(":")
        with open("data/csv/01_pages.csv", encoding="utf-8") as f:
            keys += [f"{r['volume']}_p{int(r['page']):03d}" for r in csv.DictReader(f) if r["volume"] == vol and r["section"] == sec]
    out = Path("data/atr") / a.run / a.model
    out.mkdir(parents=True, exist_ok=True)
    todo = [k for k in keys if not (out / f"{k}.json").exists()]
    spent = sum(json.loads(p.read_text()).get("cost_usd", 0) for p in out.glob("*.json"))
    print(f"{time.strftime('%H:%M:%S')} {a.run}: {len(keys)} Seiten, offen {len(todo)}, bisher {spent:.2f} $", flush=True)
    from google import genai
    client = genai.Client(api_key=api_key())
    done, cost = 0, 0.0

    def one(k: str) -> str:
        d = read_page(a.images / f"{k}.jpeg", k.split("_p")[0], a.model, client)
        (out / f"{k}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        return f"{k}: {d['timing_ms'] // 1000}s {d['finish']} {d['usage']} {d['cost_usd']:.4f} $ ({d['model_version']})"

    with ThreadPoolExecutor(a.workers) as ex:
        for i in range(0, len(todo), a.workers):
            for k, msg in zip(todo[i:i + a.workers], ex.map(one, todo[i:i + a.workers])):
                print(time.strftime("%H:%M:%S"), msg, flush=True)
                done += 1
                cost += json.loads((out / f"{k}.json").read_text())["cost_usd"]
            if done >= 10 and cost / done > 0.08 or spent + cost > a.budget:
                print(f"HALT: {done} Seiten, {cost:.2f} $ (Mittel {cost / done:.3f} $), zusammen {spent + cost:.2f} $")
                return
    print(f"{time.strftime('%H:%M:%S')} fertig: {done} Seiten, {cost:.2f} $, zusammen {spent + cost:.2f} $")


if __name__ == "__main__":
    main()
