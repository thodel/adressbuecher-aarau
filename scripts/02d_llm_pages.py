"""02d_llm_pages.py — frühe Aarauer Bände seitenweise mit einem Sprachmodell lesen (JSON Lines).

    scripts/02d_llm_pages.py --run gemini-frueh-v1 --reader gemini-3.5-flash --volumes 1833,1859,1867,1869,1877,1879,1881
    set -a; source ~/.gpustack.env; set +a
    scripts/02d_llm_pages.py --run qwen-1900hn-v1 --reader qwen --volumes 1900

Häuserverzeichnisse 1833–1881 (Fraktur) mit Gemini, Hausnumerierung 1900 (Antiqua-Tabelle) mit qwen3.8-27b
(GPUStack, Bild 2× Lanczos): Stichprobe 16.11.2026, 16 Seiten, Fraktur Gemini 95 % / qwen 61 % voll korrekt,
1900 beide 97 %. Schreibt data/atr/<run>/<seite>.json (Rohantwort, Zeit, Token) und .jsonl (Einträge);
vorhandene Seiten werden übersprungen. Gemini-Schlüssel aus GEMINI_API_KEY oder ../adressbuecher-bern-frueh/.env;
Schlüssel werden nie ausgegeben."""
import argparse, base64, io, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

PROMPT = """Du siehst eine Seite aus einem Aarauer Häuser- und Einwohnerverzeichnis des 19. Jahrhunderts (Fraktur). Das Verzeichnis ist nach Häusern geordnet: links die Hausnummer (Nro.), daneben der Hausbesitzer bzw. die erste Partei, eingerückt darunter weitere Bewohner desselben Hauses. Zwischentitel nennen Strassen, Gassen oder Quartiere.
Am rechten Bildrand kann ein Streifen der Nachbarseite sichtbar sein (abgeschnittene Nummern): diesen ignorieren.

Gib JEDE Personen- bzw. Gebäudezeile als eine JSON-Zeile aus (JSON Lines, kein Markdown, kein Kommentar), von oben nach unten.
Felder ("type":"entry"):
- "text": die Zeile genau wie gedruckt (Abkürzungen nicht auflösen, Schreibung der Vorlage; Folgezeilen eines Eintrags anhängen, Trennstriche auflösen)
- "house_no": die Hausnummer, unter der der Eintrag steht, wie gedruckt ("458 & 459", "686 u. 687", "129–130" bei Klammer); bei eingerückten Folgeeinträgen die Nummer des Hauses darüber
- "marker": Zeichen hinter der Nummer ("*", "†"), sonst ""
- "surname", "alliance_name" (Teil nach Bindestrich, Matter-Märk -> "Märk"), "forename" (wie gedruckt), "title", "civil_status" (Wittwe, Frau, Jgfr., geb. ... wie gedruckt), "occupation", "origin" (Heimatort nach "von"/"v."/"aus")
- "heading": der zuletzt gesehene Zwischentitel (Strasse/Quartier), sonst ""
Wenn der Vorname vor dem Familiennamen steht ("Daniel Hunziker, Lehrers Wittwe"), trotzdem richtig in surname/forename trennen. "Derselbe"/"Dieselbe" als surname stehen lassen.
Zwischentitel als {"type":"heading","text":...}; Seitenzahl/Kopf als {"type":"pageheader","text":...}.
Fraktur: Das lange s (ſ) ist ein s, nie ein f (Häßig, Gysi, Reist; nicht Häfig, Gyfi, Reift); ß bleibt ß; V und B, I und J, k und x genau unterscheiden. Schreibweisen nicht modernisieren (Condukteur bleibt Condukteur, Architekt bleibt Architekt).
Eine geschweifte Klammer über mehreren Hausnummern gehört zu EINEM Eintrag: einmal ausgeben, "house_no" = "415–417". Das Feld "text" bei jedem Eintrag ausfüllen.
Zeilen oben auf der Seite ohne eigene Hausnummer (Fortsetzung von der Vorseite) bekommen "house_no":"". Ein alphabetisches Namensregister ("Name, Beruf Nummer") gibt jede Registerzeile als eigenen Eintrag aus, die Nummer in "house_no".
Erfinde nichts. Unlesbares mit [?] markieren. Lass keine Zeile aus. Am Ende {"type":"end","n_entries":<Anzahl>}."""

PROMPT_1900 = """Du siehst eine Seite aus dem «Verzeichnis der neuen Hausnumerierung der Stadt Aarau» (1900): je Zeile die neue Hausnummer, der Eigentümer (Name fett, Vorname, Beruf), die Gebäudeart (Wohnhaus, Scheune …) und rechts die alte Nummer.
Gib JEDE Zeile als eine JSON-Zeile aus (JSON Lines, kein Markdown), von oben nach unten.
Felder ("type":"row"): "text" (die Zeile wie gedruckt; umbrochene Folgezeilen anhängen), "new_no", "surname" (bei "—" den Namen der Zeile darüber einsetzen), "alliance_name" (Teil nach Bindestrich), "forename", "civil_status" (Ww. usw.), "occupation", "building" (Gebäudeart, Wiederholungszeichen „ auflösen), "old_no" (wie gedruckt, auch "864/1551", "—" wenn keine).
Zwischentitel (Strassen) als {"type":"heading","text":...}; Kopfzeilen als {"type":"pageheader","text":...}.
Eine Zeile, auf der nur die neue Nummer steht, als Zeile mit leeren Feldern ausgeben (nichts von der Nachbarzeile übernehmen). Wiederholungszeichen „ bedeutet: Wert der Zeile darüber.
Erfinde nichts; Unlesbares mit [?]. Am Ende {"type":"end","n_rows":<Anzahl>}."""

def prompt_for(p): return PROMPT_1900 if p.name.startswith("1900_") else PROMPT

def parse(text):
    rows, bad = [], 0
    for ln in text.splitlines():
        ln = ln.strip().strip(",")
        if ln.startswith("```") or not ln.startswith("{"): continue
        try: rows.append(json.loads(ln))
        except json.JSONDecodeError: bad += 1
    return rows, bad

def qwen(path):
    from PIL import Image
    im = Image.open(path).convert("RGB"); im = im.resize((im.width*2, im.height*2), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "PNG")
    body = {"model": "qwen3.8-27b", "temperature": 0, "max_tokens": 16000,
            "chat_template_kwargs": {"enable_thinking": False},
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()}},
                {"type": "text", "text": prompt_for(path)}]}]}
    req = urllib.request.Request(os.environ["GPUSTACK_BASE_URL"].rstrip("/") + "/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": "Bearer " + os.environ["GPUSTACK_API_KEY"], "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=900) as r: resp = json.loads(r.read())
    return resp["choices"][0]["message"].get("content") or "", resp["choices"][0].get("finish_reason"), resp.get("usage", {}).get("completion_tokens")

def gemini(path, model):
    from google import genai
    from google.genai import types
    key = os.environ.get("GEMINI_API_KEY", "").strip() or None
    env = Path(__file__).resolve().parents[2] / "adressbuecher-bern-frueh" / ".env"
    for ln in (env.read_text().splitlines() if not key and env.exists() else []):
        k, _, v = ln.partition("=")
        if k.strip() in ("GEMINI_API_KEY", "GOOGLE_API_KEY") and v.strip(): key = v.strip().strip('"')
    client = genai.Client(api_key=key)
    mime = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    cfg = types.GenerateContentConfig(temperature=0, max_output_tokens=32000,
                                      thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW))
    r = client.models.generate_content(model=model, contents=[types.Part.from_bytes(data=path.read_bytes(), mime_type=mime), prompt_for(path)], config=cfg)
    fin = r.candidates[0].finish_reason if r.candidates else None
    return r.text or "", str(fin), getattr(r.usage_metadata, "candidates_token_count", None)

def run(job):
    path, reader, out = job
    stem = path.stem
    if (out / f"{stem}.json").exists(): return f"{stem}: schon da"
    t0 = time.time()
    try:
        text, fin, tok = qwen(path) if reader == "qwen" else gemini(path, reader)
    except Exception as e:
        return f"{stem}: FEHLER {type(e).__name__} {str(e)[:200]}"
    rows, bad = parse(text)
    ended = bool(rows) and rows[-1].get("type") == "end"
    (out / f"{stem}.json").write_text(json.dumps({"image": str(path), "reader": reader, "seconds": round(time.time()-t0, 1),
        "finish": fin, "tokens": tok, "ended": ended, "bad": bad, "content": text}, ensure_ascii=False, indent=1))
    (out / f"{stem}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    n = sum(r.get("type") in ("entry", "row") for r in rows)
    return f"{stem}: {time.time()-t0:.0f}s fin={fin} ended={ended} n={n} bad={bad} tok={tok}"

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", required=True); ap.add_argument("--reader", required=True, help="qwen oder ein Gemini-Modell")
    ap.add_argument("--volumes", required=True); ap.add_argument("--pages", default="", help="z. B. 5,6,7 (sonst alle)")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    out = Path("data/atr") / a.run; out.mkdir(parents=True, exist_ok=True)
    want = {int(p) for p in a.pages.split(",") if p}
    imgs = [p for v in a.volumes.split(",") for p in sorted(Path("data/pages", v).glob(f"{v}_p*.*"))
            if not want or int(p.stem.split("_p")[1]) in want]
    print(f"{time.strftime('%H:%M:%S')} {a.run}: {len(imgs)} Seiten, Leser {a.reader}", flush=True)
    with ThreadPoolExecutor(a.workers) as ex:
        for msg in ex.map(run, [(p, a.reader, out) for p in imgs]): print(time.strftime("%H:%M:%S"), msg, flush=True)
