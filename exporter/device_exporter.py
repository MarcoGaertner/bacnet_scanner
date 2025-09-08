# exporter/device_exporter.py
import os, csv, datetime
from typing import List, Dict, Any
import pandas as pd

from scanner.storage import DatabaseStorage

# Mapping von Export-"key" => Wert-Extraktion aus (device_row / props)
def _extract_value(key: str, device: Dict[str, Any], props: Dict[str, Any]) -> Any:
    # häufige BACnet-Keys
    if key in props:
        return props.get(key)

    # zusammengesetzte / spezielle Felder
    if key == "device_id" or key == "instance":
        return device.get("device_id")
    if key == "address_port":
        # nimm die gespeicherte Adresse "ip:port", sonst aus ipv4 + udp_port zusammenbauen
        addr = device.get("address") or ""
        if addr:
            return addr
        ip = props.get("ipv4") or ""
        port = props.get("udp_port") or ""
        return f"{ip}:{port}".strip(":")
    if key == "standort":
        # Alias für location (deutsche Beschriftung)
        return props.get("location")
    if key == "mac-address":
        return props.get("mac-address") or props.get("mac_address")
    if key == "firmware_revision_serial_number":
        return props.get("firmware_revision_serial_number") or props.get("serial-number")
    if key == "betriebs_url_dup":
        return props.get("operational-url")
    # Netzwerkfelder, falls du sie als eigene Spalten in devices ergänzt hast,
    # landen derzeit in props (aus dem Scan); wir lesen sie einfach aus props:
    if key in ("ipv4", "subnet_mask", "router", "udp_port"):
        return props.get(key, "")

    # Fallback
    return props.get(key, "")

def build_rows_for_scan(scan_id: int, selected_keys: List[str], storage: DatabaseStorage) -> List[Dict[str, Any]]:
    data = storage.get_scan_details(scan_id) or {}
    rows: List[Dict[str, Any]] = []
    for d in data.get("devices", []):
        props = (d.get("properties") or {})
        row = {}
        for k in selected_keys:
            row[k] = _extract_value(k, d, props)
        rows.append(row)
    return rows

def export_csv(path: str, rows: List[Dict[str, Any]], headers: List[str], header_labels: Dict[str, str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([header_labels.get(h, h) for h in headers])
        for r in rows:
            writer.writerow([r.get(h, "") for h in headers])

def export_xlsx(path: str, rows: List[Dict[str, Any]], headers: List[str], header_labels: Dict[str, str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # schöner: Labels als Spaltenüberschriften
    df = pd.DataFrame(rows)
    rename_map = {h: header_labels.get(h, h) for h in headers}
    # Nur gewählte Reihenfolge
    df = df[headers].rename(columns=rename_map)
    df.to_excel(path, index=False)
