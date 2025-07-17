from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.clock import Clock

class BaseScreen(Screen):
    """Basis-Klasse für alle Screens mit Theme-Support"""
    
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)
    
    def reload_theme(self):
        """Lädt das Theme neu"""
        # Dies zwingt Kivy, die Canvas-Anweisungen mit den aktualisierten Farben neu zu zeichnen
        self.canvas.ask_update()
        
        # Bei komplexen Screens können zusätzliche Aktualisierungen notwendig sein
        for child in self.walk():
            if hasattr(child, 'canvas'):
                child.canvas.ask_update()

    def reload_language(self):
        """Wird aufgerufen, wenn sich die Sprache ändert"""
        # Standard-Implementation, kann überschrieben werden
        pass