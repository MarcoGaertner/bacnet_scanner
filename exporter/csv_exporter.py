# exporter/csv_exporter.py
import csv
from typing import List, Dict, Any
from .common import ensure_dir_for

def export_csv(path: str, rows: List[Dict[str, Any]], headers: List[str], header_labels: Dict[str, str], delimiter: str = ";"):
    ensure_dir_for(path)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=delimiter)
        w.writerow([header_labels.get(h, h) for h in headers])
        for r in rows:
            w.writerow([r.get(h, "") for h in headers])
