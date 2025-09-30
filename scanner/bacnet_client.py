"""
BACnet Client-Implementierung für das Scannen von BACnet-Geräten über IP
"""

import os
import json
import asyncio
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from bacpypes3.debugging import ModuleLogger
from bacpypes3.argparse import SimpleArgumentParser
from bacpypes3.app import Application
from bacpypes3.apdu import ErrorRejectAbortNack
from bacpypes3.constructeddata import AnyAtomic
from typing import Callable, Optional

# Debugging konfigurieren
_debug = 0
_log = ModuleLogger(globals())

class BACnetClient:
    """
    BACnet-Client zum Scannen von Geräten über BACnet/IP
    """
    
    def __init__(self, scan_mode='standard'):
        """Initialisierung des BACnet-Clients"""
        self.app = None
        self.scan_result = {
            "timestamp": "",
            "device_count": 0,
            "devices": []
        }
        self.scan_mode = scan_mode  # 'standard', 'extended', 'full'
        self.on_progress: Optional[Callable[[float, str], None]] = None
        
        # Grundlegende Eigenschaften, die immer abgefragt werden
        self.basic_properties = [
            "object-name",
            "description",
            "location",
            "vendor-name",
            "model-name",
            "firmware-revision"
        ]
        
        # Erweiterte Eigenschaften für detailliertere Informationen
        self.extended_properties = [
            "application-software-version",
            "protocol-version",
            "protocol-revision-number",
            "system-status",
            "vendor-identifier",
            "max-apdu-length-accepted",
            "segmentation-supported",
            "local-time",
            "local-date",
            "utc-offset",
            "daylight-savings-status"
        ]
        
        # Umfangreiche Eigenschaften für vollständige Geräteinfo
        self.full_properties = [
            "protocol-services-supported",
            "protocol-object-types-supported",
            "device-address-binding",
            "database-revision",
            "apdu-timeout",
            "number-of-apdu-retries",
            "max-master",
            "max-info-frames",
            "device-uuid",
            "backup-failure-timeout",
            "active-cov-subscriptions",
            "last-restore-time",
            "object-list"  # Liste aller Objekte im Gerät
        ]
        
        # Eigenschaften, die tatsächlich abgefragt werden sollen, basierend auf scan_mode
        self.properties_to_query = self.get_properties_for_mode(scan_mode)




    def _progress(self, pct: float, msg: str):
        try:
            if self.on_progress:
                self.on_progress(float(pct), str(msg))
        except Exception:
            pass



    
    def get_properties_for_mode(self, mode):
        """
        Gibt die Liste der Eigenschaften zurück, die für den angegebenen Modus abgefragt werden sollen
        """
        if mode == 'standard':
            return self.basic_properties
        elif mode == 'extended':
            return self.basic_properties + self.extended_properties
        elif mode == 'full':
            return self.basic_properties + self.extended_properties + self.full_properties
        else:
            return self.basic_properties
    
    def set_scan_mode(self, mode):
        """
        Setzt den Scan-Modus und aktualisiert die Liste der abzufragenden Eigenschaften
        """
        self.scan_mode = mode
        self.properties_to_query = self.get_properties_for_mode(mode)
        print(f"Scan-Modus auf '{mode}' gesetzt mit {len(self.properties_to_query)} Properties")
    
    async def initialize(self, ip_address: str, port: int, subnet_mask: str = "/24") -> bool:
        """Initialisiert den BACnet-Client mit den angegebenen Einstellungen"""
        try:
            # Argumente für die BACnet-Anwendung konfigurieren
            sys_args = ["--address", f"{ip_address}{subnet_mask}:{port}"]
            
            parser = SimpleArgumentParser()
            args = parser.parse_args(sys_args)
            
            # BACnet-Anwendung erstellen
            self.app = Application.from_args(args)
            
            return True
        except Exception as e:
            print(f"Fehler bei der Initialisierung des BACnet-Clients: {e}")
            return False
    
    async def scan_network(self) -> Dict[str, Any]:
        if not self.app:
            raise RuntimeError("BACnet-Client wurde nicht initialisiert")

        self.scan_result["timestamp"] = datetime.datetime.now().isoformat()
        self.scan_result["scan_mode"] = self.scan_mode

        try:
            self._progress(0.10, "Sende WhoIs …")
            i_am_devices = await self.app.who_is()

            if not i_am_devices:
                self.scan_result["device_count"] = 0
                self.scan_result["devices"] = []
                self._progress(1.0, "Keine BACnet-Geräte gefunden")
                return self.scan_result

            total = len(i_am_devices)
            self.scan_result["devices"] = []
            self.scan_result["device_count"] = total
            self._progress(0.20, f"{total} Gerät(e) gefunden – lese Eigenschaften …")

            # map progress from 0.20 .. 0.95 across devices
            start_p, end_p = 0.20, 0.95

            for idx, device in enumerate(i_am_devices, start=1):
                device_id = device.iAmDeviceIdentifier[1]
                device_address = str(device.pduSource)

                self._progress(
                    start_p + (end_p - start_p) * (idx - 1) / max(1, total),
                    f"Gerät {idx}/{total} ({device_id}) …"
                )

                device_info = await self.scan_device(device_address, device_id)

                self.scan_result["devices"].append({
                    "device_id": device_id,
                    "address": device_address,
                    "properties": device_info
                })

                self._progress(
                    start_p + (end_p - start_p) * (idx) / max(1, total),
                    f"Gerät {idx}/{total} abgeschlossen"
                )

            self._progress(0.96, "Scan abgeschlossen – aufräumen …")
            return self.scan_result
        except Exception as e:
            self._progress(1.0, f"Fehler: {e}")
            print(f"Fehler beim Scannen des Netzwerks: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    async def scan_device(self, device_address: str, device_id: int) -> Dict[str, Any]:
        """Ein Gerät scannen und seine Eigenschaften abfragen"""
        print(f"\nAbfrage des Geräts {device_id} ({device_address})...")
        print(f"Scan-Modus: {self.scan_mode} mit {len(self.properties_to_query)} Properties")
        
        device_info = {}
        
        # Device-Objekt mit der entsprechenden ID abfragen
        device_objid = f"device,{device_id}"
        
        for prop in self.properties_to_query:
            try:
                # Eigenschaft lesen
                response = await self.app.read_property(
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
                # BACnet-spezifischer Fehler (Property nicht unterstützt/unbekannt)
                err_str = str(err)
                device_info[prop] = f"Nicht unterstützt: {err_str}"
                print(f"  {prop}: {err_str}")
            except Exception as e:
                # Allgemeiner Fehler
                device_info[prop] = f"Fehler: {e}"
                print(f"  {prop}: Fehler beim Lesen - {e}")
        
        # Wenn im vollständigen Scan-Modus, versuche die Objekte des Geräts zu lesen
        if self.scan_mode == 'full' and device_info.get('object-list') not in [None, 'Nicht unterstützt']:
            try:
                objects = await self._read_object_list(device_address, device_id)
                device_info['objects'] = objects
            except Exception as e:
                device_info['objects'] = f"Fehler beim Lesen der Objektliste: {e}"
        
        print("-" * 60)
        return device_info
    
    async def _read_object_list(self, device_address: str, device_id: int) -> List[Dict[str, Any]]:
        """Liest die Objektliste des Geräts und sammelt Basisinformationen zu jedem Objekt"""
        print(f"  Lese Objektliste des Geräts {device_id}...")
        
        # Objekt-Liste lesen
        device_objid = f"device,{device_id}"
        
        try:
            # Zunächst die Größe der Objektliste abfragen
            response = await self.app.read_property(
                device_address,
                device_objid,
                "object-list[0]"  # Index 0 gibt die Länge des Arrays zurück
            )
            
            if not response:
                return []
            
            list_size = response.get_value() if isinstance(response, AnyAtomic) else int(response)
            print(f"  Gefundene Objekte: {list_size}")
            
            objects = []
            
            # Jedes Objekt in der Liste abfragen (maximal 20 zur Demonstration)
            max_objects = min(list_size, 20)
            for i in range(1, max_objects + 1):
                try:
                    # Objekt-ID aus der Liste lesen
                    response = await self.app.read_property(
                        device_address,
                        device_objid,
                        f"object-list[{i}]"
                    )
                    
                    if not response:
                        continue
                    
                    obj_id = response.get_value() if isinstance(response, AnyAtomic) else response
                    obj_type, obj_instance = obj_id
                    
                    # Nur grundlegende Informationen zu jedem Objekt sammeln
                    obj_info = {
                        "type": obj_type,
                        "instance": obj_instance,
                        "id": f"{obj_type},{obj_instance}"
                    }
                    
                    # Versuche den Namen des Objekts abzufragen
                    try:
                        name_response = await self.app.read_property(
                            device_address,
                            f"{obj_type},{obj_instance}",
                            "object-name"
                        )
                        obj_info["name"] = name_response.get_value() if isinstance(name_response, AnyAtomic) else name_response
                    except:
                        obj_info["name"] = "Unbekannt"
                    
                    # Versuche den Present-Value des Objekts abzufragen (wenn vorhanden)
                    try:
                        value_response = await self.app.read_property(
                            device_address,
                            f"{obj_type},{obj_instance}",
                            "present-value"
                        )
                        obj_info["present-value"] = value_response.get_value() if isinstance(value_response, AnyAtomic) else value_response
                    except:
                        pass  # Nicht alle Objekte haben einen Present-Value
                    
                    objects.append(obj_info)
                except Exception as e:
                    print(f"  Fehler beim Lesen des Objekts {i}: {e}")
            
            if list_size > max_objects:
                print(f"  Hinweis: Nur die ersten {max_objects} von {list_size} Objekten wurden abgefragt.")
            
            return objects
        except Exception as e:
            print(f"  Fehler beim Lesen der Objektliste: {e}")
            return []
    
    def close(self):
        """Schließt den BACnet-Client"""
        if self.app:
            self.app.close()
            self.app = None