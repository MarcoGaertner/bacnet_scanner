from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from core.config import ConfigManager
from core.events import event_bus
from ui.styles.colors import ThemeManager
from os.path import join, dirname, abspath
import os
from core.i18n.translator import Translator
from kivy.clock import Clock
from ui.styles.colors import ThemeColors


ASSETS_DIR = join(dirname(abspath(__file__)), 'assets')
APP_ICON = join(ASSETS_DIR, 'siemens.ico')


class BACnetScannerApp(App):
    title = 'BACnet Scanner'
    
    def build(self):
        self.icon = APP_ICON

        try:
            Window.set_icon(APP_ICON)
            print("Icon wurde für das Fenster gesetzt")
        except Exception as e:
            print(f"Fehler beim Setzen des Icons: {e}")
    
        self.config_manager = ConfigManager()
        self.setup_theme()

        Translator()

        # Event-Listener für Änderungen
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        event_bus.bind(on_language_changed=self.on_language_changed)
        
        return Builder.load_file('ui/bacnet_scanner.kv')
    
    def setup_theme(self):
        """Initialisiert das Theme basierend auf den Einstellungen"""
        theme = self.config_manager.get_setting("ui", "theme")
        ThemeManager.set_theme(theme)
        # Setze Fenster-Hintergrund entsprechend des Themes
        Window.clearcolor = ThemeColors.current["BACKGROUND"]
    
    def on_theme_changed(self, instance, theme_name):
        """Wird aufgerufen, wenn sich das Theme ändert"""
        
        # Fensterfarbe aktualisieren
        Window.clearcolor = ThemeColors.current["BACKGROUND"]
        
        def force_update_canvases(dt):
            # Root-Widget und seinen gesamten Widget-Baum aktualisieren
            if hasattr(self, 'root'):
                # Root-Widget direkt aktualisieren
                if hasattr(self.root, 'canvas'):
                    self.root.canvas.ask_update()
                    if hasattr(self.root.canvas, 'before'):
                        self.root.canvas.before.flag_update()
                
                # Wichtigste Komponenten direkt ansprechen
                if hasattr(self.root.ids, 'screen_manager'):
                    self.root.ids.screen_manager.canvas.ask_update()
                    if hasattr(self.root.ids.screen_manager.canvas, 'before'):
                        self.root.ids.screen_manager.canvas.before.flag_update()
                
                if hasattr(self.root.ids, 'sidebar'):
                    if hasattr(self.root.ids.sidebar, 'update_colors'):
                        self.root.ids.sidebar.update_colors()
                    self.root.ids.sidebar.canvas.ask_update()
                
                # Rekursive Aktualisierung für den Rest
                self._recursive_update_canvas(self.root)
                
            # Rest des Codes wie bisher...
        
        Clock.schedule_once(force_update_canvases, 0)

    def on_language_changed(self, instance, language_code):
        """Wird aufgerufen, wenn sich die Sprache ändert"""
        # Alle Screens aktualisieren
        for screen in self.root.ids.screen_manager.screens:
            if hasattr(screen, 'reload_language'):
                screen.reload_language()
            else:
                # Fallback: Screen neu laden
                screen.reload_theme()

    def on_start(self):
        """Wird aufgerufen, wenn die App startet"""
        # Versuche Windows-spezifische Methode für das Icon
        try:
            if os.name == 'nt':
                import ctypes
                myappid = 'siemens.bacnetscanner.1.0'  # Eindeutige ID für Windows
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            print(f"Fehler bei Windows-spezifischer Icon-Setzung: {e}")

    def _recursive_update_canvas(self, widget):
        """Rekursive Aktualisierung aller Canvas-Elemente"""
        # Canvas dieses Widgets aktualisieren
        if hasattr(widget, 'canvas'):
            widget.canvas.ask_update()
            
        # Falls canvas.before oder canvas.after existieren
        if hasattr(widget, 'canvas') and hasattr(widget.canvas, 'before'):
            widget.canvas.before.flag_update()  # Verwende flag_update für canvas.before
        if hasattr(widget, 'canvas') and hasattr(widget.canvas, 'after'):
            widget.canvas.after.flag_update()  # Verwende flag_update für canvas.after
        
        # Rekursiv für alle Kinder durchführen
        for child in widget.children:
            self._recursive_update_canvas(child)



    def update_theme(self):
        """Aktualisiert das Theme des ScreenManagers"""
        # Falls nötig, Canvas aktualisieren
        self.canvas.ask_update()
        if hasattr(self.canvas, 'before'):
            self.canvas.before.flag_update()



            