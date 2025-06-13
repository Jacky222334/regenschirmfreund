# Glücksrad - Psychoonkologisches Konsil-Management

Ein kreatives und empathisches System zur fairen Zuteilung von stationären Konsilen im psychoonkologischen Team.

## Features

- 🎯 Faire Zuteilung basierend auf verschiedenen Faktoren
- 🌤️ Wetter-System zur Selbsteinschätzung
- 👥 Separate Dashboards für Oberärzt*innen und Mitarbeitende
- ⚖️ Berücksichtigung von Anstellungsprozent und stationärem Anteil
- 🤝 Regenschirm-System für flexible Übernahmen

## Installation

1. Repository klonen
2. Virtuelle Umgebung erstellen und aktivieren:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unter Windows: venv\Scripts\activate
   ```
3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

## Verwendung

1. Anwendung starten:
   ```bash
   streamlit run app.py
   ```
2. Im Browser öffnen: http://localhost:8501

## Datenstruktur

Die Mitarbeiterdaten werden in `data/employees.csv` gespeichert mit folgenden Feldern:
- Kürzel
- Name
- Anstellungsprozentsatz
- Stationärer Anteil
- Dienstplan
- Anwesenheitsstatus

## Lizenz

Intern - Nur für den Gebrauch im psychoonkologischen Team 