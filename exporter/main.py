# exporter/main.py
import argparse
from datetime import datetime
from typing import List
from scanner.storage import DatabaseStorage
from .common import build_rows_for_scan, get_enabled_headers_and_labels, ensure_dir_for
from .csv_exporter import export_csv
from .xlsx_exporter import export_xlsx
from .pdf_exporter import export_pdf

def main():
    parser = argparse.ArgumentParser(description="BACnet Geräte-Export")
    parser.add_argument("--scan-id", type=int, required=True, help="Scan-ID aus der Datenbank")
    parser.add_argument("--format", choices=["csv", "xlsx", "pdf"], default="csv", help="Exportformat")
    parser.add_argument("--out", type=str, default="", help="Ausgabedatei (optional). Standard: exports/scan_<id>_<ts>.<ext>")
    parser.add_argument("--keys", type=str, default="", help="Kommagetrennte Key-Liste; wenn leer, werden aktivierte Felder verwendet")
    args = parser.parse_args()

    storage = DatabaseStorage()

    if args.keys.strip():
        headers: List[str] = [k.strip() for k in args.keys.split(",") if k.strip()]
        labels = {k: k for k in headers}
    else:
        headers, labels = get_enabled_headers_and_labels(storage)

    rows = build_rows_for_scan(args.scan_id, headers, storage)

    if not args.out:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.out = f"exports/scan_{args.scan_id}_{ts}.{args.format}"

    ensure_dir_for(args.out)

    if args.format == "csv":
        export_csv(args.out, rows, headers, labels)
    elif args.format == "xlsx":
        export_xlsx(args.out, rows, headers, labels)
    elif args.format == "pdf":
        export_pdf(args.out, rows, headers, labels, title=f"Geräteliste – Scan {args.scan_id}")
    print(f"Export fertig: {args.out}")

if __name__ == "__main__":
    main()
