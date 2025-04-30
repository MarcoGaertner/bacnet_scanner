from bacnet_scanner import scan_bacnet
from ip_selector import select_ip
from port_selector import select_port
from gui import BACnetScannerGUI
import tkinter as tk

def console_mode():
    """Startet den Scanner im Konsolenmodus"""
    selected_ip = select_ip()
    selected_port = select_port()
    scan_bacnet(selected_ip, selected_port)

def gui_mode():
    """Startet den Scanner im GUI-Modus"""
    root = tk.Tk()
    app = BACnetScannerGUI(root)
    root.mainloop()

def main():
    print("BACnet Scanner")
    print("1. Konsolen-Version")
    print("2. GUI-Version")
    
    while True:
        choice = input("\nBitte wählen Sie (1/2): ")
        if choice == "1":
            console_mode()
            break
        elif choice == "2":
            gui_mode()
            break
        else:
            print("Ungültige Eingabe! Bitte 1 oder 2 wählen.")

if __name__ == "__main__":
    main()