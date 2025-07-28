from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.clock import Clock

class BaseScreen(Screen):
    """Basis-Klasse für alle Screens mit Theme-Support"""
    
    def __init__(self, **kwargs):
        super(BaseScreen, self).__init__(**kwargs)
    
    def reload_theme(self):
        """Lädt das Theme neu"""
        # Aktualisiere die Canvas dieses Screens
        self.canvas.ask_update()
        
        # Vollständige rekursive Canvas-Aktualisierung
        def update_widget_canvases(widget):
            if hasattr(widget, 'canvas'):
                widget.canvas.ask_update()
                
                # Falls canvas.before oder canvas.after existieren
                if hasattr(widget.canvas, 'before'):
                    widget.canvas.before.flag_update()  # Verwende flag_update hier
                if hasattr(widget.canvas, 'after'):
                    widget.canvas.after.flag_update()  # Und hier auch
            
            # Theme-Farben in allen Komponenten aktualisieren
            if hasattr(widget, 'update_colors'):
                widget.update_colors()
            
            # Rekursiv für alle Kinder durchführen
            for child in widget.children:
                update_widget_canvases(child)
        
        # Starte die rekursive Aktualisierung
        update_widget_canvases(self)
        
    def reload_language(self):
        """Wird aufgerufen, wenn sich die Sprache ändert"""
        # Standard-Implementation, kann überschrieben werden
        pass