from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.lang import Builder
from core.events import event_bus
from kivy.graphics import Color, Rectangle
from ui.styles.colors import ThemeColors

# Laden der externen KV-Datei
Builder.load_file('ui/widgets/dropdown.kv')

class CustomDropDown(DropDown):
    """Theme-unterstützendes Dropdown"""
    bg_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    
    def __init__(self, **kwargs):
        super(CustomDropDown, self).__init__(**kwargs)
        # Theme-Änderungen beobachten
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        # Container-Farbe setzen, wenn das Dropdown geöffnet wird
        self.bind(on_open=self.update_dropdown_container,)
        # Initial Farben setzen
        self.update_colors()
    
    def update_colors(self):
        """Aktualisiert die Farben basierend auf dem aktuellen Theme"""
        self.bg_color = ThemeColors.current["CARD_BACKGROUND"]
        self.text_color = ThemeColors.current["TEXT_COLOR"]
        
    def update_dropdown_container(self, *args):
        """Aktualisiert die Hintergrundfarbe des Dropdown-Containers"""
        # Warte einen Frame, um sicherzustellen, dass das Container-Widget existiert
        from kivy.clock import Clock
        Clock.schedule_once(self._update_container, 0)
    
    def _update_container(self, dt):
        """Aktualisiert das Container-Widget direkt"""
        if hasattr(self, '_dropdown_window') and self._dropdown_window:
            container = self._dropdown_window.children[0]
            with container.canvas.before:
                Color(*self.bg_color)  # Verwende die Property statt direkten Zugriff
                Rectangle(pos=container.pos, size=container.size)
            
            # Auch die Kind-Elemente aktualisieren
            for child in container.children:
                if isinstance(child, SettingsDropdownItem):
                    child.update_colors()
    
    def on_theme_changed(self, instance, theme_name):
        """Bei Theme-Änderung aktualisieren"""
        self.update_colors()
        # Wenn gerade geöffnet, Container neu zeichnen
        if self.attach_to:
            self.update_dropdown_container()

class SettingsDropdownItem(Button):
    """Button-Item für das Dropdown-Menü"""
    bg_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    
    def __init__(self, **kwargs):
        super(SettingsDropdownItem, self).__init__(**kwargs)
        self.update_colors()
        # Theme-Änderungen beobachten
        event_bus.bind(on_theme_changed=self.on_theme_changed)
    
    def update_colors(self):
        """Aktualisiert die Farben basierend auf dem aktuellen Theme"""
        self.bg_color = ThemeColors.current["CARD_BACKGROUND"]
        self.text_color = ThemeColors.current["TEXT_COLOR"]
        # Canvas aktualisieren
        self.canvas.ask_update()
    
    def on_theme_changed(self, instance, theme_name):
        """Bei Theme-Änderung aktualisieren"""
        self.update_colors()

class NestedDropdown(BoxLayout):
    """Verschachteltes Dropdown-Menü mit Theme-Support"""
    title = StringProperty('')
    options = ListProperty([])
    current_value = StringProperty('')
    on_select = ObjectProperty(None)
    is_open = BooleanProperty(False)
    
    # Dynamische Farben als Properties
    bg_color = ListProperty([1, 1, 1, 1])
    button_bg_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    border_color = ListProperty([0, 0, 0, 0.3])
    arrow_color = ListProperty([0, 0, 0, 1])
    
    def __init__(self, **kwargs):
        super(NestedDropdown, self).__init__(**kwargs)
        # Angepasstes Dropdown verwenden
        self.dropdown = CustomDropDown()

        # Schließereignisse beobachten
        self.dropdown.bind(on_dismiss=self.on_dropdown_dismiss)
        
        # Farben initialisieren
        self.update_colors()
        
        # Theme-Änderungen beobachten
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        
        # Dropdown-Items erstellen
        for option in self.options:
            item = SettingsDropdownItem(text=option)
            item.bind(on_release=lambda btn: self.dropdown.select(btn.text))
            self.dropdown.add_widget(item)
        
        # Dropdown-Auswahl binden
        self.dropdown.bind(on_select=self.on_dropdown_select)
    
    def on_dropdown_dismiss(self, instance):
        """Wird aufgerufen, wenn das Dropdown geschlossen wird"""
        self.is_open = False
    
    def update_colors(self):
        """Aktualisiert die Farben basierend auf dem aktuellen Theme"""
        self.bg_color = ThemeColors.current["CARD_BACKGROUND"]
        self.button_bg_color = ThemeColors.current["SIDEBAR_BACKGROUND"]
        self.text_color = ThemeColors.current["TEXT_COLOR"]
        # Transparente Version der Textfarbe für Rahmen
        text_color = ThemeColors.current["TEXT_COLOR"]
        self.border_color = (text_color[0], text_color[1], text_color[2], 0.3)
        self.arrow_color = ThemeColors.current["TEXT_COLOR"]
        # Canvas aktualisieren
        self.canvas.ask_update()
    
    def open_dropdown(self, button):
        self.dropdown.open(button)
        # Manuell den Status setzen und Logging auslösen
        self.is_open = True
    
    def on_dropdown_select(self, instance, value):
        self.current_value = value
        if self.on_select:
            self.on_select(value)
    
    def on_theme_changed(self, instance, theme_name):
        """Bei Theme-Änderung aktualisieren"""
        self.update_colors()