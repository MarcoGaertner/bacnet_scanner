import os
import re
from pathlib import Path

def fix_relative_imports(file_path, module_base):
    """Konvertiert relative Imports zu absoluten Imports"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern für relative Imports
    patterns = [
        # from .module import something
        (r'from\s+\.([a-zA-Z0-9_.]+)\s+import', f'from {module_base}.\\1 import'),
        # from ..module import something
        (r'from\s+\.\.([a-zA-Z0-9_.]+)\s+import', lambda m: f'from {get_parent_module(module_base)}.{m.group(1)} import'),
        # from . import something
        (r'from\s+\.\s+import', f'from {module_base} import'),
    ]
    
    for pattern, replacement in patterns:
        if callable(replacement):
            content = re.sub(pattern, replacement, content)
        else:
            content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def get_parent_module(module_path):
    """Gibt das Parent-Modul zurück"""
    parts = module_path.split('.')
    if len(parts) > 1:
        return '.'.join(parts[:-1])
    return module_path

def get_module_base(file_path, project_root):
    """Ermittelt den Modul-Basispfad"""
    rel_path = file_path.relative_to(project_root)
    parts = list(rel_path.parts[:-1])  # Ohne Dateiname
    return '.'.join(parts) if parts else ''

def scan_and_fix(project_root):
    """Scannt alle Python-Dateien und korrigiert relative Imports"""
    project_root = Path(project_root)
    fixed_files = []
    
    # Verzeichnisse zum Scannen
    scan_dirs = ['ui', 'core', 'scanner', 'exporter']
    
    for dir_name in scan_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            continue
        
        for py_file in dir_path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            
            module_base = get_module_base(py_file, project_root)
            
            if fix_relative_imports(py_file, module_base):
                fixed_files.append(py_file)
                print(f"✅ Korrigiert: {py_file.relative_to(project_root)}")
    
    return fixed_files

if __name__ == '__main__':
    # debug/fix_imports.py -> gehe 1 Ebene hoch zum project_root
    project_root = Path(__file__).parent.parent
    
    print("🔍 Suche nach relativen Imports...\n")
    print(f"📂 Projekt-Root: {project_root}\n")
    
    fixed = scan_and_fix(project_root)
    
    if fixed:
        print(f"\n✅ {len(fixed)} Dateien korrigiert!")
        print("\n💡 Bitte überprüfe die Änderungen und teste die Anwendung.")
    else:
        print("\n✅ Keine relativen Imports gefunden!")