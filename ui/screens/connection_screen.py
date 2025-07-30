from ui.screens.base_screen import BaseScreen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty, ListProperty, BooleanProperty
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
from core.config import ConfigManager
from core.i18n.translator import _
from core.events import event_bus
from ui.styles.colors import ThemeColors, get_color_with_alpha
from ui.widgets.radio_button import RadioButtonGroup, SimpleRadioButton
import json
import os
from kivy.app import App

# KV-Datei laden
Builder.load_file('ui/screens/connection_screen.kv')

class ConnectionScreen(BaseScreen):
    """Screen für BACnet-Verbindungseinstellungen"""
    screen_title = StringProperty("BACnet Connection")
    connection_type = StringProperty("network")
    config_manager = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ConnectionScreen, self).__init__(**kwargs)
        self.config_manager = ConfigManager()
        
        # Lade gespeicherte Einstellungen
        self.connection_type = self.config_manager.get_setting("connection", "type") or "network"
        
        # Registriere Events
        event_bus.bind(on_language_changed=self.on_language_changed)
        event_bus.bind(on_theme_changed=self.on_theme_changed)
        # Korrigiere diese Zeile - entferne die Bindung oder definiere on_connection_type_changed
        # event_bus.bind(on_connection_type_changed=self.on_connection_type_changed)
        
        # Initialisiere UI
        self.update_translations()
        Clock.schedule_once(self.setup_ui, 0)
    
    def update_translations(self):
        """Aktualisiert die Übersetzungen"""
        self.screen_title = _("connection.title")
    
    def setup_ui(self, *args):
        """Richtet die UI ein"""
        # Hauptlayout
        main_layout = BoxLayout(orientation='vertical', padding=[dp(20), dp(20), dp(20), dp(20)], spacing=dp(20))
        
        # Scrollview für den Inhalt
        scroll_view = ScrollView()
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
            text=_("connection.select_type"),
            font_size=dp(18),
            color=ThemeColors.current["TEXT_COLOR"],
            size_hint_y=None,
            height=dp(30),
            halign='center',
            valign='middle',
            pos_hint={'center_x': 0.5}
        )
        title_label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        
        # Verbindungsdiagramm
        diagram_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        diagram = Image(
            source='ui/assets/icons/connection_diagram.ico',
            size_hint=(None, None),
            size=(dp(200), dp(100)),
            pos_hint={'center_x': 0.5}
        )
        diagram_layout.add_widget(diagram)
        
        # Verbindungstypen
        connection_types = [
            _("connection.type.device_ap"),
            _("connection.type.network"),
            _("connection.type.mstp"),
            _("connection.type.usb"),
            _("connection.type.secure")
        ]
        
        # Bestimme den aktuell ausgewählten Typ
        selected_type = ""
        for option_text, option_value in [
            (_("connection.type.device_ap"), "device_ap"),
            (_("connection.type.network"), "network"),
            (_("connection.type.mstp"), "mstp"),
            (_("connection.type.usb"), "usb"),
            (_("connection.type.secure"), "secure")
        ]:
            if option_value == self.connection_type:
                selected_type = option_text
                break
        
        # Erstelle die Radio-Button-Gruppe
        radio_group = RadioButtonGroup(
            options=connection_types,
            selected=selected_type,
            group_name="connection_type",
            on_selection_changed=self._on_connection_type_changed
        )
        
        # Speichere eine Referenz auf die RadioButton-Gruppe
        self.radio_group = radio_group
        
        # Weiter-Button
        next_button = Button(
            text=_("connection.next"),
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=ThemeColors.current["HIGHLIGHT_COLOR"],
            color=(1, 1, 1, 1)  # Weißer Text auf Highlight-Farbe
        )
        next_button.bind(on_release=self.on_next_button_clicked)
        
        # Füge Widgets zum Layout hinzu
        content_layout.add_widget(logo_layout)
        content_layout.add_widget(title_label)
        content_layout.add_widget(diagram_layout)
        content_layout.add_widget(radio_group)
        
        # Füge einen Spacer hinzu, um den Button unten zu halten
        spacer = BoxLayout(size_hint_y=None, height=dp(20))
        content_layout.add_widget(spacer)
        
        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)
        main_layout.add_widget(next_button)
        
        # Lösche alle vorhandenen Widgets und füge das neue Layout hinzu
        self.clear_widgets()
        self.add_widget(main_layout)
    
    # Du hast diese Methode zweimal definiert - entferne eine davon
    def _on_connection_type_changed(self, value):
        """Wird aufgerufen, wenn der Verbindungstyp geändert wird"""
        print(f"DEBUG: _on_connection_type_changed aufgerufen mit Wert: {value}")
        
        # Finde den internen Wert für den übersetzten Text
        for option_text, option_value in [
            (_("connection.type.device_ap"), "device_ap"),
            (_("connection.type.network"), "network"),
            (_("connection.type.mstp"), "mstp"),
            (_("connection.type.usb"), "usb"),
            (_("connection.type.secure"), "secure")
        ]:
            if option_text == value:
                old_type = self.connection_type
                self.connection_type = option_value
                self.config_manager.update_setting("connection", "type", option_value)
                print(f"DEBUG: Verbindungstyp geändert von {old_type} zu {option_value}")
                return
        
        print(f"WARNING: Kein passender Verbindungstyp für '{value}' gefunden!")
    
    # Wenn du on_connection_type_changed verwenden möchtest, definiere sie hier
    def on_connection_type_changed(self, instance, value):
        """Event-Handler für on_connection_type_changed"""
        self._on_connection_type_changed(value)
    
    def on_next_button_clicked(self, instance):
        """Wird aufgerufen, wenn der 'Weiter'-Button geklickt wird"""
        # Navigiere zum entsprechenden Verbindungstyp-Screen
        from kivy.app import App
        app = App.get_running_app()
        
        # Überprüfe den aktuell ausgewählten RadioButton
        selected_radio = None
        for child in self.radio_group.children:
            if hasattr(child, 'selected') and child.selected:
                selected_radio = child.text
                break
        
        # Finde den internen Wert für den übersetzten Text
        selected_type = None
        for option_text, option_value in [
            (_("connection.type.device_ap"), "device_ap"),
            (_("connection.type.network"), "network"),
            (_("connection.type.mstp"), "mstp"),
            (_("connection.type.usb"), "usb"),
            (_("connection.type.secure"), "secure")
        ]:
            if option_text == selected_radio:
                selected_type = option_value
                break
        
        # Debug-Ausgaben
        print(f"DEBUG: Ausgewählter RadioButton: {selected_radio}")
        print(f"DEBUG: Entsprechender Verbindungstyp: {selected_type}")
        print(f"DEBUG: Gespeicherter connection_type: {self.connection_type}")
        
        # Aktualisiere den connection_type, falls nötig
        if selected_type and selected_type != self.connection_type:
            print(f"DEBUG: Aktualisiere connection_type von {self.connection_type} zu {selected_type}")
            self.connection_type = selected_type
        
        print(f"DEBUG: Navigation zu Screen '{self.connection_type}'")
        print(f"DEBUG: App: {app}")
        print(f"DEBUG: App.root: {app.root}")
        print(f"DEBUG: App.root.ids: {app.root.ids}")
        print(f"DEBUG: Verfügbare Screens: {app.root.ids.screen_manager.screen_names}")
        
        # Navigiere zum entsprechenden Screen
        app.root.ids.screen_manager.current = self.connection_type
    
    def on_language_changed(self, instance, language_code):
        """Wird aufgerufen, wenn die Sprache geändert wird"""
        self.update_translations()
        self.setup_ui()
    
    def on_theme_changed(self, instance, theme_name):
        """Wird aufgerufen, wenn das Theme geändert wird"""
        self.setup_ui()