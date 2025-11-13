# ui/screens/export_settings_screen.py
from typing import List, Dict, Any, Optional
from kivy.lang import Builder
from ui.utils import get_resource_path
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.app import App

from ui.screens.base_screen import BaseScreen
from ui.styles import colors
from core.config import ConfigManager  # Geändert von DatabaseStorage


class FieldRow(BoxLayout):
    key = ""
    def __init__(self, key: str, label: str, enabled: bool, order_index: int, **kwargs):
        super().__init__(**kwargs)
        self.key = key
        self.label = label
        self.enabled = bool(int(enabled))
        self.order_index = order_index


class ExportSettingsScreen(BaseScreen):
    name = "export_settings"
    fields = ListProperty([])  # [{'key','label','enabled','order_index'}, ...]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_manager = ConfigManager()

    # ---------- Lifecycle ----------
    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.load_fields()

    # ---------- Daten laden/Render ----------
    def load_fields(self):
        self.fields = self.config_manager.get_export_properties()
        self._render()

    def _render(self):
        cont = self.ids.get("fields_container")
        if not cont:
            return
        cont.clear_widgets()

        from kivy.uix.checkbox import CheckBox
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.metrics import dp

        for idx, f in enumerate(self.fields):
            line = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(36),
                spacing=dp(8),
            )

            # 1) Aktiv Checkbox – feste Breite
            cb = CheckBox(
                active=bool(int(f.get("enabled", 0))),
                size_hint_x=None,
                width=dp(28),
            )
            cb.bind(active=lambda inst, val, i=idx: self._on_field_enabled_changed(i, val))
            line.add_widget(cb)

            # 2) Feldname
            lbl_label = Label(
                text=str(f.get("label", "")),
                halign='left',
                valign='middle',
                color=colors.TEXT_COLOR,
                size_hint_x=0.6,
            )
            line.add_widget(lbl_label)

            # 3) Key
            lbl_key = Label(
                text=str(f.get("key", "")),
                halign='left',
                valign='middle',
                color=colors.TEXT_COLOR,
                size_hint_x=0.4,
            )
            line.add_widget(lbl_key)

            cont.add_widget(line)

    # ---------- Feld-Callbacks ----------
    def _on_field_enabled_changed(self, index: int, active: bool):
        if 0 <= index < len(self.fields):
            self.fields[index]["enabled"] = 1 if active else 0

    def _on_field_label_changed(self, index: int, value: str):
        if 0 <= index < len(self.fields):
            self.fields[index]["label"] = value

    def _on_field_key_changed(self, index: int, value: str):
        if 0 <= index < len(self.fields):
            self.fields[index]["key"] = value

    # ---------- Navigation-Helper ----------
    @staticmethod
    def _find_screen_manager(widget) -> Optional["ScreenManager"]:
        """Suche rekursiv den ScreenManager im Widget-Baum."""
        try:
            from kivy.uix.screenmanager import ScreenManager
        except Exception:
            return None

        if widget is None:
            return None
        if isinstance(widget, ScreenManager):
            return widget
        for ch in getattr(widget, "children", []):
            found = ExportSettingsScreen._find_screen_manager(ch)
            if found:
                return found
        return None

    def _get_screen_manager(self):
        # 1) Bevorzugt den 'echten' Manager dieses Screens
        if getattr(self, "manager", None):
            return self.manager
        # 2) Fallback: in App.root (BoxLayout) nach einem ScreenManager suchen
        root = getattr(App.get_running_app(), "root", None)
        sm = self._find_screen_manager(root)
        if not sm:
            print("[ExportSettings] Kein ScreenManager im Widget-Baum gefunden.")
        return sm

    # ---------- Speichern + zurück zum Export ----------
    def save_and_back(self):
        # 1) Speichern
        try:
            self.config_manager.set_export_properties(self.fields)
            print("[ExportSettings] Export-Properties gespeichert.")
        except Exception as e:
            print(f"[ExportSettings] Speichern fehlgeschlagen: {e}")

        # 2) ScreenManager ermitteln
        sm = self._get_screen_manager()
        if not sm:
            # Wenn gar kein SM gefunden wurde, einfach hier enden (aber nicht crashen)
            return

        # 3) ExportScreen finden
        exp = None
        try:
            exp = sm.get_screen("export")
        except Exception:
            # Falls der Name anders ist, durchiterieren
            for s in getattr(sm, "screens", []):
                if s.__class__.__name__ in ("ExportScreen",):
                    exp = s
                    break

        # 4) ExportScreen aktualisieren + navigieren
        if exp:
            try:
                exp.reload_from_settings()
            except Exception as e:
                print(f"[ExportSettings] reload_from_settings() auf ExportScreen fehlgeschlagen: {e}")
            try:
                sm.current = "export" if getattr(exp, "name", "") == "export" else exp.name
            except Exception as e:
                print(f"[ExportSettings] Navigation zu ExportScreen fehlgeschlagen: {e}")
        else:
            print("[ExportSettings] Konnte ExportScreen nicht finden – Navigation übersprungen.")


# KV laden
Builder.load_file('ui/screens/export_settings_screen.kv')
