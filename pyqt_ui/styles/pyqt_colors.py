class ThemeColors:
    # Helles Theme (Standard)
    LIGHT = {
        "SIDEBAR_BACKGROUND": "#F3F3F0",
        "TAB_BACKGROUND": "#FFFFFF",
        "TEXT_COLOR": "#9999A9",
        "HIGHLIGHT_COLOR": "#009999",
        "BACKGROUND": "#FFFFFF",
        "CARD_BACKGROUND": "#FFFFFF"
    }
    
    # Dunkles Theme
    DARK = {
        "SIDEBAR_BACKGROUND": "#1E1E1E",
        "TAB_BACKGROUND": "#323232",
        "TEXT_COLOR": "#C8C8C8",
        "HIGHLIGHT_COLOR": "#00CCCC",
        "BACKGROUND": "#323232",
        "CARD_BACKGROUND": "#282828"
    }

    # Aktuelles Theme
    current = LIGHT.copy()

class ThemeManager:
    @staticmethod
    def set_theme(theme_name="hell"):
        if theme_name.lower() in ["dark", "dunkel"]:
            ThemeColors.current = ThemeColors.DARK
        else:
            ThemeColors.current = ThemeColors.LIGHT
