from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy_garden.svg import Svg # <--- DIES IST DER KORREKTE IMPORT!
from kivy.metrics import dp
from core.events import event_bus
from ui.styles.colors import ThemeColors
from kivy.clock import Clock

class SimpleRadioButton(BoxLayout):
    """Einfacher Radio-Button mit SVG-Indikatoren."""
    text = StringProperty('')
    selected = BooleanProperty(False)
    group = StringProperty('default')
    callback = ObjectProperty(None)
    
    # Farben für Text und SVG-Indikator
    text_color = ListProperty(ThemeColors.current["TEXT_COLOR"])
    svg_color = ListProperty([0.7, 0.7, 0.7, 1]) # Standard: Hellgrau für nicht ausgewähltes SVG
    svg_selected_color = ListProperty([0.2, 0.6, 0.9, 1]) # Standard: Blau für ausgewähltes SVG

    def __init__(self, **kwargs):
        super(SimpleRadioButton, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(30) # Halbe Größe
        self.padding = [dp(15), 0]
        self.spacing = dp(10)

        # BoxLayout für den SVG-Indikator
        self.svg_container = BoxLayout(
            size_hint=(None, None),
            size=(dp(20), dp(20)), # Größe für das SVG
            pos_hint={'center_y': 0.5}
        )

        # SVG-Widget für die visuelle Darstellung des Radio-Buttons
        self.radio_svg = Svg( # <--- Hier wird das Svg-Widget instanziiert
            size_hint=(1, 1) # Füllt seinen übergeordneten Container (svg_container) aus
        )
        self.svg_container.add_widget(self.radio_svg)

        # Label für den Text
        self.label = Label(
            text=self.text,
            color=self.text_color, # Textfarbe von Property
            font_size=dp(14),
            halign='left',
            valign='middle',
            size_hint_x=1,
            pos_hint={'center_y': 0.5}
        )
        self.label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        # Widgets hinzufügen
        self.add_widget(self.svg_container)
        self.add_widget(self.label)

        # Bindungen für die Aktualisierung des SVG und des Labels
        self.bind(selected=self._update_svg_and_label_colors)
        self.bind(text_color=self._update_svg_and_label_colors)
        self.bind(svg_color=self._update_svg_and_label_colors)
        self.bind(svg_selected_color=self._update_svg_and_label_colors)

        # Initiales Setzen der SVG-Quelle und Farben
        self._update_svg_and_label_colors()

    def _update_svg_and_label_colors(self, *args):
        """Aktualisiert die SVG-Quelle und die Farben basierend auf dem Auswahlstatus und den Properties."""
        # Aktualisiere die SVG-Quelle
        if self.selected:
            self.radio_svg.source = 'ui/assets/icons/radio_selected.svg'
            self.radio_svg.color = self.svg_selected_color # Setze die Farbe des ausgewählten SVG
        else:
            self.radio_svg.source = 'ui/assets/icons/radio_unselected.svg'
            self.radio_svg.color = self.svg_color # Setze die Farbe des nicht ausgewählten SVG
        
        # Aktualisiere die Label-Farbe
        self.label.color = self.text_color

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if not self.selected:
                if self.parent:
                    for child in self.parent.children:
                        if isinstance(child, SimpleRadioButton) and child.group == self.group and child != self:
                            child.selected = False
                self.selected = True
                if self.callback:
                    self.callback(self.text)
            return True
        return super(SimpleRadioButton, self).on_touch_down(touch)


class RadioButtonGroup(BoxLayout):
    """Eine Gruppe von Radio-Buttons"""
    options = ListProperty([])
    selected = StringProperty('')
    group_name = StringProperty('default')
    on_selection_changed = ObjectProperty(None)

    # Farben für alle Buttons in dieser Gruppe
    button_text_color = ListProperty(ThemeColors.current["TEXT_COLOR"])
    button_svg_color = ListProperty([0.7, 0.7, 0.7, 1])
    button_svg_selected_color = ListProperty([0.2, 0.6, 0.9, 1])

    def __init__(self, **kwargs):
        super(RadioButtonGroup, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        
        # Wenn sich die Gruppenfarben ändern, müssen die Buttons neu initialisiert werden
        self.bind(button_text_color=self._reinit_buttons,
                  button_svg_color=self._reinit_buttons,
                  button_svg_selected_color=self._reinit_buttons)

        Clock.schedule_once(self._init_buttons, 0.1)

    def _init_buttons(self, dt):
        self.clear_widgets()
        
        for option in self.options:
            rb = SimpleRadioButton(
                text=option,
                selected=option == self.selected,
                group=self.group_name,
                callback=self._on_button_selected,
                # Farben an die SimpleRadioButton-Instanz übergeben
                text_color=self.button_text_color,
                svg_color=self.button_svg_color,
                svg_selected_color=self.button_svg_selected_color
            )
            self.add_widget(rb)

    def _reinit_buttons(self, *args):
        """Wird aufgerufen, wenn sich die Farben der Gruppe ändern, um die Buttons neu zu erstellen."""
        Clock.schedule_once(self._init_buttons, 0.1)

    def _on_button_selected(self, value):
        """Wird aufgerufen, wenn ein Button in der Gruppe ausgewählt wird."""
        self.selected = value
        if self.on_selection_changed:
            self.on_selection_changed(value)

    def on_options(self, instance, value):
        """Reagiert auf Änderungen der options-Property."""
        Clock.schedule_once(self._init_buttons, 0.1)

    def on_selected(self, instance, value):
        """Reagiert auf Änderungen der selected-Property."""
        for child in self.children:
            if isinstance(child, SimpleRadioButton):
                child.selected = (child.text == value)