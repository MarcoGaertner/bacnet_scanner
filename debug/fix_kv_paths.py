import re
from pathlib import Path

def fix_kv_paths(file_path):
    """Korrigiert Builder.load_file() Aufrufe"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Prüfe ob Builder.load_file verwendet wird
    if 'Builder.load_file(' not in content:
        return False
    
    # Prüfe ob bereits get_resource_path verwendet wird
    if 'Builder.load_file(get_resource_path(' in content:
        print(f"   ⏭️  Bereits korrigiert: {file_path.name}")
        return False
    
    # Füge Import hinzu, falls noch nicht vorhanden
    needs_import = False
    if 'from ui.utils import get_resource_path' not in content:
        needs_import = True
        
        # Finde die richtige Stelle für den Import (nach kivy.lang import)
        if 'from kivy.lang import Builder' in content:
            content = content.replace(
                'from kivy.lang import Builder',
                'from kivy.lang import Builder\nfrom ui.utils import get_resource_path'
            )
        elif 'from kivy.lang.builder import Builder' in content:
            content = content.replace(
                'from kivy.lang.builder import Builder',
                'from kivy.lang.builder import Builder\nfrom ui.utils import get_resource_path'
            )
        else:
            # Füge am Anfang der Imports hinzu (nach den ersten imports)
            lines = content.split('\n')
            import_index = -1
            for i, line in enumerate(lines):
                if line.startswith('from ') or line.startswith('import '):
                    import_index = i
                    break
            
            if import_index >= 0:
                lines.insert(import_index + 1, 'from ui.utils import get_resource_path')
                content = '\n'.join(lines)
    
    # Ersetze Builder.load_file Aufrufe
    # Pattern 1: Builder.load_file('path')
    pattern1 = r"Builder\.load_file$'([^']+)'"
    replacement1 = r"Builder.load_file(get_resource_path('\1'))"
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: Builder.load_file("path")
    pattern2 = r'Builder\.load_file$"([^"]+)"'
    replacement2 = r'Builder.load_file(get_resource_path("\1"))'
    content = re.sub(pattern2, replacement2, content)
    
    # Pattern 3: Builder.load_file(variable) - nur warnen, nicht ändern
    pattern3 = r'Builder\.load_file$([a-zA-Z_][a-zA-Z0-9_]*)'
    if re.search(pattern3, content):
        print(f"   ⚠️  WARNUNG: Variable in Builder.load_file() gefunden in {file_path.name}")
        print(f"      Bitte manuell prüfen!")
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    # debug/fix_kv_paths.py -> gehe 1 Ebene hoch zum project_root
    project_root = Path(__file__).parent.parent
    
    print("=" * 70)
    print("🔧 Builder.load_file() Korrektur-Tool")
    print("=" * 70)
    print(f"\n📂 Projekt-Root: {project_root}\n")
    print("🔍 Suche nach Builder.load_file() Aufrufen...\n")
    
    fixed_files = []
    skipped_files = []
    
    # Scanne alle Python-Dateien
    for py_file in project_root.rglob('*.py'):
        # Überspringe bestimmte Verzeichnisse
        if any(skip in str(py_file) for skip in ['venv', '.venv', '__pycache__', 'debug', 'installer', 'build', 'dist']):
            continue
        
        # Überspringe ui/utils.py selbst
        if py_file.name == 'utils.py' and 'ui' in str(py_file):
            continue
        
        try:
            if fix_kv_paths(py_file):
                fixed_files.append(py_file)
                print(f"✅ Korrigiert: {py_file.relative_to(project_root)}")
        except Exception as e:
            skipped_files.append((py_file, str(e)))
            print(f"❌ Fehler: {py_file.relative_to(project_root)}")
            print(f"   Grund: {e}")
    
    print("\n" + "=" * 70)
    print("📊 ZUSAMMENFASSUNG")
    print("=" * 70)
    
    if fixed_files:
        print(f"\n✅ {len(fixed_files)} Datei(en) erfolgreich korrigiert:")
        for f in fixed_files:
            print(f"   - {f.relative_to(project_root)}")
    else:
        print("\n✅ Keine Dateien mussten korrigiert werden!")
    
    if skipped_files:
        print(f"\n⚠️  {len(skipped_files)} Datei(en) übersprungen (Fehler):")
        for f, err in skipped_files:
            print(f"   - {f.relative_to(project_root)}: {err}")
    
    print("\n" + "=" * 70)
    print("✨ Fertig!")
    print("=" * 70)
    
    if fixed_files:
        print("\n💡 Nächste Schritte:")
        print("   1. Überprüfe die Änderungen")
        print("   2. Teste die Anwendung:")
        print("      cd debug")
        print("      python main_debug.py")
        print("   3. Baue die .exe neu:")
        print("      cd installer")
        print("      python build_installer.py 4.1 --debug")

if __name__ == '__main__':
    main()