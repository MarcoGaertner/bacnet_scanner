from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ListProperty, NumericProperty
from kivy.lang import Builder
from ui.utils import get_resource_path
from core.events import event_bus
from ui.styles.colors import ThemeColors
from kivy.clock import Clock
from kivy.metrics import dp

# KV-Datei laden
Builder.load_file('ui/widgets/expandable_panel.kv')

class ExpandablePanel(BoxLayout):
    """Ein ausklappbares Panel für verschiedene Einstellungen"""
    title = StringProperty("")
    is_expanded = BooleanProperty(False)
    bg_color = ListProperty([1, 1, 1, 1])
    text_color = ListProperty([0, 0, 0, 1])
    # Höhe des Kopfbereichs (Titelzeile)
    header_height = NumericProperty(40)
    # Spacing zwischen Header und Content
    panel_spacing = NumericProperty(5)

    def __init__(self, **kwargs):
        # Unterstützung für verschiedene Parameter für den Expansionszustand
        # Prüfe und verarbeite die verschiedenen möglichen Parameter
        if 'expanded' in kwargs:
            self.is_expanded = kwargs.pop('expanded')
        elif 'initial_expanded' in kwargs:
            self.is_expanded = kwargs.pop('initial_expanded')
        
        super(ExpandablePanel, self).__init__(**kwargs)
        self.update_colors()
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        Clock.schedule_once(self._initialize_panel, 0.1)
    
    def update_colors(self):
        """Aktualisiert die Farben basierend auf dem aktuellen Theme"""
        self.bg_color = ThemeColors.current["CARD_BACKGROUND"]
        self.text_color = ThemeColors.current["TEXT_COLOR"]

    def _initialize_panel(self, dt):
        """Initialisiert das Panel mit dem korrekten Zustand"""
        self._update_panel_state(self.is_expanded)
    
    def toggle_expansion(self):
        """Klappt das Panel aus oder ein"""
        old_state = self.is_expanded
        new_state = not old_state
        print(f"BUTTON CLICKED: Panel '{self.title}' - Status ändern von {old_state} zu {new_state}")

        self.is_expanded = new_state
        Clock.schedule_once(lambda dt: self._update_panel_state(self.is_expanded), 0)

    def get_arrow_points(self, center_x, center_y):
        """Berechnet die Punkte für das Dreieck (Pfeil)"""
        dp_value = 5  # Größe des Pfeils
        if self.is_expanded:
            # Nach oben zeigender Pfeil
            return [
                center_x + dp_value, center_y - dp_value, 
                center_x - dp_value, center_y - dp_value, 
                center_x, center_y + dp_value
            ]
        else:
            # Nach unten zeigender Pfeil
            return [
                center_x + dp_value, center_y + dp_value, 
                center_x - dp_value, center_y + dp_value, 
                center_x, center_y - dp_value
            ]
        
    def on_theme_changed(self, instance, theme_name):
        """Wird aufgerufen, wenn sich das Theme ändert"""
        self.update_colors()
        self.canvas.ask_update()

    def _update_panel_state(self, expanded):
        """Aktualisiert den UI-Zustand des Panels basierend auf dem expanded-Wert"""
        if hasattr(self, 'ids') and 'content' in self.ids:
            # Setze Eigenschaften direkt
            content = self.ids.content
            
            # Berechne die alte Höhe für die Differenz
            old_height = self.height
            
            if expanded:
                # Wenn das Panel geöffnet wird
                content.opacity = 1
                content.disabled = False
                
                # Setze die Höhe auf minimum_height
                content.height = content.minimum_height
                
                # Gesamthöhe des Panels = Header + Spacing + Content
                self.height = self.header_height + self.panel_spacing + content.height
            else:
                # Wenn das Panel geschlossen wird
                content.opacity = 0
                content.disabled = True
                content.height = 0
                
                # Gesamthöhe des Panels = nur Header
                self.height = self.header_height
            
            # Berechne die Höhendifferenz
            height_diff = self.height - old_height
            
            # Benachrichtige den Container, dass sich die Größe geändert hat
            if self.parent:
                # Aktualisiere die Höhe des übergeordneten Containers
                if hasattr(self.parent, 'minimum_height'):
                    self.parent.height = self.parent.minimum_height
                
                # Verschiebe alle nachfolgenden Widgets nach unten/oben
                if height_diff != 0:
                    # Finde die Position dieses Panels in der Liste der Kinder
                    try:
                        index = self.parent.children.index(self)
                        # Widgets in Kivy sind in umgekehrter Reihenfolge (von unten nach oben)
                        # Daher müssen wir nur die Widgets mit niedrigerem Index verschieben
                        for i in range(index):
                            child = self.parent.children[i]
                            child.y -= height_diff
                    except ValueError:
                        pass
                
                # Scrollview-Aktualisierung (wenn vorhanden)
                if hasattr(self.parent, 'parent') and self.parent.parent:
                    if hasattr(self.parent.parent, 'scroll_y'):
                        self.parent.parent.do_scroll_y = True

    def on_touch_down(self, touch):
        """Prüft, ob ein Klick im Header-Bereich erfolgt ist"""
        # Bereich des Headers berechnen
        header_y = self.y + self.height - self.header_height
        if (self.collide_point(touch.x, touch.y) and 
            touch.y >= header_y and 
            touch.y <= header_y + self.header_height):
            
            print(f"DEBUG: Klick im Header von '{self.title}' erkannt")
            self.toggle_expansion()
            return True
        
        # Wenn das Panel nicht geöffnet ist, leite den Touch nicht an die Kinder weiter
        if not self.is_expanded:
            return super(ExpandablePanel, self).on_touch_down(touch)
        
        # Wenn das Panel geöffnet ist und der Klick im Inhaltsbereich ist
        content_y = self.y
        content_height = self.height - self.header_height - self.panel_spacing
        if (self.collide_point(touch.x, touch.y) and 
            touch.y >= content_y and 
            touch.y <= content_y + content_height):
            
            # Leite den Touch an die Kinder weiter
            for child in self.children:
                if child.collide_point(touch.x, touch.y):
                    if child.dispatch('on_touch_down', touch):
                        return True
        
        return super(ExpandablePanel, self).on_touch_down(touch)

    def add_content(self, widget):
        """Fügt ein Widget zum Inhalt des Panels hinzu"""
        if hasattr(self, 'ids') and 'content' in self.ids:
            self.ids.content.add_widget(widget)
            # Aktualisiere die Höhe des Panels
            Clock.schedule_once(lambda dt: self._update_panel_state(self.is_expanded), 0)