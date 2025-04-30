# custom_menubar.py
import tkinter as tk

class CustomMenuBar(tk.Frame):
    def __init__(self, parent, bg_color, fg_color, active_bg, active_fg):
        super().__init__(parent, bg=bg_color, height=25)  # Feste Höhe für die Menüleiste
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.active_bg = active_bg
        self.active_fg = active_fg
        self.menus = {}
        
        # Verhindere, dass die Höhe geändert wird
        self.pack_propagate(False)
        
    def add_menu(self, label):
        # Erstelle einen Button für das Menü
        menu_button = tk.Menubutton(
            self,
            text=label,
            bg=self.bg_color,
            fg=self.fg_color,
            activebackground=self.active_bg,
            activeforeground=self.active_fg,
            relief='flat',
            padx=10
        )
        menu_button.pack(side='left')

        # Erstelle das Dropdown-Menü
        dropdown = tk.Menu(
            menu_button,
            tearoff=0,
            bg=self.bg_color,
            fg=self.fg_color,
            activebackground=self.active_bg,
            activeforeground=self.active_fg,
            relief='flat',
            borderwidth=1
        )
        
        # Verknüpfe Button mit Dropdown
        menu_button.configure(menu=dropdown)
        
        self.menus[label] = dropdown
        return dropdown