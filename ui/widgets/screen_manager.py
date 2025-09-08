from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from core.events import event_bus  # Wichtig: EventBus importieren
from kivy.core.window import Window
from kivy.app import App

# Screen-Klassen importieren
from ui.screens.connection_screen import ConnectionScreen
from ui.screens.devices_screen import DevicesScreen
from ui.screens.account_screen import AccountScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.files_screen import FilesScreen
from ui.screens.trend_screen import TrendScreen
from ui.screens.help_screen import HelpScreen
from ui.screens.info_screen import InfoScreen
from ui.screens.device_details_screen import DeviceDetailsScreen
from ui.screens.network_screen import NetworkScreen

Builder.load_file('ui/widgets/screen_manager.kv')

class AppScreenManager(ScreenManager):
    """Screen Manager mit Unterstützung für Mehrsprachigkeit"""
    
    # Zuordnung von Übersetzungsschlüsseln zu internen Screen-Namen
    # Diese Schlüssel bleiben konstant, unabhängig von der Sprache
    SCREEN_MAPPING = {
        'sidebar.connection': 'verbindung',
        'sidebar.devices': 'geräte',
        'sidebar.account': 'konto', 
        'sidebar.settings': 'einstellungen',
        'sidebar.files': 'dateien',
        'sidebar.trend': 'online_trend',
        'sidebar.help': 'hilfe',
        'sidebar.info': 'info'
    }
    
    def __init__(self, **kwargs):
        super(AppScreenManager, self).__init__(**kwargs)
        
        # Alle Screens hinzufügen - Verwende konstante interne Namen
        self.add_widget(ConnectionScreen(name='verbindung'))
        self.add_widget(DevicesScreen(name='geräte'))
        self.add_widget(AccountScreen(name='konto'))
        self.add_widget(SettingsScreen(name='einstellungen'))
        self.add_widget(FilesScreen(name='dateien'))
        self.add_widget(TrendScreen(name='online_trend'))
        self.add_widget(HelpScreen(name='hilfe'))
        self.add_widget(InfoScreen(name='info')) 
        self.add_widget(DeviceDetailsScreen(name="device_details"))
        self.add_widget(NetworkScreen(name='network'))
        
        # Reagiere auf Sprachänderungen
        event_bus.bind(on_language_changed=self.on_language_changed)
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        event_bus.bind(on_theme_changed=self.debug_theme_update)
    
    
    def get_screen_name_from_key(self, tab_key):
        """Gibt den internen Screen-Namen für einen Übersetzungsschlüssel zurück"""
        return self.SCREEN_MAPPING.get(tab_key, 'verbindung')  # Fallback auf Verbindungs-Screen
    
    def on_language_changed(self, instance, language_code):
        """Wird aufgerufen, wenn die Sprache geändert wird"""
        # Aktualisiere alle Screens
        for screen in self.screens:
            if hasattr(screen, 'reload_language'):
                screen.reload_language()

    def on_theme_changed(self, instance, theme_name):
        """Wird aufgerufen, wenn das Theme geändert wird"""
        print("ScreenManager: Theme wurde geändert zu", theme_name)
        
        # Canvas des ScreenManagers aktualisieren
        if hasattr(self, 'canvas'):
            self.canvas.ask_update()
            if hasattr(self.canvas, 'before'):
                self.canvas.before.flag_update()
            if hasattr(self.canvas, 'after'):
                self.canvas.after.flag_update()
        
        # Theme-Update an alle Screens weitergeben
        for screen in self.screens:
            if hasattr(screen, 'reload_theme'):
                screen.reload_theme()


    def debug_theme_update(self, instance, theme_name):
        """Zeigt an, welche Komponenten aktualisiert werden"""
        print("\n--- Theme-Update-Debug ---")
        print(f"Window.clearcolor: {Window.clearcolor}")
        
        if hasattr(self, 'root'):
            print(f"Root has canvas: {hasattr(self.root, 'canvas')}")
            
            if hasattr(self.root.ids, 'screen_manager'):
                sm = self.root.ids.screen_manager
                print(f"ScreenManager has canvas: {hasattr(sm, 'canvas')}")
                print(f"ScreenManager has canvas.before: {hasattr(sm.canvas, 'before')}")
                print(f"Current screen: {sm.current_screen.name}")
        
        print("------------------------\n")