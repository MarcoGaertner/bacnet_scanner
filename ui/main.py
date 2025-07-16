from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from ui.widgets.sidebar import Sidebar  # Expliziten Import hinzufügen
from ui.widgets.screen_manager import AppScreenManager  # Expliziten Import hinzufügen

class BACnetScannerApp(App):
    title = 'BACnet Scanner'
    
    def build(self):
        # Dunkles Thema für moderne Optik
        Window.clearcolor = (0.15, 0.15, 0.15, 1)
        # Lade die Haupt-KV-Datei
        return Builder.load_file('ui/bacnet_scanner.kv')