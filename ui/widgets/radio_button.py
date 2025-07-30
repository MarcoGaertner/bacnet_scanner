from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty, ListProperty
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.image import Image # Importiere das Image Widget
from kivy.graphics import Color, RoundedRectangle, Rectangle # Behalte diese für den Hintergrund des Buttons
from kivy.metrics import dp
from core.events import event_bus # Annahme, dass dies eine gültige Importquelle ist
from ui.styles.colors import ThemeColors # Annahme, dass dies eine gültige Importquelle ist
from kivy.clock import Clock

# KEINE KV-Datei laden, da SimpleRadioButton direkt in Python zeichnet.

class SimpleRadioButton(BoxLayout):
    """Einfacher Radio-Button als direktes Widget"""
    text = StringProperty('')
    selected = BooleanProperty(False)
    group = StringProperty('default')
    callback = ObjectProperty(None)

    def __init__(self, **kwargs):
        print(f"DEBUG: SimpleRadioButton.__init__ for text: '{kwargs.get('text', '')}'")
        super(SimpleRadioButton, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(30) # Halbe Größe wie angefordert
        self.padding = [dp(15), 0]
        self.spacing = dp(10)

        # Container für das Radio-Button-Bild (ersetzt den alten 'indicator' BoxLayout)
        self.radio_image_container = BoxLayout(
            size_hint=(None, None),
            size=(dp(20), dp(20)), # Größe für das Bild
            pos_hint={'center_y': 0.5}
        )

        # Image-Widget für die visuelle Darstellung des Radio-Buttons
        self.radio_image = Image( # <-- radio_image wird hier erstellt
            size_hint=(1, 1) # Füllt seinen übergeordneten Container (radio_image_container) aus
        )
        self.radio_image_container.add_widget(self.radio_image)

        # Label für den Text
        self.label = Label(
            text=self.text,
            color=ThemeColors.current["TEXT_COLOR"],
            font_size=dp(14),
            halign='left',
            valign='middle',
            size_hint_x=1, # Label nimmt den gesamten verfügbaren horizontalen Platz ein
            pos_hint={'center_y': 0.5}
        )
        self.label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))

        # Füge den Bild-Container und das Label zum Haupt-BoxLayout hinzu
        self.add_widget(self.radio_image_container)
        self.add_widget(self.label)
        print(f"DEBUG: SimpleRadioButton.__init__ added radio_image_container and label. Children: {self.children}")

        # Binde für das Zeichnen des Hintergrunds (RoundedRectangle für den gesamten Button)
        #self.bind(pos=self._draw_background, size=self._draw_background)
        #Clock.schedule_once(self._draw_background, 0)

        # Initiales Setzen der Bildquelle des Radio-Buttons
        # Dieser Aufruf ist jetzt sicher, da radio_image oben initialisiert wurde.
        self._update_radio_image()
        print(f"DEBUG: SimpleRadioButton.__init__ finished for '{self.text}'")

    def _draw_background(self, *args):
        """Zeichnet den RoundedRectangle-Hintergrund für den gesamten Button."""
        # print(f"DEBUG: _draw_background called for '{self.text}'. Pos: {self.pos}, Size: {self.size}")
        if not self.canvas or not self.canvas.before:
            # print(f"  WARNING: Canvas not ready for '{self.text}' background. Skipping.")
            return

        self.canvas.before.clear()
        with self.canvas.before:
            bg_color = ThemeColors.current["CARD_BACKGROUND"]
            # print(f"  Drawing background with color: {bg_color}, pos: (0,0), size: {self.size}")
            Color(rgba=bg_color)
            RoundedRectangle(pos=(0, 0), size=self.size, radius=[dp(8)])

    def _update_radio_image(self):
        """Aktualisiert die Quelle des Radio-Button-Bildes basierend auf dem Auswahlstatus."""
        # print(f"DEBUG: _update_radio_image called for '{self.text}'. Selected: {self.selected}")
        # Hinzufügen der Sicherheitsprüfung, ob radio_image bereits existiert
        if not hasattr(self, 'radio_image'):
            print(f"WARNING: radio_image not yet initialized for '{self.text}'. Skipping image update.")
            return

        if self.selected:
            self.radio_image.source = 'ui/assets/icons/radio.ico'
        else:
            self.radio_image.source = 'ui/assets/icons/radio-button.ico'
        # Kivy's Image-Widget handhabt sein eigenes Rendering und Aktualisierungen, wenn sich die Quelle ändert.

    def on_selected(self, *args):
        print(f"DEBUG: on_selected called for '{self.text}'. Selected: {self.selected}")
        # Dieser Aufruf ist jetzt sicher, da _update_radio_image eine Prüfung enthält.
        self._update_radio_image()

    def on_touch_down(self, touch):
        print(f"DEBUG: on_touch_down - Widget '{self.text}' - touch.pos: {touch.pos}, self.pos: {self.pos}, self.size: {self.size}")
        print(f"DEBUG: collide_point? {self.collide_point(*touch.pos)}")
        if self.collide_point(*touch.pos):
            print(f"DEBUG: Touch inside '{self.text}'! Selected-Status vorher: {self.selected}")
            if not self.selected:
                if self.parent:
                    for child in self.parent.children:
                        if isinstance(child, SimpleRadioButton) and child.group == self.group and child != self:
                            child.selected = False
                self.selected = True
                print(f"DEBUG: Jetzt ausgewählt! '{self.text}'")
                if self.callback:
                    self.callback(self.text)
            else:
                print(f"DEBUG: '{self.text}' war schon ausgewählt")
            return True
        return super(SimpleRadioButton, self).on_touch_down(touch)
    
    def _update_bg(self, *args):
        self._bg.pos = self.pos
        self._bg.size = self.size

# RadioButtonGroup bleibt gleich, da es nur SimpleRadioButton-Instanzen verwaltet
class RadioButtonGroup(BoxLayout):
    """Eine Gruppe von Radio-Buttons"""
    options = ListProperty([])
    selected = StringProperty('')
    group_name = StringProperty('default')
    on_selection_changed = ObjectProperty(None)

    def __init__(self, **kwargs):
        print(f"DEBUG: RadioButtonGroup.__init__ for group: '{kwargs.get('group_name', '')}'")
        super(RadioButtonGroup, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        
        Clock.schedule_once(self._init_buttons, 0.1)
        print(f"DEBUG: RadioButtonGroup.__init__ scheduled _init_buttons.")

    def _init_buttons(self, dt):
        print(f"DEBUG: RadioButtonGroup._init_buttons called. Options: {self.options}")
        self.clear_widgets()
        
        for option in self.options:
            rb = SimpleRadioButton(
                text=option,
                selected=option == self.selected,
                group=self.group_name,
                callback=self._on_button_selected
            )
            self.add_widget(rb)
            print(f"DEBUG:   Added SimpleRadioButton '{option}'. Current rb.pos: {rb.pos}, rb.size: {rb.size}")
        print(f"DEBUG: RadioButtonGroup._init_buttons finished. Children count: {len(self.children)}")
        print(f"DEBUG: RadioButtonGroup final height: {self.height}, minimum_height: {self.minimum_height}")

    def _on_button_selected(self, value):
        print(f"DEBUG: RadioButtonGroup._on_button_selected: '{value}'")
        self.selected = value
        if self.on_selection_changed:
            self.on_selection_changed(value)

    def on_options(self, instance, value):
        print(f"DEBUG: RadioButtonGroup.on_options called. New options: {value}")
        Clock.schedule_once(self._init_buttons, 0.1)

    def on_selected(self, instance, value):
        print(f"DEBUG: RadioButtonGroup.on_selected called. New selected: '{value}'")
        for child in self.children:
            if isinstance(child, SimpleRadioButton):
                child.selected = (child.text == value)