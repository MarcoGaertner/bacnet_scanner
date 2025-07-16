from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty
from kivy.lang import Builder
from kivy.core.window import Window

Builder.load_file('ui/widgets/sidebar.kv')

class TabButton(Button):
    """Button für einen Tab in der Seitenleiste"""
    icon = StringProperty('')
    tab_text = StringProperty('')
    is_selected = BooleanProperty(False)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.parent.parent.select_tab(self.tab_text)
            return True
        return super(TabButton, self).on_touch_down(touch)

class Sidebar(BoxLayout):
    """Seitenleiste mit Tabs"""
    screen_manager = ObjectProperty(None)
    is_expanded = BooleanProperty(True)
    
    def __init__(self, **kwargs):
        super(Sidebar, self).__init__(**kwargs)
        self.current_tab = None
        
    def toggle_sidebar(self):
        """Umschalten zwischen erweiterter und reduzierter Seitenleiste"""
        self.is_expanded = not self.is_expanded
    
    def select_tab(self, tab_name):
        """Zum ausgewählten Tab wechseln"""
        if self.current_tab:
            for child in self.ids.tabs_layout.children:
                if isinstance(child, TabButton):
                    child.is_selected = (child.tab_text == tab_name)
                    if child.tab_text == tab_name:
                        self.current_tab = child
        else:
            # Erster Tab-Auswahl
            for child in self.ids.tabs_layout.children:
                if isinstance(child, TabButton) and child.tab_text == tab_name:
                    child.is_selected = True
                    self.current_tab = child
        
        # Zur entsprechenden Screen wechseln
        screen_name = tab_name.lower().replace('-', '_').replace(' ', '_')
        self.screen_manager.current = screen_name