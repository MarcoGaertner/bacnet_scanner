from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, ListProperty
from kivy.lang import Builder
from core.events import event_bus
from ui.styles.colors import ThemeColors
from os.path import join, dirname, abspath
from core.i18n.translator import _

# Basisverzeichnis für Assets definieren
ASSETS_DIR = join(dirname(dirname(dirname(abspath(__file__)))), 'assets')
ICONS_DIR = join(ASSETS_DIR, 'icons')

Builder.load_file('ui/widgets/sidebar.kv')

class TabButton(Button):
    """Button für einen Tab in der Seitenleiste"""
    icon = StringProperty('')  # Behalten für Kompatibilität
    icon_source = StringProperty('')  # Pfad zur Icon-Datei
    tab_text = StringProperty('')
    tab_key = StringProperty('')
    is_selected = BooleanProperty(False)
    # Dynamische Farben als Properties
    background_color_normal = ListProperty([0, 0, 0, 0])
    background_color_selected = ListProperty([0, 0, 0, 0])
    text_color_normal = ListProperty([0, 0, 0, 0])
    text_color_selected = ListProperty([0, 0, 0, 0])
    
    def __init__(self, **kwargs):
        super(TabButton, self).__init__(**kwargs)
        self.update_colors()
        self.update_translation()

        event_bus.bind(on_language_changed=self.on_language_changed)
        
        # Icon-Pfad basierend auf tab_text setzen, falls nicht explizit angegeben
        if not self.icon_source and self.tab_text:
            icon_name = self.tab_text.lower().replace('-', '_').replace(' ', '_')
            self.icon_source = join(ICONS_DIR, f"{icon_name}.ico")
    
    def update_colors(self):
        """Aktualisiert die Farben basierend auf dem aktuellen Theme"""
        self.background_color_normal = ThemeColors.current["SIDEBAR_BACKGROUND"]
        self.background_color_selected = ThemeColors.current["SIDEBAR_BACKGROUND"]
        self.text_color_normal = ThemeColors.current["TEXT_COLOR"]
        self.text_color_selected = ThemeColors.current["HIGHLIGHT_COLOR"]
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.parent.select_tab(self.tab_key) 
            return True
        return super(TabButton, self).on_touch_down(touch)
    
    def update_translation(self):
        """Aktualisiert den Text basierend auf der aktuellen Sprache"""
        if self.tab_key:
            old_text = self.tab_text
            self.tab_text = _(self.tab_key)
            print(f"Übersetzung für {self.tab_key}: '{old_text}' -> '{self.tab_text}'")
        else:
            print(f"Kein tab_key für Button: {self.text}")


    def on_language_changed(self, instance, language_code):
        """Wird aufgerufen, wenn sich die Sprache ändert"""
        self.update_translation()
    

class Sidebar(BoxLayout):
    """Seitenleiste mit Tabs"""
    screen_manager = ObjectProperty(None)
    is_expanded = BooleanProperty(True)
    # Dynamische Farben als Properties
    sidebar_bg_color = ListProperty([0, 0, 0, 0])
    button_bg_color = ListProperty([0, 0, 0, 0])
    text_color = ListProperty([0, 0, 0, 0])
    
    def __init__(self, **kwargs):
        super(Sidebar, self).__init__(**kwargs)
        self.current_tab = None
        self.update_colors()
        
        #Änderungen beobachten
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        event_bus.bind(on_language_changed=self.on_language_changed)
    
    def update_colors(self):
        """Aktualisiert die Farben basierend auf dem aktuellen Theme"""
        self.sidebar_bg_color = ThemeColors.current["SIDEBAR_BACKGROUND"]
        self.button_bg_color = ThemeColors.current["SIDEBAR_BACKGROUND"]
        self.text_color = ThemeColors.current["TEXT_COLOR"]
    
    def toggle_sidebar(self):
        """Umschalten zwischen erweiterter und reduzierter Seitenleiste"""
        self.is_expanded = not self.is_expanded
    
    def select_tab(self, tab_key):
        """Zum ausgewählten Tab wechseln"""
        if self.current_tab:
            for child in self.ids.tabs_layout.children:
                if isinstance(child, TabButton):
                    child.is_selected = (child.tab_key == tab_key)
                    if child.tab_key == tab_key:
                        self.current_tab = child
        else:
            # Erster Tab-Auswahl
            for child in self.ids.tabs_layout.children:
                if isinstance(child, TabButton) and child.tab_key == tab_key:
                    child.is_selected = True
                    self.current_tab = child
        
        # Zur entsprechenden Screen wechseln
        screen_name = self.screen_manager.get_screen_name_from_key(tab_key)
        self.screen_manager.current = screen_name
    
    def on_theme_changed(self, instance, theme_name):
        """Wird aufgerufen, wenn sich das Theme ändert"""
        # Farben aktualisieren
        self.update_colors()
        
        # Farben aller TabButtons aktualisieren
        for child in self.walk(restrict=True):
            if isinstance(child, TabButton):
                child.update_colors()
        
        # Canvas neu zeichnen lassen
        self.canvas.ask_update()
    
    def update_translations(self):
        """Aktualisiert alle Übersetzungen in der Sidebar"""
        for child in self.walk(restrict=True):
            if isinstance(child, TabButton):
                child.update_translation()

    def on_language_changed(self, instance, language_code):
        """Wird aufgerufen, wenn sich die Sprache ändert"""
        self.update_translations()

    def on_parent(self, instance, parent):
        """Wird aufgerufen, wenn die Sidebar zur Anzeige hinzugefügt wird"""
        if parent is not None:
            # Verzögere die Aktualisierung, um sicherzustellen, dass alle Komponenten bereit sind
            from kivy.clock import Clock
            Clock.schedule_once(lambda dt: self.update_translations(), 0.1)