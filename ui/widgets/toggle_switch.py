from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty
from kivy.lang import Builder
from ui.utils import get_resource_path
from core.events import event_bus
from ui.styles.colors import ThemeColors

# KV-Datei laden
Builder.load_file('ui/widgets/toggle_switch.kv')

class ToggleSwitch(BoxLayout):
    """Ein Ein/Aus-Schalter mit Text"""
    text = StringProperty('')
    active = BooleanProperty(False)
    bg_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    switch_color = ListProperty([0.2, 0.6, 0.9, 1])
    on_toggle = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ToggleSwitch, self).__init__(**kwargs)
        self.update_colors()
        event_bus.bind(on_theme_changed=self.on_theme_changed)
    
    def update_colors(self):
        """Aktualisiert die Farben basierend auf dem aktuellen Theme"""
        self.bg_color = ThemeColors.current["CARD_BACKGROUND"]
        self.text_color = ThemeColors.current["TEXT_COLOR"]
        self.switch_color = ThemeColors.current["HIGHLIGHT_COLOR"]
    
    def toggle(self):
        """Schaltet den Toggle-Switch um"""
        self.active = not self.active
        
        # Callback auslösen, falls vorhanden
        if self.on_toggle:
            self.on_toggle(self.active)
    
    def on_theme_changed(self, instance, theme_name):
        """Bei Theme-Änderung aktualisieren"""
        self.update_colors()