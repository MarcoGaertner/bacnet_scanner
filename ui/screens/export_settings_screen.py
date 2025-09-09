# ui/screens/export_settings_screen.py
from typing import List, Dict, Any
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.app import App

from ui.screens.base_screen import BaseScreen

from ui.styles import colors
from scanner.storage import DatabaseStorage

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

    def load_fields(self):
        st = DatabaseStorage()
        self.fields = st.get_export_properties()
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

            # 2) Feldname (Label) – editierbar
            lbl_label = Label(
                text=str(f.get("label", "")),
                halign='left',
                valign='middle',
                color=colors.TEXT_COLOR,
                size_hint_x=0.6,      # 60% der Breite
            )
            line.add_widget(lbl_label)
            
            
            # 3) Key – editierbar
            lbl_key = Label(
                text=str(f.get("key", "")),
                halign='left',
                valign='middle',
                color=colors.TEXT_COLOR,
                size_hint_x=0.4,      # 40% der Breite
            )
            line.add_widget(lbl_key)

            cont.add_widget(line)

    # Hilfs-Callbacks: robust über Index statt "key" matchen
    def _on_field_enabled_changed(self, index: int, active: bool):
        if 0 <= index < len(self.fields):
            self.fields[index]["enabled"] = 1 if active else 0

    def _on_field_label_changed(self, index: int, value: str):
        if 0 <= index < len(self.fields):
            self.fields[index]["label"] = value

    def _on_field_key_changed(self, index: int, value: str):
        if 0 <= index < len(self.fields):
            self.fields[index]["key"] = value


    def save_and_back(self):
        st = DatabaseStorage()
        st.set_export_properties(self.fields)
        # zurück zum ExportScreen und Vorschau aktualisieren
        sm = App.get_running_app().root
        try:
            exp = sm.get_screen("export")
        except Exception:
            exp = None
            for s in sm.screens:
                if s.__class__.__name__ in ("ExportScreen",):
                    exp = s
                    break
        if exp:
            exp.reload_from_settings()
        sm.current = "export"

Builder.load_file('ui/screens/export_settings_screen.kv')
