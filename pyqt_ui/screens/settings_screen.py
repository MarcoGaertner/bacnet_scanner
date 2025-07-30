from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QGroupBox, QHBoxLayout
)
from core.config import ConfigManager
from core.i18n.translator import Translator
from core.events import event_dispatcher
from styles.pyqt_colors import ThemeManager, ThemeColors


class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.config_manager = ConfigManager()
        self.translator = Translator()

        # Layout initialisieren
        layout = QVBoxLayout()

        # Titel hinzufügen
        title_label = QLabel(self.translator.get("settings.title"))
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title_label)

        # UI-Section
        ui_group = QGroupBox(self.translator.get("settings.ui.section"))
        ui_layout = QVBoxLayout()

        # Dropdowns erstellen
        self.language_dropdown = self.create_dropdown(
            label=self.translator.get("settings.language"),
            items=[self.translator.get("language.german"), self.translator.get("language.english")],
            current=self.translator.get("language.german") if self.config_manager.get_setting("ui", "language") == "deutsch" else self.translator.get("language.english"),
            on_change=self.update_language
        )

        self.theme_dropdown = self.create_dropdown(
            label=self.translator.get("settings.theme"),
            items=[self.translator.get("theme.light"), self.translator.get("theme.dark")],
            current=self.translator.get("theme.light") if self.config_manager.get_setting("ui", "theme") == "hell" else self.translator.get("theme.dark"),
            on_change=self.update_theme
        )

        self.units_dropdown = self.create_dropdown(
            label=self.translator.get("settings.units"),
            items=[self.translator.get("units.metric"), self.translator.get("units.imperial")],
            current=self.translator.get("units.metric") if self.config_manager.get_setting("ui", "units") == "metrisch" else self.translator.get("units.imperial"),
            on_change=self.update_units
        )

        ui_layout.addLayout(self.language_dropdown)
        ui_layout.addLayout(self.theme_dropdown)
        ui_layout.addLayout(self.units_dropdown)

        ui_group.setLayout(ui_layout)
        layout.addWidget(ui_group)
        layout.addStretch()

        self.setLayout(layout)

        # Event Handling (Sprache und Theme-Updates)
        event_dispatcher.add_listener("on_language_changed", self.reload_translations)
        event_dispatcher.add_listener("on_theme_changed", self.reload_theme)
        
        self.apply_theme()


    def create_dropdown(self, label, items, current, on_change):
        layout = QHBoxLayout()
        lbl = QLabel(label)
        dropdown = QComboBox()
        dropdown.addItems(items)
        dropdown.setCurrentText(current)
        dropdown.currentTextChanged.connect(on_change)
        layout.addWidget(lbl)
        layout.addWidget(dropdown)
        return layout

    def update_language(self, selected):
        language_code = "deutsch" if selected == self.translator.get("language.german") else "englisch"
        self.config_manager.update_setting("ui", "language", language_code)

    def update_theme(self, selected):
        theme_code = "hell" if selected == self.translator.get("theme.light") else "dunkel"
        self.config_manager.update_setting("ui", "theme", theme_code)
        event_dispatcher.dispatch("on_theme_changed", theme_code)


    def update_units(self, selected):
        units_code = "metrisch" if selected == self.translator.get("units.metric") else "imperial"
        self.config_manager.update_setting("ui", "units", units_code)

    def reload_translations(self, language_code):
        # Neu laden aller Texte
        self.translator.set_language(language_code)
        self.refresh_ui_texts()

    def refresh_ui_texts(self):
        # UI-Texte aktualisieren (dynamisch neu setzen)
        pass

    def reload_theme(self, theme_name):
        ThemeManager.set_theme(theme_name)
        self.apply_theme()

    def apply_theme(self):
        theme = ThemeColors.current
        style = f"""
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
