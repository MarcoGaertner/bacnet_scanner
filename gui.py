import tkinter as tk
from tkinter import ttk, scrolledtext
from ip_selector import get_network_interfaces
from port_selector import get_common_bacnet_ports
from bacnet_scanner import scan_bacnet

class BACnetScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("BACnet Scanner")
        self.root.geometry("800x600")
        
        # Hauptframe
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # IP-Auswahl
        ttk.Label(main_frame, text="IP-Adresse:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.ip_var = tk.StringVar()
        self.ip_combo = ttk.Combobox(main_frame, textvariable=self.ip_var)
        self.ip_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Port-Auswahl
        ttk.Label(main_frame, text="BACnet Port:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(main_frame, textvariable=self.port_var)
        self.port_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Scan-Button
        self.scan_button = ttk.Button(main_frame, text="Scan starten", command=self.start_scan)
        self.scan_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Ergebnis-Anzeige
        ttk.Label(main_frame, text="Scan-Ergebnisse:").grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        self.result_text = scrolledtext.ScrolledText(main_frame, width=70, height=20)
        self.result_text.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Status-Anzeige
        self.status_var = tk.StringVar()
        self.status_var.set("Bereit")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=5, column=0, columnspan=2, pady=5)
        
        # Listen füllen
        self.fill_ip_list()
        self.fill_port_list()
        
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
        port_str = self.port_var.get().split()[0]  # Nimmt nur die Portnummer
        return int(port_str, 0)  # Basis 0 erlaubt hex und dezimal
    
    def start_scan(self):
        """Startet den BACnet-Scan"""
        self.result_text.delete(1.0, tk.END)
        self.status_var.set("Scan läuft...")
        self.scan_button.state(['disabled'])
        self.root.update()
        
        try:
            # Redirect stdout to capture print output
            import sys
            from io import StringIO
            old_stdout = sys.stdout
            result_stream = StringIO()
            sys.stdout = result_stream
            
            # Scan durchführen
            scan_bacnet(self.ip_var.get(), self.get_selected_port())
            
            # Ausgabe wiederherstellen und Ergebnisse anzeigen
            sys.stdout = old_stdout
            self.result_text.insert(tk.END, result_stream.getvalue())
            self.status_var.set("Scan abgeschlossen")
            
        except Exception as e:
            self.result_text.insert(tk.END, f"Fehler beim Scan: {str(e)}")
            self.status_var.set("Fehler aufgetreten")
        
        finally:
            self.scan_button.state(['!disabled'])
            self.root.update()

def start_gui():
    root = tk.Tk()
    app = BACnetScannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    start_gui()