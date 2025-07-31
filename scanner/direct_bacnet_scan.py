#!/usr/bin/env python3
"""
Minimaler BACnet-Scanner für Unternehmensumgebungen
"""

import socket
import struct
import json
import sys
import time
import logging
from ipaddress import IPv4Network

# Logging konfigurieren
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                   handlers=[logging.StreamHandler(), logging.FileHandler('bacnet_scan.log')])
logger = logging.getLogger('MinimalBACnetScanner')

# BACnet-Konstanten
BACNET_PORT = 47808
BACNET_HEADER = bytes.fromhex('81 0b 00 0c 01 20 ff ff 00 ff 10 08')  # Standard Who-Is

def get_broadcast_addresses(ip_address):
    """Berechnet mehrere mögliche Broadcast-Adressen für bessere Abdeckung"""
    addresses = []
    
    # Standard-Broadcast (letztes Oktett auf 255)
    ip_parts = ip_address.split('.')
    addresses.append(f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.255")
    
    # Versuche, Subnetz zu ermitteln und korrekte Broadcast-Adresse zu berechnen
    try:
        # Standard /24 Subnetzmaske annehmen
        network = IPv4Network(f"{ip_address}/24", strict=False)
        addresses.append(str(network.broadcast_address))
    except:
        pass
        
    # Globaler Broadcast als letzte Option
    addresses.append('255.255.255.255')
    
    return addresses

def scan_for_devices(ip_address, timeout=15):
    """Führt einen BACnet-Scan mit mehreren Fallback-Optionen durch"""
    devices = []
    device_map = {}  # Zum Vermeiden von Duplikaten
    
    logger.info(f"Starte BACnet-Scan von IP {ip_address}")
    
    try:
        # Socket erstellen mit Broadcast-Fähigkeit
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Versuche an verschiedene Adressen zu binden
        bind_successful = False
        bind_addresses = [ip_address, '0.0.0.0', '']
        
        for addr in bind_addresses:
            try:
                sock.bind((addr, 0))  # Bind zu einem dynamischen Port
                logger.info(f"Socket erfolgreich an {addr} gebunden")
                bind_successful = True
                break
            except Exception as e:
                logger.warning(f"Konnte nicht an {addr} binden: {e}")
        
        if not bind_successful:
            logger.error("Konnte Socket nicht binden. Bricht ab.")
            return []
        
        # Hole mögliche Broadcast-Adressen
        broadcast_addresses = get_broadcast_addresses(ip_address)
        
        # Sende Who-Is an alle Broadcast-Adressen
        for addr in broadcast_addresses:
            logger.info(f"Sende Who-Is an {addr}:{BACNET_PORT}")
            
            # Sende mehrere Who-Is-Pakete für bessere Zuverlässigkeit
            for _ in range(3):
                try:
                    sock.sendto(BACNET_HEADER, (addr, BACNET_PORT))
                    time.sleep(0.2)  # Kurze Pause zwischen Paketen
                except Exception as e:
                    logger.error(f"Fehler beim Senden an {addr}: {e}")
        
        # Warte auf Antworten
        end_time = time.time() + timeout
        sock.settimeout(0.5)  # 500ms Timeout für einzelne recv-Aufrufe
        
        logger.info(f"Warte auf Antworten für {timeout} Sekunden...")
        
        while time.time() < end_time:
            try:
                data, addr = sock.recvfrom(1024)
                logger.debug(f"Daten empfangen von {addr[0]}:{addr[1]}, Länge: {len(data)}")
                
                # Prüfe auf BACnet-Header
                if len(data) > 6 and data[0] == 0x81:
                    # Prüfe auf I-Am (unconfirmed service choice 0)
                    if len(data) > 8 and data[6] & 0xF0 == 0x10 and data[7] == 0x00:
                        # Extrahieren der Device-ID
                        device_id = None
                        if len(data) > 12:
                            try:
                                device_id = struct.unpack('>I', data[10:14])[0]
                            except:
                                try:
                                    device_id = struct.unpack('>I', data[8:12])[0]
                                except:
                                    device_id = None
                        
                        if device_id is not None:
                            device_key = f"{addr[0]}:{device_id}"
                            if device_key not in device_map:
                                device_info = {
                                    "address": addr[0],
                                    "id": device_id,
                                    "name": f"Device {device_id}",
                                    "type": "Unknown"
                                }
                                device_map[device_key] = device_info
                                devices.append(device_info)
                                logger.info(f"Neues Gerät gefunden: {device_info}")
            
            except socket.timeout:
                # Timeout ist normal, wir warten weiter
                pass
            except Exception as e:
                logger.error(f"Fehler beim Empfangen: {e}")
        
        sock.close()
        logger.info(f"Scan abgeschlossen. {len(devices)} Geräte gefunden.")
        
    except Exception as e:
        logger.error(f"Fehler beim Scannen: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    # HIER: Zweite Scan-Phase - an korrekter Position außerhalb des except-Blocks
    logger.info("Starte zweite Scan-Phase: Abrufen von Geräteinformationen...")
    
    print(f"\nRufe detaillierte Informationen von {len(devices)} Geräten ab...")

    for device in devices:
        device_ip = device["address"]
        device_id = device["id"]
        
        # Geräteinformationen abrufen
        additional_info = get_device_info(device_ip, device_id)
        if additional_info:
            # Aktualisiere die Geräteinformationen
            if 'Object_Name' in additional_info:
                device["name"] = additional_info['Object_Name']
            if 'Model_Name' in additional_info:
                device["model"] = additional_info['Model_Name']
                device["type"] = additional_info['Model_Name']
            if 'Vendor_Name' in additional_info:
                device["vendor"] = additional_info['Vendor_Name']
            if 'Description' in additional_info:
                device["description"] = additional_info['Description']
    
    return devices

def read_device_property(ip_address, device_id, property_id):
    """
    Liest eine spezifische Property von einem BACnet-Gerät
    """
    # BACnet Virtual Link Control (BVLC)
    bvlc = bytes.fromhex('81 0a 00 1c')
    
    # NPDU mit Destination Network = None
    npdu = bytes.fromhex('01 04')
    
    # APDU (Application Protocol Data Unit)
    apdu_type = 0x0a  # Confirmed-REQ
    max_segments_accepted = 0x05  # 16 Segmente
    max_apdu_accepted = 0x04      # 1024 Bytes
    invoke_id = 0x01
    service_choice = 0x0c         # ReadProperty
    apdu_header = bytes([apdu_type | (max_segments_accepted << 4), max_apdu_accepted, invoke_id, service_choice])
    
    # Object Identifier (Context Tag 0)
    object_type = 8  # Device
    object_id = struct.pack('>I', (object_type << 22) | device_id)
    object_tag = bytes([0x0c]) + object_id
    
    # Property Identifier (Context Tag 1)
    property_tag = bytes([0x19, property_id])
    
    # Zusammensetzen der APDU
    apdu = apdu_header + object_tag + property_tag
    
    # Paketzusammenbau
    packet_length = len(npdu) + len(apdu) + 4
    bvlc = bytes([0x81, 0x0a]) + struct.pack('>H', packet_length)
    packet = bvlc + npdu + apdu
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        sock.sendto(packet, (ip_address, BACNET_PORT))
        
        data, _ = sock.recvfrom(1024)
        sock.close()
        
        # Überprüfe auf eine gültige Antwort
        if len(data) > 14:
            # Suche nach der Application Tag für CharacterString (Typ 7)
            # Dies ist vereinfachtes Parsing und könnte für verschiedene Antwortformate erweitert werden
            for i in range(14, len(data) - 2):
                if (data[i] >> 4) == 7:  # Application Tag für CharacterString
                    string_len = data[i+1]
                    if i + 2 + string_len <= len(data):
                        try:
                            return data[i+2:i+2+string_len].decode('utf-8')
                        except:
                            return data[i+2:i+2+string_len].decode('latin1')
        return None
    except Exception as e:
        logger.error(f"Fehler beim Lesen der Property {property_id} von {ip_address}: {e}")
        return None

def send_read_property_request(ip_address, device_id, property_id, object_id=8, object_instance=None):
    """
    Sendet eine ReadProperty-Anfrage an ein BACnet-Gerät
    
    Args:
        ip_address: IP-Adresse des Geräts
        device_id: Device-ID des BACnet-Geräts
        property_id: ID der zu lesenden Eigenschaft
        object_id: Objekt-Typ (8 = Device)
        object_instance: Instanz des Objekts (falls None, wird device_id verwendet)
    """
    if object_instance is None:
        object_instance = device_id
        
    # APDU-Typ 0x0a = Confirmed-REQ mit Service Choice 0x0c = ReadProperty
    apdu_type = 0x0a
    service_choice = 0x0c
    
    # NPDU mit Destination Network = None
    npdu = bytes.fromhex('01 00')
    
    # Object Identifier (Context Tag 0)
    object_id_bytes = struct.pack('>I', (object_id << 22) | object_instance)
    object_tag = bytes([0x0c]) + object_id_bytes
    
    # Property Identifier (Context Tag 1)
    property_tag = bytes([0x19, property_id])
    
    # Zusammensetzen der APDU
    apdu = bytes([apdu_type, 0x01, service_choice]) + object_tag + property_tag
    
    # BACnet Virtual Link Control (BVLC)
    bvlc_length = len(npdu) + len(apdu) + 4
    bvlc = bytes([0x81, 0x0a]) + struct.pack('>H', bvlc_length)
    
    # Zusammensetzen des kompletten Pakets
    packet = bvlc + npdu + apdu
    
    try:
        # Socket erstellen
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)  # 2 Sekunden Timeout
        
        # Anfrage senden
        sock.sendto(packet, (ip_address, BACNET_PORT))
        
        # Auf Antwort warten
        data, addr = sock.recvfrom(1024)
        sock.close()
        
        # Überprüfen, ob eine gültige Antwort empfangen wurde
        if len(data) > 0 and data[0] == 0x81:
            # Hier müsste das Parsing der Property-Werte implementiert werden
            # Dies ist komplex und hängt vom Datentyp der Property ab
            if len(data) > 15:  # Einfache Heuristik für String-Werte
                # Suche nach Application Tag für CharacterString (Typ 7)
                for i in range(12, len(data) - 2):
                    if (data[i] >> 4) == 7:  # Application Tag für CharacterString
                        string_len = data[i+1]
                        if i + 2 + string_len <= len(data):
                            try:
                                return data[i+2:i+2+string_len].decode('utf-8')
                            except:
                                return data[i+2:i+2+string_len].decode('latin1')
        
        return None
    except Exception as e:
        logger.error(f"Fehler beim Lesen der Property {property_id} von {ip_address}: {e}")
        return None

def get_device_info(ip_address, device_id):
    """
    Ruft erweiterte Geräteinformationen über ReadProperty ab
    """
    properties_to_read = [
        ('Object_Name', 77),
        ('Description', 28),
        ('Model_Name', 70),
        ('Vendor_Name', 121)
    ]
    
    device_info = {}
    for prop_name, prop_id in properties_to_read:
        response = send_read_property_request(ip_address, device_id, prop_id)
        if response:
            device_info[prop_name] = response
            logger.info(f"Gerät {device_id} - {prop_name}: {response}")
    
    return device_info

def main():
    if len(sys.argv) < 5:
        print(f"Verwendung: {sys.argv[0]} <ip_address> <port> <timeout> <output_file>")
        return 1
    
    ip_address = sys.argv[1]
    timeout = int(sys.argv[3])
    output_file = sys.argv[4]
    
    devices = scan_for_devices(ip_address, timeout)
    
    with open(output_file, 'w') as f:
        json.dump(devices, f, indent=2)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())