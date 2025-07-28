from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder
from core.events import event_bus
from ui.styles.colors import ThemeColors

Builder.load_file('ui/widgets/hint_text_input.kv')

class HintTextInput(TextInput):
    """TextInput mit Platzhaltertext und Farbwechsel"""
    hint_text = StringProperty('')
    active_color = ListProperty([1, 1, 1, 1])
    inactive_color = ListProperty([0.7, 0.7, 0.7, 1])
    
    def __init__(self, **kwargs):
        super(HintTextInput, self).__init__(**kwargs)
        self._is_empty = not bool(self.text)
        self.update_colors()
        self.foreground_color = self.inactive_color if self._is_empty else self.active_color
        self.bind(text=self.on_text_changed)
        event_bus.bind(on_theme_changed=self.on_theme_changed)

    def update_colors(self):
        """Aktualisiert die Farben basierend auf dem aktuellen Theme"""
        self.background_color = ThemeColors.current["CARD_BACKGROUND"]
        self.cursor_color = ThemeColors.current["TEXT_COLOR"]
        self.active_color = ThemeColors.current["TEXT_COLOR"]
        self.inactive_color = [
            ThemeColors.current["TEXT_COLOR"][0] * 0.7,
            ThemeColors.current["TEXT_COLOR"][1] * 0.7,
            ThemeColors.current["TEXT_COLOR"][2] * 0.7,
            ThemeColors.current["TEXT_COLOR"][3]
        ]
        # Aktualisiere die Textfarbe basierend auf dem leeren Zustand
        self.foreground_color = self.inactive_color if self._is_empty else self.active_color
    
    def on_text_changed(self, instance, value):
        """Wird aufgerufen, wenn sich der Text ändert"""
        is_empty_now = not bool(value)
        if self._is_empty != is_empty_now:
            self._is_empty = is_empty_now
            self.foreground_color = self.inactive_color if is_empty_now else self.active_color
    
    def on_theme_changed(self, instance, theme_name):
        """Wird aufgerufen, wenn sich das Theme ändert"""
        self.update_colors()