def main():
    print("BACnet Scanner")
    print("1. Konsolen-Version")
    print("2. GUI-Version")
    
    while True:
        choice = input("\nBitte wählen Sie (1/2): ")
        if choice == "1":
            from bacnet_scanner import scan_bacnet
            from ip_selector import select_ip
            from port_selector import select_port
            
            selected_ip = select_ip()
            selected_port = select_port()
            scan_bacnet(selected_ip, selected_port)
            break
            
        elif choice == "2":
            from gui import start_gui
            start_gui()
            break
            
        else:
            print("Ungültige Eingabe! Bitte 1 oder 2 wählen.")

if __name__ == "__main__":
    main()