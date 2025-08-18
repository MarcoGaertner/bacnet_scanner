"""
BACnet Scanner - sendet eine WhoIs-Anfrage und liest grundlegende Geräteeigenschaften
"""

import sys
import asyncio
import re

from bacpypes3.debugging import ModuleLogger
from bacpypes3.argparse import SimpleArgumentParser
from bacpypes3.app import Application
from bacpypes3.pdu import Address
from bacpypes3.apdu import WhoIsRequest, ErrorRejectAbortNack
from bacpypes3.constructeddata import AnyAtomic

# Debugging konfigurieren
_debug = 0
_log = ModuleLogger(globals())

# Eigenschaften, die abgefragt werden sollen
PROPERTIES_TO_QUERY = [
    "object-name",
    "description",
    "location",
    "vendor-name",
    "model-name",
    "firmware-revision"
]

async def scan_device(app, device_address, device_id):
    """Ein Gerät scannen und seine Eigenschaften abfragen"""
    print(f"\nAbfrage des Geräts {device_id} ({device_address})...")
    
    device_info = {}
    
    # Device-Objekt mit der entsprechenden ID abfragen
    device_objid = f"device,{device_id}"
    
    for prop in PROPERTIES_TO_QUERY:
        try:
            # Eigenschaft lesen
            response = await app.read_property(
                device_address,
                device_objid,
                prop
            )
            
            # Wert extrahieren
            if isinstance(response, AnyAtomic):
                value = response.get_value()
            else:
                value = response
            
            device_info[prop] = value
            print(f"  {prop}: {value}")
        except ErrorRejectAbortNack as err:
            device_info[prop] = f"Fehler: {err}"
            print(f"  {prop}: Fehler - {err}")
        except Exception as e:
            device_info[prop] = f"Fehler: {e}"
            print(f"  {prop}: Fehler beim Lesen - {e}")
    
    print("-" * 60)
    return device_info

async def main_async():
    """Hauptfunktion des BACnet-Scanners"""
    app = None
    
    try:
        # Kommandozeilenargumente verarbeiten
        parser = SimpleArgumentParser()
        
        # IP-Adresse und Port aus den Eingabeargumenten verarbeiten
        if len(sys.argv) > 1:
            ip_address = sys.argv[1]
            if len(sys.argv) > 2:
                port = sys.argv[2]
                # Original-Argumente entfernen
                sys.argv.pop(1)
                sys.argv.pop(1)
                # Korrektes Format für --address hinzufügen
                if '/' not in ip_address:
                    ip_address = f"{ip_address}/24"  # Standard-Subnetzmaske
                sys.argv.append("--address")
                sys.argv.append(f"{ip_address}:{port}")
            else:
                # Original-Argument entfernen
                sys.argv.pop(1)
                # Korrektes Format für --address hinzufügen
                if '/' not in ip_address:
                    ip_address = f"{ip_address}/24"
                sys.argv.append("--address")
                sys.argv.append(ip_address)
        
        args = parser.parse_args()
        
        # BACnet-Anwendung erstellen
        app = Application.from_args(args)
        
        print(f"BACnet-Scanner gestartet...")
        print("Sende WhoIs-Anfrage...")
        
        # WhoIs-Anfrage senden und Antworten sammeln
        i_am_devices = await app.who_is()
        
        # Überprüfen, ob Geräte gefunden wurden
        if not i_am_devices:
            print("\nKeine BACnet-Geräte gefunden.")
            return
        
        print(f"\nGefundene Geräte: {len(i_am_devices)}")
        print("-" * 60)
        
        # Für jedes Gerät Eigenschaften abfragen
        for device in i_am_devices:
            device_id = device.iAmDeviceIdentifier[1]
            device_address = str(device.pduSource)
            await scan_device(app, device_address, device_id)
            
    except Exception as e:
        print(f"Fehler: {e}")
        if _debug:
            import traceback
            traceback.print_exc()
    finally:
        if app:
            app.close()

def main():
    """Einstiegspunkt für den BACnet-Scanner"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\nProgramm durch Benutzer unterbrochen.")
    except Exception as e:
        print(f"\nFehler: {e}")

if __name__ == "__main__":
    main()