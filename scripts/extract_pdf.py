"""Extract page-indexed text from PDFs into data/extracted/.

Install PyMuPDF separately in a trusted environment: python -m pip install pymupdf
Scanned pages with no text require OCR and are reported for follow-up.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "sources"
OUT_DIR = ROOT / "data" / "extracted"


def main() -> None:
    try:
        import fitz
    except ImportError as exc:
        raise SystemExit("Нужен PyMuPDF: python -m pip install pymupdf") from exc

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = []
    manifest = ROOT / 'data' / 'sources.json'
    inventory = json.loads(manifest.read_text(encoding='utf-8'))
    for pdf in [SOURCE_DIR / item['name'] for item in inventory]:
        doc = fitz.open(pdf)
        pages = []
        blank = []
        for number, page in enumerate(doc, start=1):
            text = page.get_text("text").strip()
            if not text:
                blank.append(number)
            pages.append({"page": number, "text": text})
        target = OUT_DIR / f"{pdf.stem}.json"
        target.write_text(json.dumps({"source": pdf.name, "pages": pages}, ensure_ascii=False, indent=2), encoding="utf-8")
        report.append({"file": pdf.name, "pages": len(doc), "pages_needing_ocr": blank, "output": str(target.relative_to(ROOT))})
        print(f"{pdf.name}: {len(doc)} стр., OCR проверить: {len(blank)}")
    (OUT_DIR / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
