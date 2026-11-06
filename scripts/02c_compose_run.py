"""02c_compose_run.py — Endstand je Seite aus Haupt- und Ersatzlesung zusammensetzen.

    python scripts/02c_compose_run.py --name aarau-antiqua-final \
        --primary aarau-antiqua-qwen38-v1/qwen3.8-27b --fallback aarau-antiqua-gemini-retry-v1/gemini-3.8-flash

Nimmt je Seite die Hauptlesung; ist sie am Token-Deckel abgeschnitten oder leer und gibt
es eine Ersatzlesung, gilt diese. Schreibt data/atr/<name>/final/<key>.json und
data/csv/02_reading_choice.csv (eine Zeile je Seite: welcher Lauf, welcher Leser, warum).
Die Parser lesen danach `--run <name> --reader final`.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

ATR = Path("data/atr")
CHOICE = Path("data/csv/02_reading_choice.csv")


def bad(d: dict) -> str:
    q = d.get("quality") or {}
    if d.get("truncated"):
        return "abgeschnitten"
    if q.get("verdict") == "empty":
        return "leer"
    return ""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--name", required=True)
    ap.add_argument("--primary", required=True)
    ap.add_argument("--fallback", action="append", default=[])
    args = ap.parse_args()
    out = ATR / args.name / "final"
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    if CHOICE.exists():
        with CHOICE.open(encoding="utf-8") as fh:
            rows = [r for r in csv.DictReader(fh) if r["final_run"] != args.name]
    for jp in sorted((ATR / args.primary).glob("*.json")):
        d = json.loads(jp.read_text(encoding="utf-8"))
        reason, src = bad(d), args.primary
        if reason:
            for fb in args.fallback:
                fp = ATR / fb / jp.name
                if fp.exists() and not bad(json.loads(fp.read_text(encoding="utf-8"))):
                    src = fb
                    break
        shutil.copyfile(ATR / src / jp.name, out / jp.name)
        rows.append({"key": jp.stem, "final_run": args.name, "source": src, "primary_problem": reason,
                     "note": "Ersatzlesung" if src != args.primary else ("Problem ohne Ersatz" if reason else "")})
    with CHOICE.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["key", "final_run", "source", "primary_problem", "note"])
        w.writeheader(); w.writerows(rows)
    mine = [r for r in rows if r["final_run"] == args.name]
    print(f"{len(mine)} Seiten → {out}; Ersatz: {sum(1 for r in mine if r['note'] == 'Ersatzlesung')}, "
          f"ohne Ersatz: {sum(1 for r in mine if r['note'] == 'Problem ohne Ersatz')}")


if __name__ == "__main__":
    main()
