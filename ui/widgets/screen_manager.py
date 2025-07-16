from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder

# Screen-Klassen importieren
from ui.screens.connection_screen import ConnectionScreen
from ui.screens.devices_screen import DevicesScreen
from ui.screens.account_screen import AccountScreen
from ui.screens.settings_screen import SettingsScreen
from ui.screens.files_screen import FilesScreen
from ui.screens.trend_screen import TrendScreen
from ui.screens.help_screen import HelpScreen
from ui.screens.info_screen import InfoScreen

Builder.load_file('ui/widgets/screen_manager.kv')

class AppScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super(AppScreenManager, self).__init__(**kwargs)
        
        # Alle Screens hinzufügen
        self.add_widget(ConnectionScreen(name='verbindung'))
        self.add_widget(DevicesScreen(name='geräte'))
        self.add_widget(AccountScreen(name='konto'))
        self.add_widget(SettingsScreen(name='einstellungen'))
        self.add_widget(FilesScreen(name='dateien'))
        self.add_widget(TrendScreen(name='online_trend'))
        self.add_widget(HelpScreen(name='hilfe'))
        self.add_widget(InfoScreen(name='info'))