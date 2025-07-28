# styles/colors.py
class ThemeColors:
    # Helles Theme (Standard)
    LIGHT = {
        "SIDEBAR_BACKGROUND": (243/255, 243/255, 240/255, 1),  # RGB: 243 243 240
        "TAB_BACKGROUND": (1, 1, 1, 1),  # RGB: 255 255 255
        "TEXT_COLOR": (153/255, 153/255, 169/255, 1),  # #9999A9
        "HIGHLIGHT_COLOR": (0, 0.6, 0.6, 1),  # #009999
        "BACKGROUND": (1, 1, 1, 1),  # Hellgrau
        "CARD_BACKGROUND": (1, 1, 1, 1)  # Weiß
    }
    
    # Dunkles Theme
    DARK = {
        "SIDEBAR_BACKGROUND": (30/255, 30/255, 30/255, 1),  # Dunkelgrau
        "TAB_BACKGROUND": (50/255, 50/255, 50/255, 1),  # Etwas helleres Grau
        "TEXT_COLOR": (200/255, 200/255, 200/255, 1),  # Hellgrau Text
        "HIGHLIGHT_COLOR": (0, 0.8, 0.8, 1),  # Helleres #009999
        "BACKGROUND": (50/255, 50/255, 50/255, 1),  # Fast Schwarz
        "CARD_BACKGROUND": (40/255, 40/255, 40/255, 1)  # Dunkelgrau
    }
    
    # Aktuelles Theme (wird beim Laden gesetzt)
    current = {}

SIDEBAR_BACKGROUND = None
TAB_BACKGROUND = None 
TEXT_COLOR = None
HIGHLIGHT_COLOR = None
BACKGROUND = None
CARD_BACKGROUND = None
SIDEBAR_ITEM = None
SIDEBAR_ITEM_SELECTED = None
SIDEBAR_TEXT = None
TEXT_PRIMARY = None
PRIMARY = None

# Theme-Manager
class ThemeManager:
    @staticmethod
    def set_theme(theme_name="hell"):
        """Setzt das aktuelle Theme basierend auf dem Namen"""
        if theme_name.lower() == "dunkel":
            ThemeColors.current = ThemeColors.DARK
        else:  # "hell" oder default
            ThemeColors.current = ThemeColors.LIGHT
        
        # WICHTIG: Aktualisiere die globalen Variablen, um sie in KV-Dateien verfügbar zu machen
        # Diese Zeilen aktualisieren die Modulvariablen, damit sie in allen KV-Dateien aktuell sind
        global SIDEBAR_BACKGROUND, TAB_BACKGROUND, TEXT_COLOR, HIGHLIGHT_COLOR
        global BACKGROUND, CARD_BACKGROUND, SIDEBAR_ITEM, SIDEBAR_ITEM_SELECTED
        global SIDEBAR_TEXT, TEXT_PRIMARY, PRIMARY
        
        SIDEBAR_BACKGROUND = ThemeColors.current["SIDEBAR_BACKGROUND"]
        TAB_BACKGROUND = ThemeColors.current["TAB_BACKGROUND"]
        TEXT_COLOR = ThemeColors.current["TEXT_COLOR"] 
        HIGHLIGHT_COLOR = ThemeColors.current["HIGHLIGHT_COLOR"]
        BACKGROUND = ThemeColors.current["BACKGROUND"]
        CARD_BACKGROUND = ThemeColors.current["CARD_BACKGROUND"]
        
        # Legacy-Variablen ebenfalls aktualisieren
        SIDEBAR_ITEM = TAB_BACKGROUND
        SIDEBAR_ITEM_SELECTED = HIGHLIGHT_COLOR
        SIDEBAR_TEXT = TEXT_COLOR
        TEXT_PRIMARY = TEXT_COLOR
        PRIMARY = HIGHLIGHT_COLOR

def get_color_with_alpha(color_name, alpha):
    """Gibt eine Farbe aus dem aktuellen Theme mit angepasstem Alpha-Wert zurück"""
    if color_name in ThemeColors.current:
        color = ThemeColors.current[color_name]
        return (color[0], color[1], color[2], alpha)
    return (0, 0, 0, alpha)  # Fallback zu Schwarz mit angegebenem Alpha

# Initialisiere das Theme mit dem Standard "hell"
ThemeManager.set_theme("hell")

# Verzögerter Import - WICHTIG: Erst nach den Klassendefinitionen
def initialize_theme_from_config():
    try:
        from core.config import ConfigManager
        config = ConfigManager()
        ThemeManager.set_theme(config.get_setting("ui", "theme"))
    except ImportError:
        print("Hinweis: Config konnte nicht importiert werden. Verwende Standard-Theme.")
    except Exception as e:
        print(f"Fehler bei Theme-Initialisierung: {e}")

# Für Kompatibilität mit bestehenden Dateien
# Diese Variablen werden von ThemeManager aktualisiert
SIDEBAR_BACKGROUND = ThemeColors.current.get("SIDEBAR_BACKGROUND")
TAB_BACKGROUND = ThemeColors.current.get("TAB_BACKGROUND")
TEXT_COLOR = ThemeColors.current.get("TEXT_COLOR")
HIGHLIGHT_COLOR = ThemeColors.current.get("HIGHLIGHT_COLOR")
BACKGROUND = ThemeColors.current.get("BACKGROUND")
CARD_BACKGROUND = ThemeColors.current.get("CARD_BACKGROUND")

# Legacy-Variablen beibehalten
SIDEBAR_ITEM = TAB_BACKGROUND
SIDEBAR_ITEM_SELECTED = HIGHLIGHT_COLOR
SIDEBAR_TEXT = TEXT_COLOR
TEXT_PRIMARY = TEXT_COLOR
PRIMARY = HIGHLIGHT_COLOR

# Versuche am Ende der Datei, das Theme zu initialisieren
initialize_theme_from_config()