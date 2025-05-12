import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ip_selector import get_network_interfaces
from port_selector import get_common_bacnet_ports
from csv_exporter import export_to_csv
import os
import platform
import ctypes
from PIL import Image, ImageTk
from config_manager import save_config, load_config
from dark_combobox import DarkCombobox  
from custom_menubar import CustomMenuBar
import json
from datetime import datetime
from tkinter import filedialog
from settings_dialog import ScanSettingsDialog
from scan_config import (
    ScanConfig,
    save_scan_config, 
    load_scan_config,
    PropertyCategory,
    BACnetProperty
)

class BACnetScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BACnet Scanner")

        # 1. Grundlegende Konfiguration
        self.config = load_config()
        self.devices = {}
        self.networks = {}

        # 2. Style-Konfiguration
        self.setup_styles()

        # 3. Fenster-Geometrie
        self.setup_window_geometry()

        # 4. Icon-Konfiguration
        self.setup_window_icon()

        # 5. Grid-Konfiguration
        self.root.grid_rowconfigure(0, weight=0)  # Für die Menüleiste
        self.root.grid_rowconfigure(1, weight=1)  # Für den Hauptinhalt
        self.root.grid_columnconfigure(0, weight=1)

        # 6. GUI-Elemente erstellen (vor dem Menü)
        self.create_gui_elements()

        # 7. Menü erstellen (nach den GUI-Elementen)
        self.create_menu()

        # 8. Widget-Styling
        self.style_widgets()

        # 9. Event-Handler
        self.setup_event_handlers()

        # 10. Finale Initialisierung
        self.finalize_setup()

        #11 Speichert das aktuelle Scan-Ergebnis
        self.current_result = None

        # Lade gespeicherte Konfiguration
        self.scan_config = load_scan_config()
        print("\nInitiale Scan-Konfiguration geladen:")
        for name, prop in self.scan_config.properties.items():
            print(f"- {name}: {prop.enabled}")

    def setup_styles(self):
        """Konfiguriert alle Styles"""
        self.colors = {
            'deep_blue': '#000028',    # Haupthintergrund
            'white': '#FFFFFF',        # Text
            'light_sand': '#F3F3F0',   # Sekundäre Elemente
            'petrol': '#00cccc',       # Akzente (Button)
            'light_petrol': '#00C1B6', # Hover/Aktiv Zustände
            'dark_element': '#1f1f3e'  # Textbox und Combobox Hintergrund
        }

        self.style = ttk.Style()
        
        # Basis-Style
        self.style.configure('.',
            background=self.colors['deep_blue'],
            foreground=self.colors['white']
        )

        # Button Style speziell anpassen
        self.style.configure('Scan.TButton',
            background=self.colors['petrol'],
            foreground=self.colors['white']
        )
        self.style.map('Scan.TButton',
            background=[('active', self.colors['light_petrol']),
                    ('pressed', self.colors['petrol'])],
            foreground=[('active', self.colors['white']),
                    ('pressed', self.colors['white'])]
        )

        # Frame Style
        self.style.configure('TFrame',
            background=self.colors['deep_blue']
        )

        # Label Style
        self.style.configure('TLabel',
            background=self.colors['deep_blue'],
            foreground=self.colors['white']
        )

        # Button Style
        self.style.configure('TButton',
            background=self.colors['petrol'],
            foreground=self.colors['white']
        )
        self.style.map('TButton',
            background=[('active', self.colors['light_petrol'])],
            foreground=[('active', self.colors['white'])]
        )

        # LabelFrame Style
        self.style.configure('TLabelframe',
            background=self.colors['deep_blue'],
            foreground=self.colors['white']
        )
        self.style.configure('TLabelframe.Label',
            background=self.colors['deep_blue'],
            foreground=self.colors['white']
        )

        # Haupthintergrund setzen
        self.root.configure(bg=self.colors['deep_blue'])

    def export_csv(self):
        """Exportiert die Scan-Ergebnisse als CSV"""
        if not self.networks:
            messagebox.showwarning(
                "Keine Daten",
                "Es wurden noch keine Geräte gescannt. Bitte führen Sie zuerst einen Scan durch."
            )
            return
        
        success, message = export_to_csv(self.devices, self.networks)
        if success:
            messagebox.showinfo("Export erfolgreich", message)
        else:
            messagebox.showerror("Export fehlgeschlagen", message)

    def setup_window_geometry(self):
        """Konfiguriert die Fenster-Geometrie"""
        default_geometry = "800x600"
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        
        try:
            if self.config.get('window_size') and self.config.get('window_position'):
                saved_size = self.config['window_size']
                saved_x, saved_y = self.config['window_position']
                
                if (0 <= saved_x <= screen_width - 200 and 
                    0 <= saved_y <= screen_height - 200):
                    self.root.geometry(f"{saved_size}+{saved_x}+{saved_y}")
                else:
                    self.root.geometry(f"{saved_size}+{x}+{y}")
            else:
                self.root.geometry(f"{default_geometry}+{x}+{y}")
        except Exception as e:
            print(f"Fehler beim Setzen der Fenstergeometrie: {e}")
            self.root.geometry(f"{default_geometry}+{x}+{y}")

    def style_widgets(self):
        """Styling für spezifische Widgets"""
        # ScrolledText (Ergebnis-Textbox) Style
        self.result_text.configure(
            background=self.colors['dark_element'],
            foreground=self.colors['white'],
            insertbackground=self.colors['petrol'],  # Cursor-Farbe
            selectbackground=self.colors['petrol'],
            selectforeground=self.colors['white']
        )

    def setup_event_handlers(self):
        """Richtet alle Event-Handler ein"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.ip_combo.bind('<<ComboboxSelected>>', self.on_ip_selected)
        self.port_combo.bind('<<ComboboxSelected>>', self.on_port_selected)

    def finalize_setup(self):
        """Führt finale Initialisierungsschritte durch"""
        self.root.update()
        self.root.minsize(400, 300)
        self.fill_ip_list()
        self.fill_port_list()

    def setup_window_icon(self):
        """Konfiguriert das Fenster-Icon"""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'graphics', 'siemens_logo_icon.ico')
            
            if platform.system() == 'Windows':
                myappid = 'siemens.bacnet.scanner.1.0'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                self.root.iconbitmap(default=icon_path)
                
                hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                if hwnd:
                    ctypes.windll.user32.SendMessageW(hwnd, 0x80, 0, icon_path)
            else:
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, photo)
                
        except Exception as e:
            print(f"Fehler beim Laden des Icons: {e}")

    def fill_ip_list(self):
        """Füllt die IP-Adressliste"""
        try:
            # Debug-Ausgaben
            print("Lade IP-Liste...")
            print(f"Gespeicherte Konfiguration: {self.config}")
            
            interfaces = get_network_interfaces()
            ip_list = [ip for ip, desc in interfaces]
            
            print(f"Verfügbare IPs: {ip_list}")
            print(f"Letzte IP aus Konfig: {self.config.get('last_ip')}")
            
            # Aktualisiere die Werte in der Combobox
            self.ip_combo.configure(values=ip_list)  # Hier die Änderung
            
            # Setze den letzten verwendeten Wert oder den ersten in der Liste
            last_ip = self.config.get('last_ip')
            if last_ip and last_ip in ip_list:
                print(f"Versuche letzte IP zu setzen: {last_ip}")
                self.ip_combo.set(last_ip)  # Hier die Änderung
            else:
                print("Keine letzte IP gefunden oder nicht verfügbar, setze erste verfügbare IP")
                if ip_list:
                    self.ip_combo.set(ip_list[0])  # Hier die Änderung
                    
            # Aktualisiere die GUI
            self.root.update()
            
        except Exception as e:
            print(f"Fehler in fill_ip_list: {e}")

    def create_gui_elements(self):
        """Erstellt alle GUI-Elemente"""
        # Hauptframe
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Konfiguriere Main-Frame-Grid für Skalierung
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(4, weight=1)
        
        # Oberer Frame für Eingabefelder
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        input_frame.grid_columnconfigure(1, weight=1)
        
        # IP-Auswahl Label
        ttk.Label(input_frame, text="IP-Adresse:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))

        # Port-Auswahl Label
        ttk.Label(input_frame, text="BACnet Port:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        
        # IP-Auswahl Combobox
        self.ip_var = tk.StringVar()
        self.ip_combo = DarkCombobox(
            input_frame,
            background=self.colors['dark_element'],
            foreground=self.colors['white']
        )
        self.ip_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # Port-Auswahl Combobox
        self.port_var = tk.StringVar()
        self.port_combo = DarkCombobox(
            input_frame,
            background=self.colors['dark_element'],
            foreground=self.colors['white']
        )
        self.port_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Button-Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Scan-Button als normalen tk.Button statt ttk.Button
        self.scan_button = tk.Button(
            button_frame,
            text="Scan starten",
            command=self.start_scan,
            bg=self.colors['petrol'],
            fg=self.colors['white'],
            activebackground=self.colors['light_petrol'],
            activeforeground=self.colors['white'],
            relief='flat',  # flaches Design
            cursor='hand2'  # Hand-Cursor beim Hover
        )
        self.scan_button.grid(row=0, column=0)

        # Optional: Hover-Effekt
        def on_enter(e):
            self.scan_button['background'] = self.colors['light_petrol']

        def on_leave(e):
            self.scan_button['background'] = self.colors['petrol']

        self.scan_button.bind("<Enter>", on_enter)
        self.scan_button.bind("<Leave>", on_leave)
        
        # Ergebnis-Frame
        result_frame = ttk.LabelFrame(main_frame, text="Scan-Ergebnisse", padding="5")
        result_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        result_frame.grid_columnconfigure(0, weight=1)
        result_frame.grid_rowconfigure(0, weight=1)
        
        # Ergebnis-Anzeige
        self.result_text = scrolledtext.ScrolledText(result_frame)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status-Frame
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.S), pady=(5, 0))
        status_frame.grid_columnconfigure(0, weight=1)
        
        # Status-Anzeige
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

    def on_closing(self):
        """Wird beim Schließen des Fensters aufgerufen"""
        try:
            # 1. Speichere Scan-Konfiguration
            self.scan_config.ip_address = self.ip_var.get()
            self.scan_config.port = self.get_selected_port()
            save_scan_config(self.scan_config)

            # 2. Speichere Fenster-Konfiguration
            is_zoomed = False
            if platform.system() == 'Windows':
                try:
                    is_zoomed = self.root.state() == 'zoomed'
                except:
                    pass
            
            window_size = "800x600"  # Standard-Größe
            window_position = None    # Standard-Position
            
            if not is_zoomed:
                x = self.root.winfo_x()
                y = self.root.winfo_y()
                
                # Prüfe ob Position sinnvoll ist
                if x >= 0 and y >= 0:
                    current_geometry = self.root.geometry()
                    window_size = current_geometry.split('+')[0]
                    window_position = (x, y)
                    
                    print(f"Speichere Fenstergeometrie: {window_size} at ({x}, {y})")
            
            # Speichere Fenster-Konfiguration mit korrekten Keyword-Argumenten
            save_config(
                self.ip_var.get(),
                self.get_selected_port(),
                window_size=window_size,
                window_position=window_position,
                last_export_path=getattr(self, 'last_export_path', None)
            )
                
        except Exception as e:
            print(f"Fehler beim Speichern der Konfigurationen: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.root.destroy()

    def reset_window_position(self):
        """Setzt das Fenster zurück in die Bildschirmmitte"""
        # Berechne Zentrum
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Setze Fenster zurück
        self.root.state('normal')  # Beende Vollbildmodus
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def update_widget_colors(self, bg_color, fg_color):
        """Aktualisiert die Farben aller Widgets"""
        # Aktualisiere Styles
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color)
        self.style.configure('TButton',
            background=self.colors['petrol'],
            foreground=self.colors['white']
        )
        self.style.configure('TLabelframe', background=bg_color, foreground=fg_color)
        self.style.configure('TLabelframe.Label', background=bg_color, foreground=fg_color)
        
        # Aktualisiere ScrolledText
        self.result_text.configure(
            background=self.colors['light_sand'] if bg_color == self.colors['deep_blue'] else self.colors['deep_blue'],
            foreground=fg_color,
            insertbackground=self.colors['petrol']
        )

    def fill_port_list(self):
        """Füllt die Port-Liste"""
        try:
            ports = get_common_bacnet_ports()
            port_list = [f"{port} ({desc})" for port, desc in ports]
            
            # Aktualisiere die Werte in der Combobox
            self.port_combo.configure(values=port_list)
            
            # Setze den letzten verwendeten Wert oder den ersten in der Liste
            last_port = self.config.get('last_port')
            if last_port:
                for port_str in port_list:
                    if str(last_port) in port_str:
                        self.port_combo.set(port_str)
                        break
                else:  # Wenn der letzte Port nicht in der Liste ist
                    self.port_combo.set(port_list[0] if port_list else "47808 (Standard BACnet Port)")
            elif port_list:
                self.port_combo.set(port_list[0])
            else:
                self.port_combo.set("47808 (Standard BACnet Port)")
                
            # Aktualisiere die GUI
            self.root.update()
            
        except Exception as e:
            print(f"Fehler in fill_port_list: {e}")
            # Setze einen Standardwert im Fehlerfall
            self.port_combo.set("47808 (Standard BACnet Port)")
    
    def on_ip_selected(self, event=None):
        """Wird aufgerufen, wenn eine neue IP ausgewählt wird"""
        try:
            selected_ip = self.ip_var.get()
            selected_port = self.get_selected_port()
            print(f"Speichere neue IP-Auswahl: {selected_ip}")
            save_config(selected_ip, selected_port)
        except Exception as e:
            print(f"Fehler beim Speichern der IP-Auswahl: {e}")
    
    def on_port_selected(self, event=None):
        """Wird aufgerufen, wenn ein neuer Port ausgewählt wird"""
        try:
            selected_ip = self.ip_var.get()
            selected_port = self.get_selected_port()
            print(f"Speichere neue Port-Auswahl: {selected_port}")
            save_config(selected_ip, selected_port)
        except Exception as e:
            print(f"Fehler beim Speichern der Port-Auswahl: {e}")
    
    def get_selected_port(self):
        """Extrahiert den Port-Wert aus der Combo-Box-Auswahl"""
        try:
            port_str = self.port_combo.get()  # Verwende direkt die Combobox statt der Variable
            if not port_str:  # Wenn kein Wert ausgewählt ist
                return 47808  # Standard BACnet Port als Fallback
            
            # Extrahiere den Port aus dem String (z.B. "47808 (Standard BACnet Port)")
            port = port_str.split()[0]  # Nimm den ersten Teil vor dem Leerzeichen
            return int(port)
        except (IndexError, ValueError):
            print("Fehler beim Lesen des Ports, verwende Standard-Port 47808")
            return 47808  # Standard BACnet Port als Fallback
    
    def create_menu(self):
        """Erstellt die Menüleiste"""
        
        # Erstelle die benutzerdefinierte Menüleiste
        self.menubar = CustomMenuBar(  # Speichere als Instanzvariable
            self.root,
            bg_color=self.colors['dark_element'],
            fg_color=self.colors['white'],
            active_bg=self.colors['petrol'],
            active_fg=self.colors['white']
        )
        self.menubar.grid(row=0, column=0, sticky='new')

        # Datei-Menü
        file_menu = self.menubar.add_menu("Datei")
        
        # Export-Untermenü erstellen
        export_menu = tk.Menu(
            file_menu,
            tearoff=0,
            bg=self.colors['dark_element'],
            fg=self.colors['white'],
            activebackground=self.colors['petrol'],
            activeforeground=self.colors['white']
        )
        
        # Export-Untermenü zum Datei-Menü hinzufügen
        file_menu.add_cascade(label="Exportieren als", menu=export_menu)
        
        # Export-Optionen hinzufügen
        export_menu.add_command(label="CSV", command=self.export_csv)
        export_menu.add_command(label="Excel Binary (.xlsb)", command=self.export_excel)
        
        file_menu.add_separator()
        file_menu.add_command(
            label="Beenden",
            command=self.on_closing
        )

        # Einstellungen-Menü
        settings_menu = self.menubar.add_menu("Einstellungen")
        settings_menu.add_command(
            label="Scan-Einstellungen",
            command=self.show_settings_dialog
        )

        # Ansicht-Menü
        view_menu = self.menubar.add_menu("Ansicht")
        view_menu.add_command(
            label="Fenster zentrieren",
            command=self.reset_window_position
        )
        view_menu.add_separator()
        view_menu.add_command(
            label="Theme wechseln",
            command=self.toggle_theme
        )

        # Hilfe-Menü
        help_menu = self.menubar.add_menu("Hilfe")
        help_menu.add_command(
            label="Über",
            command=self.show_about
        )

        #Scan laden
        file_menu.add_command(
        label="Scan laden",
        command=self.load_scan
        )

    def show_about(self):
        """Zeigt Informationen über die Anwendung"""
        messagebox.showinfo(
            "Über BACnet Scanner",
            "BACnet Scanner\nVersion 1.0\n\n"
            "Ein Tool zum Scannen von BACnet-Geräten im Netzwerk."
        )

    def toggle_theme(self):
        """Wechselt zwischen Hell- und Dunkel-Modus"""
        if self.root.cget('bg') == self.colors['deep_blue']:
            # Wechsel zu Hell-Modus
            self.apply_theme('light')
        else:
            # Wechsel zu Dunkel-Modus
            self.apply_theme('dark')
   
    def apply_theme(self, theme):
        """Wendet das ausgewählte Theme an"""
        if theme == 'light':
            bg_color = self.colors['light_sand']
            fg_color = self.colors['deep_blue']
            element_bg = self.colors['white']
        else:
            bg_color = self.colors['deep_blue']
            fg_color = self.colors['white']
            element_bg = self.colors['dark_element']
        
        # Aktualisiere Styles
        self.style.configure('.', background=bg_color, foreground=fg_color)
        self.root.configure(bg=bg_color)
        
        # Aktualisiere ScrolledText
        self.result_text.configure(
            background=element_bg,
            foreground=fg_color
        )
        
        # Aktualisiere Comboboxen mit den neuen Farben
        self.ip_combo.configure(background=element_bg)
        self.port_combo.configure(background=element_bg)

    def export_excel(self):
        """Exportiert die Scan-Ergebnisse als Excel-Datei"""
        if not self.networks:
            messagebox.showwarning(
                "Keine Daten",
                "Es wurden noch keine Geräte gescannt. Bitte führen Sie zuerst einen Scan durch."
            )
            return
        
        from excel_exporter import export_to_excel  # Import am Anfang der Datei oder hier
        success, message = export_to_excel(self.devices, self.networks)
        if success:
            messagebox.showinfo("Export erfolgreich", message)
        else:
            messagebox.showerror("Export fehlgeschlagen", message)        

    def start_scan(self):
        """Startet den BACnet-Scan"""
        # Speichere aktuelle Auswahl vor dem Scan
        save_config(self.ip_var.get(), self.get_selected_port())
        
        self.result_text.delete(1.0, tk.END)
        self.status_var.set("Scan läuft...")
        self.scan_button.configure(state='disabled')
        self.root.update()
        
        try:
            # Erstelle Scan-Konfiguration
            scan_config = ScanConfig(
                ip_address=self.ip_var.get(),
                port=self.get_selected_port()
            )
            
            # Wenn Einstellungen bereits konfiguriert wurden, übernehme sie
            if hasattr(self, 'scan_config'):
                scan_config.properties = self.scan_config.properties
            
            # Hole aktivierte Properties
            enabled_properties = scan_config.get_enabled_properties()
            print(f"\nAktivierte Properties für Scan:")
            for prop in enabled_properties:
                print(f"- {prop.name} (ID: {prop.bacnet_id})")
            
            # Scanner initialisieren
            from bacnet_scanner import BACnetScanner
            scanner = BACnetScanner(
                local_ip=scan_config.ip_address,
                bacnet_port=scan_config.port
            )
            
            # Konfiguriere Scanner-Parameter nach der Initialisierung
            scanner.timeout = scan_config.timeout
            scanner.attempts = scan_config.attempts
            
            # Scan durchführen mit aktivierten Properties
            self.devices, self.networks = scanner.scan(properties=enabled_properties)
            
            # Ergebnisse anzeigen
            self.display_results({
                'timestamp': datetime.now().isoformat(),
                'config': scan_config.to_dict(),
                'devices': self.devices,
                'networks': self.networks
            })
            
            self.status_var.set("Scan abgeschlossen")
            
        except Exception as e:
            self.result_text.insert(tk.END, f"Fehler beim Scan: {str(e)}")
            self.status_var.set("Fehler aufgetreten")
            self.devices = {}
            self.networks = {}
        
        finally:
            self.scan_button.configure(state='normal')
            self.root.update()

    def load_scan(self):
        """Lädt einen gespeicherten Scan"""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir="scan_results"
        )
        
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    result = json.load(f)
                
                # Prüfe und konvertiere das Format
                if isinstance(result, dict):
                    # Stelle sicher, dass alle notwendigen Schlüssel existieren
                    if 'devices' not in result:
                        result['devices'] = {}
                    if 'networks' not in result:
                        result['networks'] = {}
                    if 'config' not in result:
                        result['config'] = {}
                    
                    # Konvertiere 'local_ip' zu 'ip_address' wenn nötig
                    if 'local_ip' in result['config']:
                        result['config']['ip_address'] = result['config']['local_ip']
                    
                    # Setze Standardwerte wenn Felder fehlen
                    if not result['config'].get('ip_address'):
                        result['config']['ip_address'] = self.ip_combo.get() or ''
                    if not result['config'].get('port'):
                        result['config']['port'] = result['config'].get('bacnet_port', self.get_selected_port() or 47808)
                    
                    # Setze Zeitstempel wenn nicht vorhanden
                    if 'timestamp' not in result:
                        result['timestamp'] = datetime.now().isoformat()

                    # Speichere die Daten
                    self.current_result = result
                    self.devices = result['devices']
                    self.networks = result['networks']
                    
                    # Aktualisiere die GUI-Elemente
                    if result['config'].get('ip_address'):
                        self.ip_combo.set(result['config']['ip_address'])
                    if result['config'].get('port'):
                        port_str = f"{result['config']['port']} (BACnet Port)"
                        self.port_combo.set(port_str)

                    # Zeige die Ergebnisse an
                    self.display_results(result)
                    self.status_var.set("Scan geladen")
                else:
                    raise ValueError("Ungültiges JSON-Format")
                
            except json.JSONDecodeError:
                messagebox.showerror("Fehler", "Die Datei enthält kein gültiges JSON-Format")
            except ValueError as e:
                messagebox.showerror("Fehler", str(e))
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Laden der Datei: {str(e)}")

    def display_results(self, result):
        """Zeigt die Scan-Ergebnisse an"""
        self.result_text.delete(1.0, tk.END)
        
        try:
            # Zeige Scan-Informationen
            self.result_text.insert(tk.END, f"Scan durchgeführt am: {result.get('timestamp', 'Unbekannt')}\n")
            
            # Verwende entweder ip_address oder local_ip
            ip = result.get('config', {}).get('ip_address') or result.get('config', {}).get('local_ip', 'Unbekannt')
            port = result.get('config', {}).get('port') or result.get('config', {}).get('bacnet_port', 'Unbekannt')
            
            self.result_text.insert(tk.END, f"IP-Adresse: {ip}\n")
            self.result_text.insert(tk.END, f"Port: {port}\n\n")
            
            # Zeige gefundene Geräte
            self.result_text.insert(tk.END, "Gefundene Geräte:\n")
            devices = result.get('devices', {})
            if devices:
                for ip, device_id in devices.items():
                    id_str = f" (Device-ID: {device_id})" if device_id is not None else " (Keine Device-ID)"
                    self.result_text.insert(tk.END, f"- {ip}{id_str}\n")
            else:
                self.result_text.insert(tk.END, "Keine Geräte gefunden\n")
            
            # Zeige Netzwerke
            self.result_text.insert(tk.END, "\nGefundene Netzwerke:\n")
            networks = result.get('networks', {})
            if networks:
                for subnet, devices in networks.items():
                    self.result_text.insert(tk.END, f"\nNetzwerk {subnet}:\n")
                    for ip, device_id in devices:
                        id_str = f" (Device-ID: {device_id})" if device_id is not None else " (Keine Device-ID)"
                        self.result_text.insert(tk.END, f"  - {ip}{id_str}\n")
            else:
                self.result_text.insert(tk.END, "Keine Netzwerke gefunden\n")
                
        except Exception as e:
            self.result_text.insert(tk.END, f"Fehler beim Anzeigen der Ergebnisse: {str(e)}\n")
            self.result_text.insert(tk.END, f"Rohdaten: {str(result)}\n")

    def show_settings_dialog(self):
        """Öffnet den Einstellungen-Dialog"""
        print("\nÖffne Einstellungen:")
        print("Aktueller Zustand der Properties:")
        for name, prop in self.scan_config.properties.items():
            print(f"- {name}: {prop.enabled}")
            
        dialog = ScanSettingsDialog(self.root, self.scan_config)
        self.root.wait_window(dialog.dialog)
        
        # Nach dem Schließen des Dialogs
        print("\nNach Schließen des Dialogs:")
        print("Zustand der Properties:")
        for name, prop in self.scan_config.properties.items():
            print(f"- {name}: {prop.enabled}")

    

def start_gui():
    root = tk.Tk()
    app = BACnetScannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    start_gui()