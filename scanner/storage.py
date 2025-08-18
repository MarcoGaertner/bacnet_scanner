"""
Datenbankgestützter Speicher für BACnet-Scan-Ergebnisse
"""

import os
import json
import sqlite3
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

class DatabaseStorage:
    """Speicher für BACnet-Scan-Ergebnisse in SQLite-Datenbank"""
    
    def __init__(self, db_path="data/scan_results/bacnet_scans.db"):
        """Initialisiert die Datenbank"""
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._initialize_db()
    
    def _initialize_db(self):
        """Erstellt die benötigten Tabellen, wenn sie nicht existieren"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Scans-Tabelle für die Scan-Metadaten
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            scan_mode TEXT,
            device_count INTEGER,
            description TEXT,
            connection_info TEXT  -- JSON-serialisierte Verbindungsinfo
        )
        ''')
        
        # Geräte-Tabelle
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            device_id INTEGER,
            scan_id INTEGER,
            address TEXT,
            properties TEXT,  -- JSON-serialisierte Eigenschaften
            PRIMARY KEY (device_id, scan_id),
            FOREIGN KEY (scan_id) REFERENCES scans (scan_id) ON DELETE CASCADE
        )
        ''')
        
        # Objekt-Tabelle für detaillierte Objektdaten
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS objects (
            object_id TEXT,
            device_id INTEGER,
            scan_id INTEGER,
            object_type TEXT,
            object_instance INTEGER,
            object_name TEXT,
            present_value TEXT,
            additional_properties TEXT,  -- JSON-serialisierte zusätzliche Eigenschaften
            PRIMARY KEY (object_id, device_id, scan_id),
            FOREIGN KEY (device_id, scan_id) REFERENCES devices (device_id, scan_id) ON DELETE CASCADE
        )
        ''')
        
        # Aktiviere Foreign Key Constraints
        cursor.execute("PRAGMA foreign_keys = ON")
        
        conn.commit()
        conn.close()
        
        print(f"Datenbank initialisiert: {self.db_path}")
    
    def save_scan_result(self, scan_result: Dict[str, Any], description: str = "", connection_info: Dict[str, Any] = None) -> int:
        """
        Speichert das Scan-Ergebnis in der Datenbank
        
        Args:
            scan_result: Das Scan-Ergebnis als Dictionary
            description: Eine Beschreibung des Scans
            connection_info: Informationen zur Verbindung (optional)
            
        Returns:
            Die ID des gespeicherten Scans
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Scan-Metadaten speichern
            cursor.execute('''
            INSERT INTO scans (timestamp, scan_mode, device_count, description, connection_info)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                scan_result.get("timestamp", datetime.datetime.now().isoformat()),
                scan_result.get("scan_mode", "standard"),
                scan_result.get("device_count", 0),
                description,
                json.dumps(connection_info) if connection_info else None
            ))
            
            scan_id = cursor.lastrowid
            
            # Geräte speichern
            for device in scan_result.get("devices", []):
                device_id = device.get("device_id")
                address = device.get("address")
                
                # Objektliste aus den Properties extrahieren
                properties = device.get("properties", {}).copy()
                objects = properties.pop("objects", []) if "objects" in properties else []
                
                # Gerät speichern
                cursor.execute('''
                INSERT INTO devices (device_id, scan_id, address, properties)
                VALUES (?, ?, ?, ?)
                ''', (device_id, scan_id, address, json.dumps(properties)))
                
                # Objekte speichern
                for obj in objects:
                    obj_type = obj.get("type")
                    obj_instance = obj.get("instance")
                    obj_id = f"{obj_type},{obj_instance}"
                    obj_name = obj.get("name", "")
                    
                    # Present-Value und zusätzliche Eigenschaften trennen
                    present_value = ""
                    additional_props = obj.copy()
                    if "present-value" in additional_props:
                        present_value = str(additional_props.pop("present-value"))
                    
                    cursor.execute('''
                    INSERT INTO objects (object_id, device_id, scan_id, object_type, object_instance, 
                                        object_name, present_value, additional_properties)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        obj_id, device_id, scan_id, obj_type, obj_instance,
                        obj_name, present_value, json.dumps(additional_props)
                    ))
            
            conn.commit()
            print(f"Scan mit ID {scan_id} erfolgreich gespeichert")
            return scan_id
            
        except Exception as e:
            conn.rollback()
            print(f"Fehler beim Speichern des Scan-Ergebnisses: {e}")
            import traceback
            traceback.print_exc()
            return -1
            
        finally:
            conn.close()
    
    def get_scan_list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Gibt eine Liste der letzten Scans zurück
        
        Args:
            limit: Maximale Anzahl zurückzugebender Scans
            
        Returns:
            Liste von Scan-Metadaten
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Zugriff auf Spalten über Namen
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT scan_id, timestamp, scan_mode, device_count, description
            FROM scans
            ORDER BY timestamp DESC
            LIMIT ?
            ''', (limit,))
            
            scans = []
            for row in cursor.fetchall():
                scans.append(dict(row))
            
            return scans
            
        except Exception as e:
            print(f"Fehler beim Abrufen der Scan-Liste: {e}")
            return []
            
        finally:
            conn.close()
    
    def get_scan_details(self, scan_id: int) -> Optional[Dict[str, Any]]:
        """
        Gibt die Details eines Scans zurück
        
        Args:
            scan_id: ID des Scans
            
        Returns:
            Vollständige Scan-Details oder None, wenn der Scan nicht existiert
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Zugriff auf Spalten über Namen
        cursor = conn.cursor()
        
        try:
            # Scan-Metadaten abrufen
            cursor.execute('SELECT * FROM scans WHERE scan_id = ?', (scan_id,))
            scan_row = cursor.fetchone()
            if not scan_row:
                return None
            
            scan_data = dict(scan_row)
            
            # Connection-Info deserialisieren, falls vorhanden
            if scan_data.get('connection_info'):
                try:
                    scan_data['connection_info'] = json.loads(scan_data['connection_info'])
                except:
                    scan_data['connection_info'] = {}
            
            # Geräte abrufen
            cursor.execute('SELECT * FROM devices WHERE scan_id = ?', (scan_id,))
            devices = []
            for device_row in cursor.fetchall():
                device_data = dict(device_row)
                
                # Properties deserialisieren
                try:
                    device_data['properties'] = json.loads(device_data['properties'])
                except:
                    device_data['properties'] = {}
                
                # Objekte abrufen
                cursor.execute('''
                SELECT * FROM objects 
                WHERE device_id = ? AND scan_id = ?
                ''', (device_data['device_id'], scan_id))
                
                objects = []
                for obj_row in cursor.fetchall():
                    obj_data = dict(obj_row)
                    
                    # Zusätzliche Eigenschaften deserialisieren
                    try:
                        additional_props = json.loads(obj_data['additional_properties'])
                    except:
                        additional_props = {}
                    
                    # Objekt zusammenbauen
                    obj = {
                        "id": obj_data['object_id'],
                        "type": obj_data['object_type'],
                        "instance": obj_data['object_instance'],
                        "name": obj_data['object_name']
                    }
                    
                    # Present-Value hinzufügen, wenn vorhanden
                    if obj_data['present_value']:
                        obj["present-value"] = obj_data['present_value']
                    
                    # Weitere Eigenschaften hinzufügen
                    obj.update(additional_props)
                    objects.append(obj)
                
                # Objekte zu den Geräteeigenschaften hinzufügen
                if objects:
                    device_data['properties']['objects'] = objects
                
                devices.append(device_data)
            
            # Vollständiges Scan-Ergebnis zusammenbauen
            scan_result = {
                "scan_id": scan_data['scan_id'],
                "timestamp": scan_data['timestamp'],
                "scan_mode": scan_data['scan_mode'],
                "device_count": scan_data['device_count'],
                "description": scan_data['description'],
                "devices": devices
            }
            
            return scan_result
            
        except Exception as e:
            print(f"Fehler beim Abrufen der Scan-Details für ID {scan_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
            
        finally:
            conn.close()
    
    def delete_scan(self, scan_id: int) -> bool:
        """
        Löscht einen Scan aus der Datenbank
        
        Args:
            scan_id: ID des zu löschenden Scans
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Foreign Key Constraints aktiv - Löschen des Scans löscht auch verknüpfte Einträge
            cursor.execute('DELETE FROM scans WHERE scan_id = ?', (scan_id,))
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            conn.rollback()
            print(f"Fehler beim Löschen des Scans {scan_id}: {e}")
            return False
            
        finally:
            conn.close()
    
    def delete_old_scans(self, keep_count: int = 100) -> int:
        """
        Löscht alte Scans und behält nur die neuesten keep_count
        
        Args:
            keep_count: Anzahl der zu behaltenden Scans
            
        Returns:
            Anzahl der gelöschten Scans
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # IDs der zu behaltenden Scans abrufen
            cursor.execute('''
            SELECT scan_id FROM scans
            ORDER BY timestamp DESC
            LIMIT ?
            ''', (keep_count,))
            
            keep_ids = [row[0] for row in cursor.fetchall()]
            
            if not keep_ids:
                return 0
            
            # Zählen, wie viele Scans gelöscht werden
            cursor.execute('''
            SELECT COUNT(*) FROM scans WHERE scan_id NOT IN ({})
            '''.format(','.join('?' * len(keep_ids))), keep_ids)
            
            to_delete_count = cursor.fetchone()[0]
            
            # Alle Scans löschen, die nicht in keep_ids sind
            # Foreign Key Constraints sorgen dafür, dass auch die zugehörigen Geräte und Objekte gelöscht werden
            cursor.execute('''
            DELETE FROM scans WHERE scan_id NOT IN ({})
            '''.format(','.join('?' * len(keep_ids))), keep_ids)
            
            conn.commit()
            print(f"{to_delete_count} alte Scans gelöscht")
            return to_delete_count
            
        except Exception as e:
            conn.rollback()
            print(f"Fehler beim Löschen alter Scans: {e}")
            return 0
            
        finally:
            conn.close()
    
    def get_device_history(self, device_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Gibt die Scan-Historie für ein bestimmtes Gerät zurück
        
        Args:
            device_id: Die BACnet-Geräte-ID
            limit: Maximale Anzahl der zurückzugebenden Scan-Einträge
            
        Returns:
            Liste von Scan-Einträgen für das Gerät
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT s.scan_id, s.timestamp, s.scan_mode, d.address, d.properties
            FROM devices d
            JOIN scans s ON d.scan_id = s.scan_id
            WHERE d.device_id = ?
            ORDER BY s.timestamp DESC
            LIMIT ?
            ''', (device_id, limit))
            
            history = []
            for row in cursor.fetchall():
                entry = dict(row)
                try:
                    entry['properties'] = json.loads(entry['properties'])
                except:
                    entry['properties'] = {}
                history.append(entry)
                
            return history
            
        except Exception as e:
            print(f"Fehler beim Abrufen der Geräte-Historie für {device_id}: {e}")
            return []
            
        finally:
            conn.close()
    
    def search_devices(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Durchsucht die Datenbank nach Geräten, die den Suchbegriff im Namen, 
        der Beschreibung oder dem Standort enthalten
        
        Args:
            search_term: Der Suchbegriff
            
        Returns:
            Liste der passenden Geräte
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Suche nach dem Begriff in den JSON-Properties
            # Hinweis: SQLite kann nicht direkt in JSON-Feldern suchen, daher verwenden wir LIKE
            cursor.execute('''
            SELECT d.device_id, d.address, d.properties, s.scan_id, s.timestamp
            FROM devices d
            JOIN scans s ON d.scan_id = s.scan_id
            WHERE d.properties LIKE ?
            ORDER BY s.timestamp DESC
            ''', (f'%{search_term}%',))
            
            results = []
            seen_devices = set()  # Um Duplikate zu vermeiden
            
            for row in cursor.fetchall():
                device_data = dict(row)
                device_id = device_data['device_id']
                
                # Wenn wir dieses Gerät bereits gesehen haben, überspringen wir es
                if device_id in seen_devices:
                    continue
                
                # Properties deserialisieren
                try:
                    device_data['properties'] = json.loads(device_data['properties'])
                except:
                    device_data['properties'] = {}
                
                # Prüfen, ob der Begriff tatsächlich im Namen, der Beschreibung oder dem Standort vorkommt
                name = device_data['properties'].get('object-name', '')
                description = device_data['properties'].get('description', '')
                location = device_data['properties'].get('location', '')
                
                if (search_term.lower() in name.lower() or 
                    search_term.lower() in description.lower() or 
                    search_term.lower() in location.lower()):
                    seen_devices.add(device_id)
                    results.append(device_data)
            
            return results
            
        except Exception as e:
            print(f"Fehler bei der Gerätesuche für '{search_term}': {e}")
            return []
            
        finally:
            conn.close()