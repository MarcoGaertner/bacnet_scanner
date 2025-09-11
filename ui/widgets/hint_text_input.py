from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, ListProperty, BooleanProperty
from kivy.lang import Builder
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from core.events import event_bus
from ui.styles.colors import ThemeColors

Builder.load_file('ui/widgets/hint_text_input.kv')

class HintTextInput(TextInput):
    """TextInput mit Platzhaltertext und Farbwechsel"""
    hint_text = StringProperty('')
    active_color = ListProperty([1, 1, 1, 1])
    inactive_color = ListProperty([0.7, 0.7, 0.7, 1])
    is_focused = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(HintTextInput, self).__init__(**kwargs)
        self._is_empty = not bool(self.text)
        
        # Entferne alle Standard-Hintergründe
        self.background_normal = ''
        self.background_active = ''
        self.background_disabled_normal = ''
        
        self.update_colors()
        self.foreground_color = self.inactive_color if self._is_empty else self.active_color
        
        self.bind(text=self.on_text_changed)
        self.bind(focus=self.on_focus_changed)
        self.bind(pos=self.update_canvas)
        self.bind(size=self.update_canvas)
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        
        # Initialer Canvas-Aufbau
        self.update_canvas()

    def update_colors(self):
        """Aktualisiert die Farben basierend auf dem aktuellen Theme"""
        self.cursor_color = ThemeColors.current["TEXT_COLOR"]
        self.active_color = ThemeColors.current["TEXT_COLOR"]
        self.inactive_color = [
            ThemeColors.current["TEXT_COLOR"][0] * 0.7,
            ThemeColors.current["TEXT_COLOR"][1] * 0.7,
            ThemeColors.current["TEXT_COLOR"][2] * 0.7,
            ThemeColors.current["TEXT_COLOR"][3]
        ]
        
        # Setze auch die hint_text_color programmatisch
        self.hint_text_color = [
            ThemeColors.current["TEXT_COLOR"][0] * 0.5,
            ThemeColors.current["TEXT_COLOR"][1] * 0.5,
            ThemeColors.current["TEXT_COLOR"][2] * 0.5,
            0.8  # Leicht transparent
        ]
        
        # WICHTIG: Setze die Textfarbe explizit
        self.foreground_color = self.inactive_color if self._is_empty else self.active_color
        
        # Debug: Ausgabe der Farben
        print(f"DEBUG: Text leer: {self._is_empty}")
        print(f"DEBUG: Active color: {self.active_color}")
        print(f"DEBUG: Inactive color: {self.inactive_color}")
        print(f"DEBUG: Foreground color: {self.foreground_color}")
        print(f"DEBUG: Hint color: {self.hint_text_color}")
        
        # Canvas neu zeichnen
        self.update_canvas()
        
        # Canvas neu zeichnen
        self.update_canvas()
    
    def update_canvas(self, *args):
        """Aktualisiert das Canvas für Hintergrund und Rahmen"""
        self.canvas.before.clear()
        
        border_width = dp(2)
        radius = dp(6)
        
        with self.canvas.before:
            # Rahmen: Äußeres Rechteck in Rahmenfarbe
            if self.is_focused:
                Color(*ThemeColors.current["HIGHLIGHT_COLOR"])
            else:
                Color(*ThemeColors.current["SIDEBAR_BACKGROUND"])
            
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[radius, radius, radius, radius]
            )
            
            # Hintergrund: Inneres Rechteck in Hintergrundfarbe
            Color(*ThemeColors.current["TAB_BACKGROUND"])
            RoundedRectangle(
                pos=(self.x + border_width, self.y + border_width),
                size=(self.width - 2*border_width, self.height - 2*border_width),
                radius=[max(0, radius-border_width)] * 4
            )

    def on_text_changed(self, instance, value):
        """Wird aufgerufen, wenn sich der Text ändert"""
        is_empty_now = not bool(value)
        if self._is_empty != is_empty_now:
            self._is_empty = is_empty_now
            # Aktualisiere die Textfarbe sofort
            self.foreground_color = self.inactive_color if is_empty_now else self.active_color
            print(f"DEBUG: Text geändert zu: '{value}', leer: {is_empty_now}, Farbe: {self.foreground_color}")
    
    def on_focus_changed(self, instance, is_focused):
        """Wird aufgerufen, wenn sich der Fokus-Zustand ändert"""
        self.is_focused = is_focused
        self.update_canvas()
        # Stelle sicher, dass die Textfarbe korrekt ist
        self.foreground_color = self.inactive_color if self._is_empty else self.active_color
        print(f"DEBUG: Fokus geändert zu: {is_focused}, Textfarbe: {self.foreground_color}")
    
    def on_theme_changed(self, instance, theme_name):
        """Wird aufgerufen, wenn sich das Theme ändert"""
        self.update_colors()