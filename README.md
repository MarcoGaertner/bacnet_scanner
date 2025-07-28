Verwendung
Verbindung zum BACnet-Netzwerk herstellen
    1. Wähle den Tab "Verbindung" in der Seitenleiste
    2. Gib die IP-Adresse deines BACnet-Netzwerks ein
    3. Konfiguriere optional den Port (Standard: 47808)
    4. Klicke auf "Verbinden"
Geräte scannen
    1. Nach erfolgreicher Verbindung wechsle zum Tab "Geräte"
    2. Klicke auf "Scan starten"
    3. Warte, bis der Scan abgeschlossen ist
    4. Die gefundenen Geräte werden in einer Liste angezeigt
Geräteinformationen anzeigen
    1. Wähle ein Gerät aus der Liste aus
    2. Die Eigenschaften und Datenpunkte des Geräts werden angezeigt
    3. Klicke auf einen Datenpunkt, um Details anzuzeigen oder Werte zu ändern
Online-Trend erstellen
    1. Wechsle zum Tab "Online-Trend"
    2. Wähle die zu überwachenden Datenpunkte aus
    3. Konfiguriere das Aktualisierungsintervall
    4. Starte die Überwachung mit "Trend starten"


Architektur
Die Anwendung ist modular aufgebaut und folgt dem Prinzip der Trennung von UI und Geschäftslogik:

    - UI-Modul: Implementiert mit Kivy für eine responsive und plattformübergreifende Benutzeroberfläche
    - Scanner-Modul: Enthält die BACnet-Kommunikationslogik und Geräteentdeckung
    - ore-Modul: Stellt gemeinsame Funktionen wie Event-Handling und Konfigurationsmanagement bereit
    - Data-Modul: Verwaltet die Persistenz und den Export von Daten


Projektstruktur
bacnet_scanner/
│
├── main.py                      # Haupteinstiegspunkt
├── requirements.txt             # Projektabhängigkeiten
│
├── ui/
│   ├── main.py                  # UI-Hauptmodul
│   ├── assets/                  # Bilder, Icons, Styles
│   ├── screens/                 # UI-Bildschirme
│   └── widgets/                 # Wiederverwendbare UI-Komponenten
│
├── scanner/
│   ├── main.py                  # Scanner-Hauptmodul
│   ├── discovery.py             # Geräteentdeckung
│   └── bacnet_client.py         # BACnet-Kommunikation
│
└── core/
    ├── models.py                # Datenmodelle
    ├── events.py                # Event-System
    └── config.py                # Konfigurationsmanagement


Entwicklung
Entwicklungsumgebung einrichten

    
# Repository klonen
git clone https://github.com/username/bacnet_scanner.git
cd bacnet_scanner

# Virtuelle Umgebung erstellen und aktivieren
python -m venv bacnet_env
# Windows:
bacnet_env\Scripts\activate
# Linux/Mac:
# source bacnet_env/bin/activate

# Entwicklungsabhängigkeiten installieren
pip install -r requirements-dev.txt


Tests ausführen
pytest


Code-Formatierung
black .

Roadmap
    - Integration mit BACnet/SC (Secure Connect)
    - Mobile Apps für iOS und Android
    - Erweitertes Alarmmanagement
    - Unterstützung für BACnet-Scheduling
    - Cloud-Synchronisation für Gerätekonfigurationen

Beitragen
Beiträge sind willkommen!

Lizenz
Dieses Projekt ist LIZENZFREI

Autoren
Marco Gärtner - Initiale Arbeit - GitHub

Danksagungen
    - BACpypes-Team für die hervorragende BACnet-Bibliothek
    - Kivy-Team für das großartige UI-Framework
    - Alle Mitwirkenden und Tester, die zur Verbesserung dieses Projekts beigetragen haben


Kontakt
Bei Fragen oder Anregungen erstelle bitte ein Issue im GitHub-Repository oder kontaktiere den Projektbetreuer unter marco-paul.gaertner@siemens.com