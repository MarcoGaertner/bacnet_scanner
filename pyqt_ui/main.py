import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow
from styles.pyqt_colors import ThemeManager, ThemeColors

# Pfad zum übergeordneten Ordner hinzufügen
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

from screens.settings_screen import SettingsScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BACnet Scanner – Einstellungen")
        self.setGeometry(100, 100, 600, 400)
        self.settings_screen = SettingsScreen()
        self.setCentralWidget(self.settings_screen)

        # Theme direkt zu Beginn anwenden
        self.apply_theme(ThemeColors.current)

    def apply_theme(self, theme):
        # Diesen Style auch auf das MainWindow anwenden!
        style = f"""
        QMainWindow {{
            background-color: {theme['BACKGROUND']};
        }}
        QWidget {{
            background-color: {theme['BACKGROUND']};
            color: {theme['TEXT_COLOR']};
        }}
        QGroupBox {{
            background-color: {theme['CARD_BACKGROUND']};
            border: 1px solid {theme['HIGHLIGHT_COLOR']};
            border-radius: 8px;
            margin-top: 10px;
            padding: 10px;
        }}
        QLabel {{
            color: {theme['TEXT_COLOR']};
            font-size: 14px;
        }}
        QComboBox {{
            background-color: {theme['TAB_BACKGROUND']};
            color: {theme['TEXT_COLOR']};
            padding: 5px;
            border-radius: 5px;
            border: 1px solid {theme['HIGHLIGHT_COLOR']};
        }}
        QComboBox::drop-down {{
            border-left: 1px solid {theme['HIGHLIGHT_COLOR']};
        }}
        QComboBox QAbstractItemView {{
            background-color: {theme['CARD_BACKGROUND']};
            color: {theme['TEXT_COLOR']};
            selection-background-color: {theme['HIGHLIGHT_COLOR']};
        }}
        """
        self.setStyleSheet(style)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
