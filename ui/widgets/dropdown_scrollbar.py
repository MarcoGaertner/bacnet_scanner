import os
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ListProperty, ObjectProperty, BooleanProperty
from kivy.lang import Builder
from ui.utils import get_resource_path
from kivy.clock import Clock
from core.events import event_bus
from kivy.graphics import Color, Rectangle
from ui.styles.colors import ThemeColors

try:
    kv_path = os.path.join(os.path.dirname(__file__), 'dropdown_scrollbar.kv')
    Builder.load_file(kv_path)
    print("DEBUG: dropdown_scrollbar.kv erfolgreich geladen.")
except Exception as e:
    print(f"FATALER FEHLER: Konnte dropdown_scrollbar.kv nicht laden: {e}")


class ScrollableCustomDropDown(DropDown):
    """Theme-unterstützendes Dropdown mit ScrollView."""
    bg_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])

    def __init__(self, **kwargs):
        super(ScrollableCustomDropDown, self).__init__(**kwargs)
        
        # Wir erstellen unsere ScrollView
        self.scroll_view = ScrollView(size_hint_y=None)
        
        # Erstellen eines eigenen Containers für unsere Items
        self.custom_container = GridLayout(cols=1, size_hint_y=None)
        self.custom_container.bind(minimum_height=self.custom_container.setter('height'))
        
        # Füge den benutzerdefinierten Container zur ScrollView hinzu
        self.scroll_view.add_widget(self.custom_container)
        
        # Füge die ScrollView zum DropDown hinzu
        super(ScrollableCustomDropDown, self).add_widget(self.scroll_view)
        
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        self.bind(on_open=self.update_dropdown_layout)
        self.update_colors()
        
        # Debug-Ausgabe
        print(f"DEBUG: ScrollableCustomDropDown initialisiert")

    def add_widget(self, widget, *args, **kwargs):
        """Überschreibe add_widget, um Elemente dem benutzerdefinierten Container hinzuzufügen."""
        if isinstance(widget, ScrollView):
            # Wenn es sich um unsere eigene ScrollView handelt, füge sie direkt zum DropDown hinzu
            super(ScrollableCustomDropDown, self).add_widget(widget, *args, **kwargs)
        elif hasattr(self, 'custom_container') and self.custom_container is not None:
            # Füge das Widget zum benutzerdefinierten Container hinzu
            self.custom_container.add_widget(widget)
        else:
            # Fallback: Füge direkt zum DropDown hinzu
            super(ScrollableCustomDropDown, self).add_widget(widget, *args, **kwargs)

    def update_colors(self):
        self.bg_color = ThemeColors.current["CARD_BACKGROUND"]
        self.text_color = ThemeColors.current["TEXT_COLOR"]

    def update_dropdown_layout(self, *args):
        # Aktualisiere die Höhe der ScrollView basierend auf der Mindesthöhe des Containers
        max_height = self.get_max_height()
        if self.custom_container and self.custom_container.children:
            self.scroll_view.height = min(self.custom_container.minimum_height, max_height)
        Clock.schedule_once(self._update_container_color, 0)

    def _update_container_color(self, dt):
        if hasattr(self, '_dropdown_window') and self._dropdown_window:
            # Färbe den Hintergrund der ScrollView
            with self.scroll_view.canvas.before:
                Color(*self.bg_color)
                Rectangle(pos=self.scroll_view.pos, size=self.scroll_view.size)
            
            # Und die Items im Grid
            for child in self.custom_container.children:
                if isinstance(child, ScrollableSettingsDropdownItem):
                    child.update_colors()

    def on_theme_changed(self, instance, theme_name):
        self.update_colors()
        if self.attach_to:
            self.update_dropdown_layout()
    
    def get_max_height(self):
        if self.custom_container and self.custom_container.children:
            return self.custom_container.children[0].height * 5.5


class ScrollableSettingsDropdownItem(Button):
    """Button-Item für das scrollbare Dropdown-Menü."""
    bg_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])

    def __init__(self, **kwargs):
        super(ScrollableSettingsDropdownItem, self).__init__(**kwargs)
        self.update_colors()
        event_bus.bind(on_theme_changed=self.on_theme_changed)

    def update_colors(self):
        self.bg_color = ThemeColors.current["CARD_BACKGROUND"]
        self.text_color = ThemeColors.current["TEXT_COLOR"]
        self.canvas.ask_update()

    def on_theme_changed(self, instance, theme_name):
        self.update_colors()


class ScrollableNestedDropdown(BoxLayout):
    """Verschachteltes, scrollbares Dropdown-Menü mit Theme-Support."""
    title = StringProperty('')
    options = ListProperty([])
    current_value = StringProperty('')
    on_select = ObjectProperty(None)
    is_open = BooleanProperty(False)

    bg_color = ListProperty([1, 1, 1, 1])
    button_bg_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    border_color = ListProperty([0, 0, 0, 0.3])
    arrow_color = ListProperty([0, 0, 0, 1])

    def __init__(self, **kwargs):
        super(ScrollableNestedDropdown, self).__init__(**kwargs)
        self.dropdown = ScrollableCustomDropDown()
        print(f"DEBUG: Dropdown '{self.title}' initialisiert mit {len(self.options)} Optionen")
        Clock.schedule_once(self._setup_dropdown, 0.1)
        event_bus.bind(on_theme_changed=self.on_theme_changed)

    def _setup_dropdown(self, dt):
        # Leere den Container, falls er bereits Elemente enthält
        if hasattr(self.dropdown, 'custom_container') and self.dropdown.custom_container is not None:
            self.dropdown.custom_container.clear_widgets()
        
        self.dropdown.bind(on_dismiss=self.on_dropdown_dismiss)
        self.update_colors()

        for option in self.options:
            item = ScrollableSettingsDropdownItem(text=option)
            # WICHTIG: Verwende eine Closure, um den aktuellen Wert von option zu speichern
            def create_release_callback(opt):
                return lambda instance: self.dropdown.select(opt)
            
            item.bind(on_release=create_release_callback(option))
            self.dropdown.add_widget(item)  # Diese Zeile verwendet unsere überschriebene add_widget-Methode

        self.dropdown.bind(on_select=self.on_dropdown_select)

    def on_dropdown_dismiss(self, instance):
        self.is_open = False

    def update_colors(self):
        self.bg_color = ThemeColors.current["CARD_BACKGROUND"]
        self.button_bg_color = ThemeColors.current["SIDEBAR_BACKGROUND"]
        self.text_color = ThemeColors.current["TEXT_COLOR"]
        text_color = ThemeColors.current["TEXT_COLOR"]
        self.border_color = (text_color[0], text_color[1], text_color[2], 0.3)
        self.arrow_color = ThemeColors.current["TEXT_COLOR"]
        self.canvas.ask_update()

    def open_dropdown(self, button):
        print(f"DEBUG: Öffne Dropdown '{self.title}' mit {len(self.options)} Optionen")
        # Dropdown nur öffnen, wenn Optionen vorhanden sind
        if self.options:
            self.dropdown.open(button)
            self.is_open = True

    def on_dropdown_select(self, instance, value):
        print(f"DEBUG: '{value}' aus Dropdown '{self.title}' ausgewählt")
        self.current_value = value
        if self.on_select:
            self.on_select(value)

    def on_theme_changed(self, instance, theme_name):
        self.update_colors()