import tkinter as tk

class DarkCombobox(tk.Frame):
    def __init__(self, parent, values=[], **kwargs):
        super().__init__(parent)
        self.configure(bg=kwargs.get('background', '#1f1f3e'))  # Dark background

        # Hauptframe konfigurieren
        self.grid_columnconfigure(0, weight=1)
        
        # Container für Entry und Button
        self.container = tk.Frame(self, bg=kwargs.get('background', '#1f1f3e'))
        self.container.grid(row=0, column=0, sticky='nsew')
        self.container.grid_columnconfigure(0, weight=1)
        
        # Variable für den ausgewählten Wert
        self.var = tk.StringVar()
        
        # Entry-Widget für die Anzeige
        self.entry = tk.Entry(
            self.container,
            textvariable=self.var,
            bg=kwargs.get('background', '#1f1f3e'),
            fg=kwargs.get('foreground', 'white'),
            relief='flat',
            readonlybackground=kwargs.get('background', '#1f1f3e'),
            justify='left'
        )
        self.entry.grid(row=0, column=0, sticky='ew', padx=(5, 0))
        self.entry.configure(state='readonly')
        
        # Dropdown Button
        self.button = tk.Button(
            self.container,
            text='▼',
            bg=kwargs.get('background', '#1f1f3e'),
            fg=kwargs.get('foreground', 'white'),
            relief='flat',
            command=self.show_dropdown,
            width=2,
            cursor='hand2'
        )
        self.button.grid(row=0, column=1)
        
        # Listbox für Dropdown (initial versteckt)
        self.dropdown_frame = tk.Frame(
            self,
            bg=kwargs.get('background', '#1f1f3e'),
            highlightthickness=1,
            highlightbackground=kwargs.get('foreground', 'white')
        )
        
        self.listbox = tk.Listbox(
            self.dropdown_frame,
            bg=kwargs.get('background', '#1f1f3e'),
            fg=kwargs.get('foreground', 'white'),
            selectmode='single',
            relief='flat',
            selectbackground='#00cccc',  # Petrol color for selection
            selectforeground='white'
        )
        self.listbox.pack(fill='both', expand=True)
        
        # Werte setzen
        self.values = values
        self.update_values(values)
        
        # Event Bindings
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.listbox.bind('<Leave>', self.on_leave)
        self.bind('<Configure>', self.on_configure)
        
        # Hover-Effekte für den Button
        self.button.bind('<Enter>', lambda e: self.button.configure(bg='#00cccc'))
        self.button.bind('<Leave>', lambda e: self.button.configure(bg=kwargs.get('background', '#1f1f3e')))

    def update_values(self, values):
        """Aktualisiert die Werte in der Listbox"""
        self.values = values
        self.listbox.delete(0, tk.END)
        for item in values:
            self.listbox.insert(tk.END, item)

    def show_dropdown(self):
        """Zeigt oder versteckt die Dropdown-Liste"""
        if not self.dropdown_frame.winfo_viewable():
            # Position und Größe des Dropdowns setzen
            self.dropdown_frame.grid(row=1, column=0, sticky='nsew')
            self.dropdown_frame.lift()
            # Größe an Container anpassen
            width = self.container.winfo_width()
            self.dropdown_frame.configure(width=width)
            # Maximale Höhe für 5 Einträge
            items_to_show = min(5, len(self.values))
            height = items_to_show * 20  # 20 Pixel pro Eintrag
            self.listbox.configure(height=items_to_show)
        else:
            self.dropdown_frame.grid_remove()

    def on_select(self, event=None):
        """Wird aufgerufen, wenn ein Element ausgewählt wird"""
        if self.listbox.curselection():
            selected = self.listbox.get(self.listbox.curselection())
            self.var.set(selected)
            self.dropdown_frame.grid_remove()
            # Event generieren
            self.event_generate('<<ComboboxSelected>>')

    def on_leave(self, event=None):
        """Versteckt das Dropdown wenn die Maus es verlässt"""
        # Kleine Verzögerung um versehentliches Schließen zu vermeiden
        self.after(100, self.check_mouse_position)

    def check_mouse_position(self):
        """Überprüft ob die Maus wirklich außerhalb ist"""
        x, y = self.winfo_pointerxy()
        widget_at_pointer = self.winfo_containing(x, y)
        if not (widget_at_pointer in [self.listbox, self.button, self.entry]):
            self.dropdown_frame.grid_remove()

    def on_configure(self, event=None):
        """Passt die Größe des Dropdowns an wenn sich das Fenster ändert"""
        if self.dropdown_frame.winfo_viewable():
            width = self.container.winfo_width()
            self.dropdown_frame.configure(width=width)

    def get(self):
        """Gibt den aktuellen Wert zurück"""
        return self.var.get()

    def set(self, value):
        """Setzt einen neuen Wert"""
        self.var.set(value)

    def configure(self, **kwargs):
        """Konfiguriert das Widget"""
        if 'values' in kwargs:
            self.update_values(kwargs['values'])
        if 'state' in kwargs:
            self.entry.configure(state=kwargs['state'])
        super().configure(**{k:v for k,v in kwargs.items() if k not in ['values', 'state']})