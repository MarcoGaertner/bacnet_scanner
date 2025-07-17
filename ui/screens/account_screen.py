# ui/screens/account_screen.py
from kivy.lang import Builder
from ui.screens.base_screen import BaseScreen  # Die neue Basis-Klasse verwenden

Builder.load_file('ui/screens/account_screen.kv')

class AccountScreen(BaseScreen):  # Von BaseScreen erben statt Screen
    pass