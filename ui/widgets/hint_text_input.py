from kivy.uix.textinput import TextInput
from kivy.properties import (
    StringProperty, ListProperty, BooleanProperty, NumericProperty
)
from kivy.lang import Builder
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.clock import Clock
from core.events import event_bus
from ui.styles.colors import ThemeColors

# Pfad ggf. anpassen
Builder.load_file('ui/widgets/hint_text_input.kv')

class HintTextInput(TextInput):
    """TextInput mit Hint + Theme-Farben + sichtbarem Rahmen, Debug-Tools
       und vollständig unsichtbarer Textselektion (kein Highlight)."""

    # Public API
    hint_text = StringProperty('')
    active_color = ListProperty([1, 1, 1, 1])
    inactive_color = ListProperty([0.7, 0.7, 0.7, 1])
    is_focused = BooleanProperty(False)

    # Rahmen/Style
    show_border = BooleanProperty(True)
    draw_border_on_after = BooleanProperty(False)
    border_radius = NumericProperty(6)
    border_width_unfocused = NumericProperty(1.5)
    border_width_focused = NumericProperty(2.0)

    # Border-Rendering
    border_style = StringProperty("stroke")
    snap_half_px = BooleanProperty(True)

    # Theme-abgeleitete Farben
    border_color_unfocused = ListProperty([0, 0, 0, 0.35])
    border_color_focused = ListProperty([0, 0.6, 0.6, 1])
    fill_color = ListProperty([1, 1, 1, 1])

    # NEU: Selektions-Highlight global unterdrücken
    disable_text_highlight = BooleanProperty(True)

    # Debug
    debug_enabled = BooleanProperty(False)
    debug_print_events = BooleanProperty(False)
    debug_show_padding_guides = BooleanProperty(False)
    debug_force_border = BooleanProperty(False)
    debug_border_color = ListProperty([1, 0, 1, 1])
    debug_border_width = NumericProperty(3.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Standard-Backgrounds deaktivieren
        self.background_normal = ''
        self.background_active = ''
        self.background_disabled_normal = ''

        self._is_empty = not bool(self.text)
        self.update_colors()
        self.foreground_color = self.inactive_color if self._is_empty else self.active_color

        # Selektions‑UI unsichtbar halten (zusätzliche Absicherung)
        self._apply_no_highlight()

        # Bindings
        self.bind(text=self.on_text_changed, focus=self.on_focus_changed)
        self.bind(pos=self._redraw, size=self._redraw)
        event_bus.bind(on_theme_changed=self.on_theme_changed)

        # nach KV-Aufbau
        Clock.schedule_once(lambda dt: (self._apply_no_highlight(), self._redraw()), 0)

    # ---------- Theme / Farben ----------
    def update_colors(self, *args):
        self.cursor_color = ThemeColors.current["TEXT_COLOR"]
        self.active_color = ThemeColors.current["TEXT_COLOR"]
        self.inactive_color = [
            ThemeColors.current["TEXT_COLOR"][0] * 0.7,
            ThemeColors.current["TEXT_COLOR"][1] * 0.7,
            ThemeColors.current["TEXT_COLOR"][2] * 0.7,
            ThemeColors.current["TEXT_COLOR"][3],
        ]
        self.hint_text_color = [
            ThemeColors.current["TEXT_COLOR"][0] * 0.5,
            ThemeColors.current["TEXT_COLOR"][1] * 0.5,
            ThemeColors.current["TEXT_COLOR"][2] * 0.5,
            0.85,
        ]
        self.fill_color = ThemeColors.current["TAB_BACKGROUND"]
        txt = ThemeColors.current["TEXT_COLOR"]
        self.border_color_unfocused = [txt[0], txt[1], txt[2], 0.35]
        self.border_color_focused = ThemeColors.current["HIGHLIGHT_COLOR"]

        # Textfarbe abhängig von leer/nicht leer
        self.foreground_color = self.inactive_color if self._is_empty else self.active_color

        # Selektionsfarbe zusätzlich auf "unsichtbar" setzen (falls _draw_selection je aufgerufen wird)
        self.selection_color = (0, 0, 0, 0)

    # ---------- Selektion dauerhaft unsichtbar ----------
    def _apply_no_highlight(self):
        """Sichtbare Selektion vollständig unterdrücken (Handles/Bubble aus, Farbe transparent)."""
        if self.disable_text_highlight:
            self.selection_color = (0, 0, 0, 0)
            self.use_handles = False
            self.use_bubble = False

    # *** Kernpunkt: Auswahl nicht zeichnen ***
    def _draw_selection(self, *args):  # Kivy ruft das zum Zeichnen des Highlights auf
        if self.disable_text_highlight:
            return  # nichts zeichnen => kein sichtbares Highlight
        # Falls du das irgendwann wieder sichtbar haben willst:
        return super()._draw_selection(*args)

    # ---------- Events ----------
    def on_text_changed(self, instance, value):
        self._is_empty = not bool(value)
        self.foreground_color = self.inactive_color if self._is_empty else self.active_color
        if self.disable_text_highlight:
            self.selection_color = (0, 0, 0, 0)

    def on_focus_changed(self, instance, is_focused):
        self.is_focused = is_focused
        if self.disable_text_highlight:
            self.selection_color = (0, 0, 0, 0)
        self._redraw()

    def on_theme_changed(self, instance, theme_name):
        self.update_colors()
        self._apply_no_highlight()
        self._redraw()

    # ---------- Zeichnen ----------
    def _snap_bw(self, bw: float) -> float:
        if not self.snap_half_px:
            return bw
        return round(bw * 2.0) / 2.0

    def _redraw(self, *args):
        canvas_target = self.canvas.after if self.draw_border_on_after else self.canvas.before
        canvas_target.clear()

        # Geometrie
        x, y, w, h = float(self.x), float(self.y), float(self.width), float(self.height)
        r = float(dp(self.border_radius))

        # Rahmenfarbe/-breite
        if self.debug_force_border:
            bc = self.debug_border_color
            bw = float(dp(self.debug_border_width))
        else:
            bc = self.border_color_focused if self.is_focused else self.border_color_unfocused
            bw = float(dp(self.border_width_focused if self.is_focused else self.border_width_unfocused))

        bw = self._snap_bw(bw)

        if self.border_style == "stroke":
            with canvas_target:
                Color(*self.fill_color)
                RoundedRectangle(pos=(x, y), size=(w, h), radius=[r, r, r, r])

            ix = x + bw / 2.0
            iy = y + bw / 2.0
            iw = max(0.0, w - bw)
            ih = max(0.0, h - bw)
            ir = max(0.0, r - bw / 2.0)

            with canvas_target:
                Color(*bc)
                Line(rounded_rectangle=(ix, iy, iw, ih, ir), width=bw)
        else:
            iw = max(0.0, w - 2.0 * bw)
            ih = max(0.0, h - 2.0 * bw)
            ir = max(0.0, r - bw)
            with canvas_target:
                Color(*bc)
                RoundedRectangle(pos=(x, y), size=(w, h), radius=[r, r, r, r])
                Color(*self.fill_color)
                RoundedRectangle(pos=(x + bw, y + bw), size=(iw, ih), radius=[ir, ir, ir, ir])

        if self.debug_show_padding_guides:
            px, py = 0.0, 0.0
            try:
                if isinstance(self.padding, (list, tuple)):
                    if len(self.padding) == 2:
                        px, py = float(self.padding[0]), float(self.padding[1])
                    elif len(self.padding) == 4:
                        px, py = float(self.padding[0]), float(self.padding[1])
            except Exception:
                pass
            with canvas_target:
                Color(1, 0, 0, 0.3)
                Line(rectangle=(x + px, y + py, max(0.0, w - 2 * px), max(0.0, h - 2 * py)), width=1.0)
