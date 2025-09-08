# ui/screens/export_settings_screen.py
from typing import List, Dict, Any
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.app import App

from ui.screens.base_screen import BaseScreen
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
        for f in self.fields:
            row = FieldRow(key=f["key"], label=f["label"], enabled=f["enabled"], order_index=f["order_index"])
            # dynamisch UI bauen:
            from kivy.uix.checkbox import CheckBox
            from kivy.uix.label import Label
            from kivy.uix.boxlayout import BoxLayout
            line = BoxLayout(orientation='horizontal', size_hint_y=None, height=32, spacing=8)
            cb = CheckBox(active=bool(int(f["enabled"])))
            def _on_active(inst, key=f["key"]):
                for ff in self.fields:
                    if ff["key"] == key:
                        ff["enabled"] = 1 if inst.active else 0
                        break
            cb.bind(active=_on_active)
            line.add_widget(cb)
            line.add_widget(Label(text=f["label"], halign='left', valign='middle', color=App.get_running_app().root.theme_colors.TEXT_COLOR, text_size=(0,0)))
            line.add_widget(Label(text=f["key"], halign='left', valign='middle', color=App.get_running_app().root.theme_colors.TEXT_COLOR, text_size=(0,0)))
            cont.add_widget(line)

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
