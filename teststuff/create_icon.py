from PIL import Image
import os
from io import BytesIO

def create_multisize_icon():
    # Pfad zum Quellbild
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(script_dir, 'graphics', 'siemens_logo_icon.png')
    target_path = os.path.join(script_dir, 'graphics', 'siemens_logo_icon.ico')
    
    try:
        # Öffne das Quellbild
        img = Image.open(source_path)
        
        # Konvertiere zu RGBA
        if img.mode != 'RGBA':
            print(f"Konvertiere von {img.mode} zu RGBA...")
            img = img.convert('RGBA')
        
        # Definiere die gewünschten Größen
        sizes = [(16,16), (32,32), (48,48), (64,64), (128,128)]
        
        # Erstelle separate Bilder für jede Größe
        images = []
        for size in sizes:
            print(f"Erstelle Größe {size}...")
            resized_img = img.resize(size, Image.Resampling.LANCZOS)
            # Speichere jede Größe als separate PNG im Speicher
            img_bytes = BytesIO()
            resized_img.save(img_bytes, format='PNG')
            images.append((size[0], img_bytes.getvalue()))
        
        # Speichere als ICO mit allen Größen
        print("Speichere ICO-Datei...")
        with open(target_path, 'wb') as ico:
            # Schreibe ICO Header
            ico.write(bytes([0, 0, 1, 0, len(images), 0]))
            
            # Schreibe Directory Entries
            offset = 6 + 16 * len(images)
            for size, _ in images:
                ico.write(bytes([
                    size,  # Width
                    size,  # Height
                    0,     # Color palette
                    0,     # Reserved
                    1, 0,  # Color planes
                    32, 0, # Bits per pixel
                ]))
                # Größe und Offset werden später eingefügt
                ico.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
            
            # Schreibe die Bilddaten
            for i, (_, img_data) in enumerate(images):
                # Update Directory Entry
                size = len(img_data)
                ico.seek(6 + 16 * i + 8)
                ico.write(size.to_bytes(4, 'little'))
                ico.write(offset.to_bytes(4, 'little'))
                
                # Schreibe Bilddaten
                ico.seek(offset)
                ico.write(img_data)
                offset += size
        
        print(f"\nIcon erfolgreich erstellt: {target_path}")
        
        # Überprüfe das erstellte Icon
        with Image.open(target_path) as icon:
            sizes = icon.info.get('sizes', set())
            print(f"Verfügbare Icon-Größen: {sizes}")
            
    except Exception as e:
        print(f"\nFehler beim Erstellen des Icons:")
        print(f"Typ: {type(e).__name__}")
        print(f"Details: {str(e)}")

if __name__ == "__main__":
    create_multisize_icon()