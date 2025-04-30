import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ip_selector import get_network_interfaces
from port_selector import get_common_bacnet_ports
from bacnet_scanner import scan_bacnet
from csv_exporter import export_to_csv
import os
import platform
import ctypes
from PIL import Image, ImageTk

class BACnetScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BACnet Scanner")
        self.root.geometry("800x600")
        
        # Initialisiere Datenspeicher
        self.devices = {}
        self.networks = {}
        
        # Erstelle Menü
        self.create_menu()
        # Setze das Fenster-Icon
        try:
            # Basis-Pfad für Icons
            icon_path = os.path.join(os.path.dirname(__file__), 'graphics', 'siemens_logo_icon.ico')
            
            if platform.system() == 'Windows':
                # Windows-spezifischer Code
                myappid = 'siemens.bacnet.scanner.1.0'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
                
                # Setze Icons für verschiedene Größen
                self.root.iconbitmap(default=icon_path)
                
                # Zusätzlich: Setze das Icon explizit für die Taskleiste
                hwnd = ctypes.windll.kernel32.GetConsoleWindow()
                if hwnd:
                    ctypes.windll.user32.SendMessageW(hwnd, 0x80, 0, icon_path)
            else:
                # Für andere Betriebssysteme
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, photo)
                
        except Exception as e:
            print(f"Fehler beim Laden des Icons: {e}")

        # Konfiguriere Root-Grid für Skalierung
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Hauptframe
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Konfiguriere Main-Frame-Grid für Skalierung
        main_frame.grid_columnconfigure(1, weight=1)  # Zweite Spalte skalierbar
        main_frame.grid_rowconfigure(4, weight=1)     # Ergebnisfeld skalierbar
        
        # Oberer Frame für Eingabefelder
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N), pady=(0, 10))
        input_frame.grid_columnconfigure(1, weight=1)
        
        # IP-Auswahl
        ttk.Label(input_frame, text="IP-Adresse:").grid(row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.ip_var = tk.StringVar()
        self.ip_combo = ttk.Combobox(input_frame, textvariable=self.ip_var)
        self.ip_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Port-Auswahl
        ttk.Label(input_frame, text="BACnet Port:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(input_frame, textvariable=self.port_var)
        self.port_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Button-Frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        button_frame.grid_columnconfigure(0, weight=1)
        
        # Scan-Button
        self.scan_button = ttk.Button(button_frame, text="Scan starten", command=self.start_scan)
        self.scan_button.grid(row=0, column=0)
        
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
        
        # Listen füllen
        self.fill_ip_list()
        self.fill_port_list()
        
        # Minimale Fenstergröße setzen
        self.root.update()
        self.root.minsize(400, 300)
    
    def fill_ip_list(self):
        """Füllt die IP-Adressliste"""
        interfaces = get_network_interfaces()
        ip_list = [ip for ip, desc in interfaces]
        self.ip_combo['values'] = ip_list
        if ip_list:
            self.ip_combo.set(ip_list[0])
            
    def fill_port_list(self):
        """Füllt die Port-Liste"""
        ports = get_common_bacnet_ports()
        port_list = [f"{port} ({desc})" for port, desc in ports]
        self.port_combo['values'] = port_list
        if port_list:
            self.port_combo.set(port_list[0])
    
    def get_selected_port(self):
        """Extrahiert den Port-Wert aus der Combo-Box-Auswahl"""
        port_str = self.port_var.get().split()[0]
        return int(port_str, 0)
    
    def create_menu(self):
        """Erstellt die Menüleiste"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Datei-Menü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Datei", menu=file_menu)
        
        # Export-Untermenü
        export_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Exportieren als", menu=export_menu)
        export_menu.add_command(label="CSV", command=self.export_csv)
        
        file_menu.add_separator()
        file_menu.add_command(label="Beenden", command=self.root.quit)
        
        # Hilfe-Menü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Hilfe", menu=help_menu)
        help_menu.add_command(label="Über", command=self.show_about)

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

    def show_about(self):
        """Zeigt Informationen über die Anwendung"""
        messagebox.showinfo(
            "Über BACnet Scanner",
            "BACnet Scanner\nVersion 1.0\n\n"
            "Ein Tool zum Scannen von BACnet-Geräten im Netzwerk."
        )

    def start_scan(self):
        """Startet den BACnet-Scan"""
        self.result_text.delete(1.0, tk.END)
        self.status_var.set("Scan läuft...")
        self.scan_button.state(['disabled'])
        self.root.update()
        
        try:
            import sys
            from io import StringIO
            old_stdout = sys.stdout
            result_stream = StringIO()
            sys.stdout = result_stream
            
            # Scan durchführen
            self.devices = {}  # Reset devices
            self.networks = {}  # Reset networks
            scan_bacnet(self.ip_var.get(), self.get_selected_port())
            
            # Ergebnisse verarbeiten
            sys.stdout = old_stdout
            scan_output = result_stream.getvalue()
            self.result_text.insert(tk.END, scan_output)
            
            # Extrahiere die Geräte-Informationen aus der Ausgabe
            self.parse_scan_results(scan_output)
            
            self.status_var.set("Scan abgeschlossen")
            
        except Exception as e:
            self.result_text.insert(tk.END, f"Fehler beim Scan: {str(e)}")
            self.status_var.set("Fehler aufgetreten")
        
        finally:
            self.scan_button.state(['!disabled'])
            self.root.update()

    def parse_scan_results(self, scan_output):
        """Extrahiert die Geräte-Informationen aus der Scan-Ausgabe"""
        self.networks = {}
        current_subnet = None
        
        for line in scan_output.split('\n'):
            if line.startswith('Subnet'):
                current_subnet = line.split(':')[0].replace('Subnet ', '')
                self.networks[current_subnet] = []
            elif line.startswith('- ') and current_subnet:
                parts = line.replace('- ', '').split()
                ip = parts[0]
                device_id = None
                if len(parts) > 1:
                    try:
                        device_id = int(parts[1].strip('()').split(':')[1])
                    except:
                        pass
                self.networks[current_subnet].append((ip, device_id))

def start_gui():
    root = tk.Tk()
    app = BACnetScannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    start_gui()