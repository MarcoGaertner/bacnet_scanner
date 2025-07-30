from ui.screens.base_screen import BaseScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty
from kivy.metrics import dp
from kivy.clock import Clock
from core.config import ConfigManager
from core.i18n.translator import _
from core.events import event_bus
from ui.styles.colors import ThemeColors

class ConnectionTypeBaseScreen(BaseScreen):
    """Basis-Screen für alle Verbindungstyp-Screens"""
    screen_title = StringProperty("")
    config_manager = ObjectProperty(None)
    connection_type = StringProperty("")
    
    def __init__(self, **kwargs):
        super(ConnectionTypeBaseScreen, self).__init__(**kwargs)
        self.config_manager = ConfigManager()
        
        # Registriere Events
        event_bus.bind(on_language_changed=self.on_language_changed)
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        
        # Initialisiere UI
        self.update_translations()
        Clock.schedule_once(self.setup_ui, 0)
    
    def update_translations(self):
        """Aktualisiert die Übersetzungen (in Unterklassen zu überschreiben)"""
        pass
    
    def setup_ui(self, *args):
        """Richtet die UI ein (in Unterklassen zu überschreiben)"""
        # Hauptlayout
        main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(20), dp(20), dp(20)], spacing=dp(20))
        
        # Scrollview für den Inhalt
        scroll_view = ScrollView(do_scroll_x=False, do_scroll_y=True)
        content_layout = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Logo
        logo_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        logo = Image(
            source='ui/assets/icons/connection_yel-logo.ico',
            size_hint=(None, None),
            size=(dp(64), dp(64)),
            pos_hint={'center_x': 0.5}
        )
        logo_layout.add_widget(logo)
        
        # Überschrift
        title_label = Label(
            text=self.screen_title,
            font_size=dp(18),
            color=ThemeColors.current["TEXT_COLOR"],
            size_hint_y=None,
            height=dp(30),
            halign='center',
            valign='middle',
            pos_hint={'center_x': 0.5}
        )
        title_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # Füge spezifische Inhalte hinzu (in Unterklassen zu überschreiben)
        specific_content = self.create_specific_content()
        
        # Stellen Sie sicher, dass specific_content size_hint_y=None hat
        specific_content.size_hint_y = None
        specific_content.bind(minimum_height=specific_content.setter('height'))
        
        # Buttons
        button_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10))
        
        # Zurück-Button
        back_button = Button(
            text=_("connection.back"),
            size_hint_x=0.5,
            background_normal='',
            background_color=ThemeColors.current["CARD_BACKGROUND"],
            color=ThemeColors.current["TEXT_COLOR"]
        )
        back_button.bind(on_release=self.on_back_button_clicked)
        
        # Weiter-Button
        next_button = Button(
            text=_("connection.next"),
            size_hint_x=0.5,
            background_normal='',
            background_color=ThemeColors.current["HIGHLIGHT_COLOR"],
            color=(1, 1, 1, 1)
        )
        next_button.bind(on_release=self.on_next_button_clicked)
        
        button_layout.add_widget(back_button)
        button_layout.add_widget(next_button)
        
        # Füge Widgets zum Layout hinzu
        content_layout.add_widget(logo_layout)
        content_layout.add_widget(title_label)
        content_layout.add_widget(specific_content)
        
        # Füge einen Spacer hinzu, um die Buttons unten zu halten
        spacer = BoxLayout(size_hint_y=None, height=dp(20))
        content_layout.add_widget(spacer)
        
        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)
        main_layout.add_widget(button_layout)
        
        # Lösche alle vorhandenen Widgets und füge das neue Layout hinzu
        self.clear_widgets()
        self.add_widget(main_layout)
        
        # Speichere eine Referenz auf das content_layout für spätere Aktualisierungen
        self.ids['content_layout'] = content_layout
    
    def create_specific_content(self):
        """Erstellt den spezifischen Inhalt für den jeweiligen Verbindungstyp (in Unterklassen zu überschreiben)"""
        return BoxLayout(size_hint_y=None, height=dp(100))
    
    def on_back_button_clicked(self, instance):
        """Wird aufgerufen, wenn der 'Zurück'-Button geklickt wird"""
        app = self.get_root_window().children[0]
        app.root.ids.screen_manager.current = 'verbindung'
    
    def on_next_button_clicked(self, instance):
        """Wird aufgerufen, wenn der 'Weiter'-Button geklickt wird (in Unterklassen zu überschreiben)"""
        # Standardmäßig zur Geräte-Seite wechseln
        app = self.get_root_window().children[0]
        app.root.ids.screen_manager.current = 'geräte'
    
    def on_language_changed(self, instance, language_code):
        """Wird aufgerufen, wenn die Sprache geändert wird"""
        self.update_translations()
        self.setup_ui()
    
    def on_theme_changed(self, instance, theme_name):
        """Wird aufgerufen, wenn das Theme geändert wird"""
        self.setup_ui()