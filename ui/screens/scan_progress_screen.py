from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from ui.screens.base_screen import BaseScreen
from ui.styles.colors import ThemeColors

# load kv
Builder.load_file('ui/screens/scan_progress_screen.kv')

class ScanProgressScreen(BaseScreen):
    name = "scan_progress"

    progress = NumericProperty(0.0)   # 0.0 .. 1.0
    message  = StringProperty("")

    def set_progress(self, value: float, message: str = ""):
        # clamp + update
        try:
            v = max(0.0, min(1.0, float(value)))
        except Exception:
            v = 0.0
        self.progress = v
        if message is not None:
            self.message = str(message)
