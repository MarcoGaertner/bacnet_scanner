import tkinter as tk
from tkinter import ttk
from scan_config import PropertyCategory, ScanConfig

class ScanSettingsDialog:
    def __init__(self, parent, scan_config: ScanConfig):
        self.parent = parent
        self.scan_config = scan_config
        self.dialog = tk.Toplevel(parent)
        
        # Fenster-Konfiguration
        self.dialog.title("Scan-Einstellungen")
        self.dialog.minsize(600, 400)
        self.dialog.geometry("800x600")
        
        # Fenster-Eigenschaften
        self.dialog.transient(parent)  # Dialog immer im Vordergrund des Hauptfensters
        self.dialog.grab_set()         # Modal: Blockiert Interaktion mit Hauptfenster
        
        # Erlaube Maximieren und Minimieren
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            self.colors = {
                'deep_blue': '#000028',
                'white': '#FFFFFF',
                'light_sand': '#F3F3F0',
                'petrol': '#00cccc',
                'light_petrol': '#00C1B6',
                'dark_element': '#1f1f3e'
            }
        
        # Style konfigurieren
        self.setup_styles()
        
        # GUI erstellen
        self.create_widgets()
        
        # Fenster zentrieren
        self.center_dialog()

    def setup_styles(self):
        """Konfiguriert das Aussehen des Dialogs"""
        self.dialog.configure(bg=self.colors['deep_blue'])
        
        # Style für den Dialog
        self.style = ttk.Style(self.dialog)
        
        # Frame Style
        self.style.configure('Dialog.TFrame',
            background=self.colors['deep_blue']
        )
        
        # Label Style
        self.style.configure('Dialog.TLabel',
            background=self.colors['deep_blue'],
            foreground=self.colors['white']
        )
        
        # Checkbutton Style
        self.style.configure('Dialog.TCheckbutton',
            background=self.colors['deep_blue'],
            foreground=self.colors['white']
        )
        
        # Button Style
        self.style.configure('Dialog.TButton',
            background=self.colors['petrol'],
            foreground=self.colors['white']
        )
        self.style.map('Dialog.TButton',
            background=[('active', self.colors['light_petrol'])],
            foreground=[('active', self.colors['white'])]
        )
        
        # LabelFrame Style
        self.style.configure('Dialog.TLabelframe',
            background=self.colors['deep_blue'],
            foreground=self.colors['white']
        )
        self.style.configure('Dialog.TLabelframe.Label',
            background=self.colors['deep_blue'],
            foreground=self.colors['white'],
            font=('Arial', 10, 'bold')
        )
        
        # Success/Error Label Styles
        self.style.configure('Success.TLabel',
            background=self.colors['deep_blue'],
            foreground='#00ff00'
        )
        self.style.configure('Error.TLabel',
            background=self.colors['deep_blue'],
            foreground='#ff0000'
        )

    def create_widgets(self):
        """Erstellt alle GUI-Elemente"""
        # Hauptframe
        main_frame = ttk.Frame(self.dialog, style='Dialog.TFrame', padding="10")
        main_frame.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbare Region
        canvas = tk.Canvas(main_frame, bg=self.colors['deep_blue'], 
                         highlightthickness=0)  # Entfernt den Canvas-Rand
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", 
                                command=canvas.yview)
        
        # Frame für den Inhalt
        self.content_frame = ttk.Frame(canvas, style='Dialog.TFrame')
        
        # Konfiguriere Canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Erstelle Fenster im Canvas
        canvas_window = canvas.create_window((0, 0), window=self.content_frame, 
                                          anchor="nw", tags="self.content_frame")
        
        # Event Bindings für das Scrolling
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Passe die Breite des Frames an die Canvas-Breite an
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
            
        self.content_frame.bind('<Configure>', configure_canvas)
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(
            canvas_window, width=canvas.winfo_width()))
        
        # Erstelle die Einstellungen
        self.create_settings()
        
        # Button-Frame
        button_frame = ttk.Frame(self.dialog, style='Dialog.TFrame')
        button_frame.grid(row=1, column=0, pady=10, padx=10, sticky='ew')
        
        # Buttons
        ttk.Button(button_frame, text="Speichern", style='Dialog.TButton',
                  command=self.save_settings).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Abbrechen", style='Dialog.TButton',
                  command=self.dialog.destroy).pack(side='right', padx=5)
        
        # Grid-Konfiguration
        self.dialog.grid_rowconfigure(0, weight=1)
        self.dialog.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Platziere Canvas und Scrollbar
        canvas.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')

    def create_settings(self):
        """Erstellt die Einstellungsoptionen"""
        self.checkboxes = {}
        self.category_vars = {}  # Für "Alle auswählen" Funktionalität
        row = 0
        
        # Überschrift
        header = ttk.Label(
            self.content_frame, 
            text="Wählen Sie die zu scannenden Eigenschaften:",
            style='Dialog.TLabel',
            font=('Arial', 12, 'bold')
        )
        header.grid(row=row, column=0, columnspan=2, pady=(0, 20), sticky='w')
        row += 1
        
        # Erstelle Einstellungen nach Kategorien
        for category in PropertyCategory:
            properties = self.scan_config.get_properties_by_category(category)
            if properties:
                # Kategorie-Frame mit Umrandung
                category_frame = ttk.LabelFrame(
                    self.content_frame,
                    text=category.value,
                    style='Dialog.TLabelframe'
                )
                category_frame.grid(row=row, column=0, sticky='ew', pady=(5, 10), padx=5)
                
                # "Alle auswählen" Checkbox für die Kategorie
                category_var = tk.BooleanVar()
                self.category_vars[category] = category_var
                
                select_all = ttk.Checkbutton(
                    category_frame,
                    text="Alle auswählen",
                    variable=category_var,
                    style='Dialog.TCheckbutton',
                    command=lambda cat=category: self.toggle_category(cat)
                )
                select_all.grid(row=0, column=0, sticky='w', padx=10, pady=5)
                
                # Properties in einem separaten Frame
                props_frame = ttk.Frame(category_frame, style='Dialog.TFrame')
                props_frame.grid(row=1, column=0, sticky='ew', padx=20)
                
                # Properties hinzufügen
                for i, prop in enumerate(properties):
                    print(f"Erstelle Checkbox für {prop.name}: enabled={prop.enabled}")
                    var = tk.BooleanVar(value=prop.enabled)
                    self.checkboxes[prop.name] = var
                    
                    cb = ttk.Checkbutton(
                        props_frame,
                        text=prop.name,
                        variable=var,
                        style='Dialog.TCheckbutton',
                        command=lambda cat=category: self.update_category_state(cat)
                    )
                    cb.grid(row=i, column=0, sticky='w', pady=2)
                
                row += 1
                
                # Aktualisiere den Status der "Alle auswählen" Checkbox
                self.update_category_state(category)

                
    def save_settings(self):
        """Speichert die ausgewählten Einstellungen"""
        try:
            selected_items = {
                item: var.get()
                for item, var in self.checkboxes.items()
            }
            print("\nSpeichere Einstellungen:")
            for item, enabled in selected_items.items():
                print(f"- {item}: {enabled}")
                
            self.scan_config.update_property_settings(selected_items)
            
            # Debug: Überprüfe Zustand nach dem Update
            print("\nZustand nach Update in scan_config:")
            for name, prop in self.scan_config.properties.items():
                print(f"- {name}: {prop.enabled}")
            
            # Speichere die Konfiguration
            from scan_config import save_scan_config
            save_scan_config(self.scan_config)
            
            # Zeige Erfolg an
            success_label = ttk.Label(
                self.dialog,
                text="Einstellungen gespeichert!",
                style='Success.TLabel',
                font=('Arial', 10)
            )
            success_label.grid(row=2, column=0, pady=5)
            self.dialog.after(1000, self.dialog.destroy)
                
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
            import traceback
            traceback.print_exc()
            error_label = ttk.Label(
                self.dialog,
                text=f"Fehler beim Speichern: {str(e)}",
                style='Error.TLabel',
                font=('Arial', 10)
            )
            error_label.grid(row=2, column=0, pady=5)

    def center_dialog(self):
        """Zentriert den Dialog auf dem Bildschirm"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')

    def toggle_category(self, category):
        """Aktiviert/Deaktiviert alle Eigenschaften einer Kategorie"""
        state = self.category_vars[category].get()
        properties = self.scan_config.get_properties_by_category(category)
        
        for prop in properties:
            if prop.name in self.checkboxes:
                self.checkboxes[prop.name].set(state)

    def update_category_state(self, category):
        """Aktualisiert den Status der Kategorie-Checkbox"""
        properties = self.scan_config.get_properties_by_category(category)
        states = [self.checkboxes[prop.name].get() for prop in properties 
                 if prop.name in self.checkboxes]