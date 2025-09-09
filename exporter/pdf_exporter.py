# exporter/pdf_exporter.py
from typing import List, Dict, Any, Optional
from math import ceil
from xml.sax.saxutils import escape as xml_escape
import os
import json
from datetime import datetime
from pathlib import Path  # <-- NEU

from .common import ensure_dir_for


def export_pdf(path: str,
               rows: List[Dict[str, Any]],
               headers: List[str],
               header_labels: Dict[str, str],
               title: str = "Geräteliste",
               landscape_mode: bool = True,
               logo_path: str = "assets/siemens_logo.svg",
               user_info: Optional[Dict[str, Any]] = None,
               user_settings_path: Optional[str] = None):

    ensure_dir_for(path)

    try:
        from reportlab.lib.pagesizes import A4, landscape, portrait
        from reportlab.lib import colors as rl
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    except ImportError as e:
        raise ImportError("Für PDF-Export wird 'reportlab' benötigt. Installiere z.B.: pip install reportlab") from e

    # ---- Setup -----------------------------------------------------------------
    pagesize = landscape(A4) if landscape_mode else portrait(A4)
    HEADER_HEIGHT = 42  # pt
    doc = SimpleDocTemplate(
        path,
        pagesize=pagesize,
        leftMargin=24, rightMargin=24,
        topMargin=28 + HEADER_HEIGHT,
        bottomMargin=28
    )

    # User-Settings laden
    if user_info is None:
        user_info = _load_user_settings(user_settings_path)

    # Datum/Uhrzeit
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    # --- LOGO-PFAD EINMALIG ROBUST AUFLÖSEN ------------------------------------
    try:
        resolved_logo_path = _resolve_logo_path(logo_path)
        # Optional: Debugausgabe, damit du siehst, was benutzt wird
        print(f"[PDF] Verwende Logo: {resolved_logo_path}")
    except FileNotFoundError as e:
        # Kein Fallback – nur klarer Log
        print(f"[PDF] SVG-Logo nicht gefunden: {e}")
        resolved_logo_path = None

    # ---- Styles & Helpers ------------------------------------------------------
    def make_styles(font_size: int):
        from reportlab.lib.styles import ParagraphStyle
        leading = font_size + 2
        base = ParagraphStyle('cell', fontName='Helvetica', fontSize=font_size,
                              leading=leading, spaceBefore=0, spaceAfter=0)
        head = ParagraphStyle('head', parent=base, fontName='Helvetica-Bold')
        return base, head

    page_width = pagesize[0] - doc.leftMargin - doc.rightMargin

    def compute_col_widths(headers_: List[str], rows_: List[Dict[str, Any]], min_w=50, max_w=260):
        weights = []
        sample_n = min(120, len(rows_))
        for h in headers_:
            hl = len(str(header_labels.get(h, h)))
            avg = 0
            if sample_n > 0:
                total = 0
                for r in rows_[:sample_n]:
                    total += len(str(r.get(h, "")))
                avg = total / sample_n
            w = max(1.0, hl * 1.0 + avg * 1.2)
            weights.append(w)
        s = sum(weights) or len(headers_)
        raw = [(w / s) * page_width for w in weights]
        clamped = [max(min_w, min(max_w, v)) for v in raw]
        factor = page_width / sum(clamped)
        return [v * factor for v in clamped]

    def para_lines(par: Paragraph, col_w: float, leading: float) -> int:
        _, h = par.wrap(col_w, 10000)
        return int(ceil(h / leading)) if leading > 0 else 1

    def fit_paragraph(text: Any, style: ParagraphStyle, col_w: float, max_lines: int = 3) -> Paragraph:
        t = "" if text is None else str(text)
        t = t.replace("\n", " ")
        safe = xml_escape(t)
        p = Paragraph(safe, style)
        if para_lines(p, col_w, style.leading) <= max_lines:
            return p
        lo, hi = 0, len(safe)
        best = "…"
        while lo < hi:
            mid = (lo + hi) // 2
            cand = safe[:mid] + "…"
            p = Paragraph(cand, style)
            if para_lines(p, col_w, style.leading) <= max_lines:
                best = cand
                lo = mid + 1
            else:
                hi = mid
        return Paragraph(best, style)

    def overflow_ratio(font_size: int, col_widths: List[float], sample_rows=60) -> float:
        base, head = make_styles(font_size)
        sample_rows = min(sample_rows, len(rows))
        if sample_rows == 0:
            return 0.0
        overflow = 0
        total = sample_rows * len(headers)
        for r in rows[:sample_rows]:
            for j, h in enumerate(headers):
                p = Paragraph(xml_escape(str(r.get(h, ""))), base)
                if para_lines(p, col_widths[j], base.leading) > 3:
                    overflow += 1
        return overflow / max(1, total)

    candidate_sizes = [10, 9, 8, 7]
    col_widths = compute_col_widths(headers, rows)
    chosen_size = candidate_sizes[-1]
    for fs in candidate_sizes:
        if overflow_ratio(fs, col_widths) <= 0.05:
            chosen_size = fs
            break
    base_style, head_style = make_styles(chosen_size)

    head_row = [Paragraph(xml_escape(str(header_labels.get(h, h))), head_style) for h in headers]
    table_data = [head_row]
    for r in rows:
        table_data.append([fit_paragraph(r.get(h, ""), base_style, col_widths[j], max_lines=3)
                           for j, h in enumerate(headers)])

    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors as rl
    tbl = Table(table_data, colWidths=col_widths, repeatRows=1, splitByRow=1)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl.HexColor("#EEEEEE")),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl.black),
        ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.25, rl.grey),
        ("LEFTPADDING",  (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING",   (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl.whitesmoke, rl.white]),
    ]))

    # ---- Header-Zeichner -------------------------------------------------------
    def draw_header(canv, doc_):
        canv.saveState()
        x_left = doc_.leftMargin
        y_top = pagesize[1] - 18

        logo_drawn_w = 0.0
        try:
            if not resolved_logo_path:
                raise FileNotFoundError(f"{logo_path}")
            logo_drawn_w = _draw_svg_logo(canv, resolved_logo_path, x_left, y_top, target_h=HEADER_HEIGHT - 10)
        except Exception as e:
            print(f"[PDF] SVG-Logo konnte nicht gezeichnet werden: {e}")
            logo_drawn_w = 0.0

        left_x = x_left + (logo_drawn_w + 12 if logo_drawn_w else 0)
        right_x = pagesize[0] - doc_.rightMargin

        canv.setFont("Helvetica-Bold", 12)
        canv.drawString(left_x, y_top - 12, title)

        canv.setFont("Helvetica", 9)
        user_line = _compose_user_line(user_info)
        canv.drawString(left_x, y_top - 26, user_line)
        canv.drawRightString(right_x, y_top - 26, f"Erstellt am: {now_str}")
        canv.restoreState()

    story = [tbl]
    doc.build(story, onFirstPage=draw_header, onLaterPages=draw_header)


# ----------------------- Hilfsfunktionen ----------------------------------------

def _resolve_logo_path(logo_path: str) -> str:
    """
    Löst logo_path robust auf:
    - absolute Pfade direkt
    - relativ zu diesem Modul (../assets/…)
    - relativ zum aktuellen Arbeitsverzeichnis (cwd)
    - optional über Kivy resource_find
    Gibt einen absoluten Pfad zurück oder wirft FileNotFoundError.
    """
    requested = Path(logo_path)

    # 1) Bereits absolut oder relativ, aber existent?
    if requested.is_file():
        return str(requested.resolve())

    # 2) relativ zu diesem File (exporter/pdf_exporter.py)
    here = Path(__file__).resolve()
    candidates = [
        here.parent / logo_path,              # exporter/ + assets/...
        here.parent.parent / logo_path,       # projektroot/ + assets/...
        Path.cwd() / logo_path,               # aktuelles Arbeitsverzeichnis
    ]

    # 3) Kivy resource_find (falls verfügbar)
    try:
        from kivy.resources import resource_find
        found = resource_find(logo_path)
        if found:
            candidates.append(Path(found))
    except Exception:
        pass

    for c in candidates:
        if c and Path(c).is_file():
            return str(Path(c).resolve())

    # Debug-Infos helfen beim Diagnostizieren
    debug = f"cwd={Path.cwd()} | __file__={here} | geprüft={', '.join(str(p) for p in candidates)}"
    raise FileNotFoundError(f"Logo nicht gefunden: {logo_path} | {debug}")


def _draw_svg_logo(canv, logo_path: str, x_left: float, y_top: float, target_h: float) -> float:
    """
    SVG mit svglib laden, proportional auf target_h skalieren und zeichnen.
    Gibt die gezeichnete Breite (pt) zurück.
    """
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF

    drawing = svg2rlg(logo_path)
    if drawing is None or not getattr(drawing, "width", None) or not getattr(drawing, "height", None):
        raise ValueError("Ungültige SVG-Abmessungen")

    orig_w = float(drawing.width)
    orig_h = float(drawing.height)
    if orig_h <= 0.0:
        raise ValueError("SVG-Höhe ist 0")

    scale = float(target_h) / orig_h
    drawing.scale(scale, scale)
    renderPDF.draw(drawing, canv, x_left, y_top - target_h)
    return orig_w * scale


def _compose_user_line(user_info: Optional[Dict[str, Any]]) -> str:
    if not user_info:
        return "User: unbekannt"
    first = (user_info.get("first_name") or "").strip()
    last = (user_info.get("last_name") or "").strip()
    email = (user_info.get("email") or "").strip()
    company = (user_info.get("company") or user_info.get("organization") or "").strip()

    name = (f"{first} {last}".strip()) or email or "unbekannt"
    if email and name != email:
        name = f"{name} ({email})"
    if company:
        return f"User: {name} – {company}"
    return f"User: {name}"


def _load_user_settings(user_settings_path: Optional[str]) -> Dict[str, Any]:
    candidates = []
    if user_settings_path:
        candidates.append(user_settings_path)
    candidates.extend([
        "config/user_settings.json",
        "data/user_settings.json",
        "user_settings.json",
    ])
    for p in candidates:
        try:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f) or {}
        except Exception:
            pass
    return {}
