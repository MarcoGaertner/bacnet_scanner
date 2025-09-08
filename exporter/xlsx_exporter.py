# exporter/xlsx_exporter.py
from typing import List, Dict, Any
from .common import ensure_dir_for

def export_xlsx(path: str, rows: List[Dict[str, Any]], headers: List[str], header_labels: Dict[str, str]):
    ensure_dir_for(path)
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError("Für XLSX-Export wird 'pandas' (und 'openpyxl') benötigt.") from e

    df = pd.DataFrame(rows)
    # nur gewählte Reihenfolge & Labels
    df = df.reindex(columns=headers)
    df = df.rename(columns={h: header_labels.get(h, h) for h in headers})
    df.to_excel(path, index=False)
