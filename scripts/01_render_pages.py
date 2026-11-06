"""01_render_pages.py — Seitenbilder aus den Adressbuch-PDFs holen.

Die PDFs enthalten je Seite genau ein eingebettetes Graustufen-JPEG (1000 px breit,
~120 dpi). Ein Neurendern würde nur interpolieren; darum wird das Bild byteidentisch
extrahiert. Hat eine Seite nicht genau ein Bild, wird sie mit 300 dpi gerendert und
das in 01_pages.csv vermerkt.

Schreibt:
  <out>/<jahr>/<jahr>_p<nnn>.<ext>        die Seitenbilder (nicht im Git)
  <csv>/00_volumes.csv                     Band, PDF, Seitenzahl, SHA-256
  <csv>/01_pages.csv                       eine Zeile je Seite; Abschnitt leer, wird in
                                           Welle 0 von Hand/halbautomatisch gefüllt.
Vorhandene Abschnittsangaben in 01_pages.csv bleiben erhalten (Merge über volume,page).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path

import pymupdf

SECTIONS = ("vorspann", "gebaeude", "einwohner", "berufe", "zeitungen",
            "behoerden", "inserate", "leer", "sonst")

PAGE_FIELDS = ["volume", "page", "image", "width", "height", "source",
               "printed_page", "section", "typeface", "columns", "note"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def year_of(pdf: Path) -> str:
    m = re.search(r"(18\d\d|19\d\d)", pdf.stem)
    if not m:
        raise SystemExit(f"kein Jahr im Dateinamen: {pdf.name}")
    return m.group(1)


def read_existing(csv_path: Path) -> dict[tuple[str, str], dict]:
    if not csv_path.exists():
        return {}
    with csv_path.open(newline="", encoding="utf-8") as fh:
        return {(r["volume"], r["page"]): r for r in csv.DictReader(fh)}


def extract(pdf: Path, out_dir: Path, year: str) -> list[dict]:
    doc = pymupdf.open(pdf)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, page in enumerate(doc, start=1):
        images = page.get_images(full=True)
        name = f"{year}_p{i:03d}"
        if len(images) == 1:
            im = doc.extract_image(images[0][0])
            target = out_dir / f"{name}.{im['ext']}"
            if not target.exists():
                target.write_bytes(im["image"])
            w, h, source = im["width"], im["height"], "embedded"
        else:
            target = out_dir / f"{name}.png"
            pix = page.get_pixmap(dpi=300)
            if not target.exists():
                pix.save(target)
            w, h, source = pix.width, pix.height, f"rendered300:{len(images)}img"
        rows.append({"volume": year, "page": str(i),
                     "image": str(target.relative_to(out_dir.parent)),
                     "width": str(w), "height": str(h), "source": source,
                     "printed_page": "", "section": "", "typeface": "",
                     "columns": "", "note": ""})
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pdf-dir", required=True, type=Path)
    ap.add_argument("--out", default=Path("data/pages"), type=Path)
    ap.add_argument("--csv", default=Path("data/csv"), type=Path)
    args = ap.parse_args()

    pdfs = sorted(args.pdf_dir.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"keine PDFs in {args.pdf_dir}")
    args.csv.mkdir(parents=True, exist_ok=True)
    pages_csv = args.csv / "01_pages.csv"
    existing = read_existing(pages_csv)

    volumes, pages = [], []
    for pdf in pdfs:
        year = year_of(pdf)
        rows = extract(pdf, args.out / year, year)
        for r in rows:
            old = existing.get((r["volume"], r["page"]))
            if old:
                for k in ("printed_page", "section", "typeface", "columns", "note"):
                    r[k] = old.get(k, "")
        pages.extend(rows)
        volumes.append({"volume": year, "pdf": pdf.name, "pages": str(len(rows)),
                        "sha256": sha256(pdf)})
        print(f"{year}: {len(rows)} Seiten → {args.out / year}")

    with (args.csv / "00_volumes.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["volume", "pdf", "pages", "sha256"])
        w.writeheader(); w.writerows(volumes)
    with pages_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=PAGE_FIELDS)
        w.writeheader(); w.writerows(pages)
    print(f"{len(pages)} Seiten in {pages_csv}")


if __name__ == "__main__":
    main()
