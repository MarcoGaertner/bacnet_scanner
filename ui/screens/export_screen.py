from typing import List, Dict
import os
from datetime import datetime

from kivy.lang import Builder
from kivy.properties import NumericProperty, ListProperty, StringProperty, DictProperty, ObjectProperty
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.resources import resource_find

from ui.styles import colors
from ui.styles.colors import ThemeColors
from ui.screens.base_screen import BaseScreen
from scanner.storage import DatabaseStorage
from exporter.common import build_rows_for_scan
from exporter.csv_exporter import export_csv
from exporter.xlsx_exporter import export_xlsx
from exporter.pdf_exporter import export_pdf
from core.config import ConfigManager

# Vorschau-Widgets
from ui.widgets.pdf_preview import PdfPreview
from ui.widgets.spreadsheet_preview import SpreadsheetPreview

# Radio-Buttons aus deinem Projekt
from ui.widgets.radio_button import RadioButtonGroup, SimpleRadioButton


class HeaderIconButton(ButtonBehavior, Image):
    """Klickbares Icon (Zahnrad)."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = True
        self.color = (1, 1, 1, 1)

    def on_kv_post(self, *args):
        src = getattr(self, "source", "") or ""
        if not resource_find(src):
            for alt in ("ui/assets/icons/settings.png", "ui/assets/icons/settings.svg", "ui/assets/icons/settings.ico"):
                if resource_find(alt):
                    self.source = alt
                    break

    def on_press(self, *args):
        self.color = ThemeColors.current["HIGHLIGHT_COLOR"]

    def on_release(self, *args):
        self.color = (1, 1, 1, 1)


class ExportScreen(BaseScreen):
    name = "export"
    scan_id = NumericProperty(0)

    format = StringProperty("csv")          # "csv" | "xlsx" | "pdf"
    headers = ListProperty([])
    header_labels = DictProperty({})

    # Temp-Preview-Verwaltung
    _temp_path = StringProperty("")
    _current_preview = ObjectProperty(None, allownone=True)
    _format_group = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_manager = ConfigManager()

    # ---------- Lifecycle ----------
    def on_pre_enter(self, *args):
        self._ensure_scan_and_headers()
        # Radios erst montieren, wenn KV geladen ist
        Clock.schedule_once(self._mount_format_radios, 0)
        # Vorschau aufbauen
        self._rebuild_preview_async()

    def on_leave(self, *args):
        self._cleanup_temp()

    def load_for_scan(self, scan_id: int):
        self.scan_id = int(scan_id or 0)
        self.reload_from_settings()

    # ---------- Routing ----------
    def open_settings(self, *_):
        """Wechselt zum Export-Settings-Screen (versucht mehrere mögliche Namen)."""
        sm = self.manager or getattr(App.get_running_app(), "root", None)
        if not sm:
            print("[ExportScreen] Kein ScreenManager gefunden.")
            return
        candidate_names = [
            "export_settings", "export-settings", "export_settings_screen", "ExportSettingsScreen"
        ]
        for name in candidate_names:
            try:
                sc = sm.get_screen(name)
                if sc:
                    sm.current = name
                    return
            except Exception:
                continue
        print("[ExportScreen] export_settings Screen nicht gefunden. Prüfe den Screen-Namen.")

    # ---------- Daten laden ----------
    def reload_from_settings(self):
        props = self.config_manager.get_export_properties()
        enabled_props = [p for p in props if int(p.get("enabled", 0)) == 1]
        enabled_props.sort(key=lambda x: int(x.get("order", 999)))
        self.headers = [p["key"] for p in enabled_props]
        self.header_labels = {p["key"]: p["label"] for p in enabled_props}
        self._rebuild_preview_async()

    def _ensure_scan_and_headers(self):
        if not int(self.scan_id or 0):
            sm = self.manager
            if sm:
                dev = None
                try:
                    dev = sm.get_screen("geräte")
                except Exception:
                    for sc in sm.screens:
                        if sc.__class__.__name__ == "DevicesScreen":
                            dev = sc
                            break
                if dev and int(getattr(dev, "scan_id", 0)):
                    self.scan_id = int(dev.scan_id)

        if not self.headers:
            storage = DatabaseStorage()
            try:
                props = storage.get_export_properties()
            except Exception:
                props = []
            self.headers = [p["key"] for p in props if int(p.get("enabled", 0)) == 1]
            self.header_labels = {p["key"]: p.get("label", p["key"]) for p in props}

        if not self.headers:
            self.headers = ["object-name", "device_id", "address_port"]
            self.header_labels.update({
                "object-name": "Name",
                "device_id": "Geräteinstanznr.",
                "address_port": "Adresse + Port",
            })

    # ---------- Vorschau aufbauen ----------
    def on_format(self, *_):
        self._rebuild_preview_async()

    def _rebuild_preview_async(self):
        Clock.schedule_once(lambda dt: self._rebuild_preview(), 0)

    def _rebuild_preview(self):
        self._ensure_scan_and_headers()

        storage = DatabaseStorage()
        rows = build_rows_for_scan(int(self.scan_id), self.headers, storage)

        # Temp-Datei erzeugen
        tmp_dir = os.path.join("data", "tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_name = f"preview_scan_{self.scan_id}.{self._ext_for_format()[1:]}"
        tmp_path = os.path.join(tmp_dir, tmp_name)

        try:
            if self.format == "csv":
                export_csv(tmp_path, rows, self.headers, self.header_labels)
            elif self.format == "xlsx":
                export_xlsx(tmp_path, rows, self.headers, self.header_labels)
            elif self.format == "pdf":
                export_pdf(
                    tmp_path,
                    rows,
                    self.headers,
                    self.header_labels,
                    title=f"Geräteliste – Scan {self.scan_id}",
                    landscape_mode=True,
                    logo_path="assets/siemens_logo.svg",
                    user_info=None,
                    user_settings_path="config/user_settings.json",
                )
            self._temp_path = tmp_path
        except Exception as e:
            print(f"[ExportScreen] Temp-Vorschau fehlgeschlagen: {e}")
            self._temp_path = ""

        # Vorschau-Widget einsetzen
        host = self.ids.get("preview_host")
        if not host:
            print("[ExportScreen] preview_host nicht gefunden.")
            return
        host.clear_widgets()
        self._current_preview = None

        if self.format == "pdf" and self._temp_path:
            pv = PdfPreview(fit_to_width=True)
            host.add_widget(pv)
            self._current_preview = pv
            pv.source = self._temp_path
        elif self.format in ("csv", "xlsx") and self._temp_path:
            sp = SpreadsheetPreview(filetype=self.format)
            host.add_widget(sp)
            self._current_preview = sp
            sp.source = self._temp_path
        else:
            from kivy.uix.label import Label
            host.add_widget(Label(text="Keine Vorschau verfügbar.", color=colors.TEXT_COLOR))

    # ---------- Export ----------
    def export_now(self):
        self._ensure_scan_and_headers()

        storage = DatabaseStorage()
        rows = build_rows_for_scan(int(self.scan_id), self.headers, storage)
        if not rows:
            print("Keine Daten zu exportieren.")
            return

        ext = self._ext_for_format()
        suggested = self._suggest_filename()
        start_dir = self._get_last_dir()

        try:
            from plyer import filechooser
            sel = filechooser.save_file(
                title="Speichern unter…",
                path=os.path.join(start_dir, suggested),
                filters=[("Dateien", f"*{ext}")]
            )
            if not sel:
                print("[Export] Nutzer hat abgebrochen.")
                return
            chosen = sel if isinstance(sel, str) else sel[0]
            if os.path.isdir(chosen):
                chosen = os.path.join(chosen, suggested)
            if not chosen.lower().endswith(ext):
                chosen += ext

            if self.format == "csv":
                export_csv(chosen, rows, self.headers, self.header_labels)
            elif self.format == "xlsx":
                export_xlsx(chosen, rows, self.headers, self.header_labels)
            elif self.format == "pdf":
                export_pdf(
                    chosen, rows, self.headers, self.header_labels,
                    title=f"Geräteliste – Scan {self.scan_id}", landscape_mode=True,
                    logo_path="assets/siemens_logo.svg",
                    user_info=None, user_settings_path="config/user_settings.json"
                )

            self._save_last_dir(os.path.dirname(chosen) or ".")
            self._cleanup_temp()
            print(f"Export fertig: {chosen}")

        except Exception as e:
            print(f"Speichern fehlgeschlagen: {e}")

    # ---------- Radio-Gruppe ----------
    def _mount_format_radios(self, *_):
        box = self.ids.get("format_group_container")
        if not box:
            print("[ExportScreen] format_group_container nicht gefunden.")
            return

        box.clear_widgets()
        label_for = {"csv": "CSV", "xlsx": "Excel (XLSX)", "pdf": "PDF"}
        options = [label_for["csv"], label_for["xlsx"], label_for["pdf"]]
        selected_label = label_for.get(self.format, "CSV")

        grp = RadioButtonGroup(
            options=options,
            selected=selected_label,
            group_name="export_format",
            on_selection_changed=self._on_format_selected,
        )
        grp.orientation = "horizontal"
        grp.spacing = dp(12)
        grp.size_hint_x = 1
        grp.size_hint_y = None
        grp.bind(minimum_height=grp.setter("height"))

        box.add_widget(grp)
        self._format_group = grp
        Clock.schedule_once(self._fix_radio_children_sizes, 0)

    def _fix_radio_children_sizes(self, *_):
        grp = self._format_group
        if not grp:
            return
        for child in grp.children:
            if not isinstance(child, SimpleRadioButton):
                continue
            lbl = getattr(child, "label", None)
            icon_box = getattr(child, "radio_image_container", None)
            if lbl:
                lbl.texture_update()
                text_w = lbl.texture_size[0]
            else:
                text_w = dp(40)
            icon_w = icon_box.width if icon_box else dp(20)
            child.size_hint_x = None
            child.width = dp(12) + icon_w + child.spacing + text_w + dp(12)
            child.size_hint_y = None
            child.height = dp(30)

    def _on_format_selected(self, label: str):
        mapping = {"CSV": "csv", "Excel (XLSX)": "xlsx", "PDF": "pdf"}
        new_fmt = mapping.get(label, "csv")
        if new_fmt != self.format:
            self.format = new_fmt

    # ---------- Misc ----------
    def _ext_for_format(self) -> str:
        return ".csv" if self.format == "csv" else ".xlsx" if self.format == "xlsx" else ".pdf"

    def _suggest_filename(self) -> str:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"scan_{self.scan_id}_{ts}{self._ext_for_format()}"

    def _get_last_dir(self) -> str:
        try:
            os.makedirs("data", exist_ok=True)
            path = "data/last_export_dir.txt"
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    d = f.read().strip()
                    if d and os.path.isdir(d):
                        return d
        except Exception:
            pass
        try:
            app = App.get_running_app()
            if hasattr(app, "user_data_dir") and os.path.isdir(app.user_data_dir):
                return app.user_data_dir
        except Exception:
            pass
        return os.getcwd()

    def _save_last_dir(self, d: str):
        try:
            os.makedirs("data", exist_ok=True)
            with open("data/last_export_dir.txt", "w", encoding="utf-8") as f:
                f.write(d)
        except Exception:
            pass

    def _cleanup_temp(self):
        p = getattr(self, "_temp_path", "")
        if p and os.path.isfile(p):
            try:
                os.remove(p)
                print(f"[ExportScreen] Temp gelöscht: {p}")
            except Exception:
                pass
        self._temp_path = ""


# KV laden
Builder.load_file('ui/screens/export_screen.kv')
