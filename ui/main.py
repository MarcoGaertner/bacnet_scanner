from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from core.config import ConfigManager
from core.events import event_bus
from ui.styles.colors import ThemeManager
from os.path import join, dirname, abspath
import os
from core.i18n.translator import Translator


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
        from ui.styles.colors import ThemeColors
        Window.clearcolor = ThemeColors.current["BACKGROUND"]
    
    def on_theme_changed(self, instance, theme_name):
        """Wird aufgerufen, wenn sich das Theme ändert"""
        # Aktualisiere die Fensterfarbe
        from ui.styles.colors import ThemeColors
        Window.clearcolor = ThemeColors.current["BACKGROUND"]
        
        # Alle Screens neu laden
        for screen in self.root.ids.screen_manager.screens:
            screen.reload_theme()


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

    current_language = Translator().current_language
    print(f"Initialisiere UI-Übersetzungen mit Sprache: {current_language}")
    event_bus.dispatch('on_language_changed', current_language)