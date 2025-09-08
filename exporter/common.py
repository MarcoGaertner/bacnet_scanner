# exporter/common.py
import os
from typing import List, Dict, Any
from scanner.storage import DatabaseStorage

def _extract_value(key: str, device: Dict[str, Any], props: Dict[str, Any]) -> Any:
    # 1) direkter Treffer in Props
    if key in props:
        return props.get(key)

    # 2) zusammengesetzte / Spezial-Felder
    if key in ("device_id", "instance"):
        return device.get("device_id")

    if key == "address_port":
        addr = device.get("address") or ""
        if addr:
            return addr
        ip = props.get("ipv4") or ""
        port = props.get("udp_port") or ""
        return f"{ip}:{port}".strip(":")

    if key == "standort":  # Alias deutsch
        return props.get("location")

    if key == "mac-address":
        return props.get("mac-address") or props.get("mac_address")

    if key == "firmware_revision_serial_number":
        return props.get("firmware_revision_serial_number") or props.get("serial-number")

    if key == "betriebs_url_dup":
        return props.get("operational-url")

    if key in ("ipv4", "subnet_mask", "router", "udp_port"):
        return props.get(key, "")

    # 3) Fallback
    return props.get(key, "")

def build_rows_for_scan(scan_id: int, selected_keys: List[str], storage: DatabaseStorage) -> List[Dict[str, Any]]:
    data = storage.get_scan_details(scan_id) or {}
    rows: List[Dict[str, Any]] = []
    for d in data.get("devices", []) or []:
        props = (d.get("properties") or {})
        row = {k: _extract_value(k, d, props) for k in selected_keys}
        rows.append(row)
    return rows

def get_enabled_headers_and_labels(storage: DatabaseStorage) -> (List[str], Dict[str, str]):
    """Liest export_properties aus der DB, liefert aktivierte Keys + Label-Mapping."""
    props = storage.get_export_properties()
    headers = [p["key"] for p in props if int(p["enabled"]) == 1]
    header_labels = {p["key"]: p["label"] for p in props}
    return headers, header_labels

def ensure_dir_for(path: str):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
