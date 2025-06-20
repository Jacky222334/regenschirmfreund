# ☂️ Regenschirm freund:innen - Psycho-Oncology Triage Dashboard

Ein interaktives Streamlit Dashboard für die Zuteilung und Verwaltung von psycho-onkologischen Konsilen.

## 🎯 Features

### 🏥 Triage-System
- **Faire Rotation**: Automatische Zuteilung basierend auf Verfügbarkeit
- **AM/PM Schichten**: Separate Verfügbarkeit für Vormittag/Nachmittag
- **Session-basierte Warteschlange**: Kontinuierliche Rotation ohne Verlust
- **Mitarbeiterfotos**: Visuelle Darstellung mit Cyber-Design

### 📚 Tagesquestions - Quiz
- **3 Schwierigkeitsgrade**: 
  - 🪱 Regenwurm (leicht) - Fragen 1-5
  - 🐦 Spatz (mittel) - Fragen 6-13
  - 🐧 Pinguin (schwer) - Fragen 14-20
- **Interaktive Beantwortung**: Sofortige Anzeige der Lösungen
- **Statistik-Tracking**: Erfolgsquote und Fortschritt
- **Wissenschaftlich fundiert**: Basiert auf Lehmann et al. (2009)

### 🔄 Interaktives Flowchart
- **Konsil-Workflow**: Schritt-für-Schritt Abarbeitung
- **Dynamische Entfaltung**: Buttons erscheinen basierend auf Entscheidungen
- **Mermaid-Diagramm**: Visuelle Darstellung des aktuellen Status
- **SOP-Integration**: Verknüpfung mit Standard Operating Procedures

### 📋 SOP-Management
- **Automatische Erkennung**: Findet alle SOP*.png Dateien
- **Visuelle Darstellung**: Embedded Images mit Cyber-Design
- **Download-Funktion**: Direkter Download der SOP-Dokumente

### 🌈 Design & UX
- **Cyberpunk-Theme**: Schwarzer Hintergrund mit neon-gelben Akzenten
- **Wettersimulation**: 5 verschiedene Wettermuster (Regen, Blitz, Sonne, Wolken)
- **Swiss German Interface**: Vollständig lokalisierte Benutzeroberfläche
- **Mobile-optimiert**: Responsive Design für alle Geräte

## 🚀 Installation & Setup

### Lokale Installation
```bash
# Repository klonen
git clone https://github.com/YOUR_USERNAME/regenschirmfreunde-dashboard.git
cd regenschirmfreunde-dashboard

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt

# App starten
streamlit run triage_dashboard.py
```

### CSV-Datenstruktur
Erstelle eine Datei `data/employees.csv` mit folgender Struktur:
```csv
kuerzel,name,anstellungs_prozent,stationaer_anteil,verfuegbar
MA01,BA,80,50,True
MA02,AN,100,30,True
MA03,JU,60,70,True
```

### Mitarbeiterfotos (Optional)
- Speichere Fotos als `data/[NAME].png` (z.B. `data/BA.png`)
- Empfohlene Größe: 200x200px
- Format: PNG mit transparentem Hintergrund

### SOP-Dokumente (Optional)
- Speichere SOPs als `data/SOP01.png`, `data/SOP02.png`, etc.
- Format: PNG-Bilder der Dokumente

## 🏗️ Deployment auf Streamlit Community Cloud

1. **Repository auf GitHub**: Stelle sicher, dass dein Code auf GitHub ist
2. **Streamlit Cloud**: Gehe zu [share.streamlit.io](https://share.streamlit.io)
3. **App deployen**: 
   - "New app" klicken
   - GitHub Repository auswählen
   - Branch: `main`
   - Main file path: `triage_dashboard.py`
   - App URL anpassen
4. **Deploy**: Klicke "Deploy!" und warte auf den Build

## 📊 Verwendung

### Triage-Dashboard
1. **Anwesenheit markieren**: Expandiere "Anwesenheit hüt" und markiere verfügbare Mitarbeiter
2. **Zuteilung**: Klicke "GO" um einen Fall zuzuteilen oder "NO" um zu überspringen
3. **Verlauf**: Sieh dir alle Zuweisungen im "Zuteiligsverlauf" an

### Quiz
1. **Schwierigkeitsgrad wählen**: Expandiere Regenwurm, Spatz oder Pinguin
2. **Fragen beantworten**: Klicke auf die gewünschte Antwort (a, b, c, d)
3. **Sofortiges Feedback**: Richtige/falsche Antworten werden sofort angezeigt
4. **Statistik verfolgen**: Sieh deine Erfolgsquote am Ende

### Interaktives Flowchart
1. **Workflow starten**: Klicke "Start: Konsilanfrag erhalte"
2. **Entscheidungen treffen**: Folge den Buttons durch den Konsil-Prozess
3. **Visuelles Feedback**: Das Mermaid-Diagramm zeigt den aktuellen Status
4. **Reset**: Klicke "Workflow zurücksetze" um von vorne zu beginnen

## 🎨 Anpassungen

### Farben ändern
Die Hauptfarben sind in CSS-Variablen definiert:
- `--primary-neon`: #CCFF00 (Neon-Gelb)
- `--secondary-neon`: #39FF14 (Neon-Grün)
- `--accent-yellow`: #FFFF00 (Reines Gelb)

### Wettereffekte
Die Wettersimulation kann in der `weather_js` Variable angepasst werden:
- Neue Wettermuster hinzufügen
- Timing der Effekte ändern
- CSS-Animationen modifizieren

### Quiz erweitern
Neue Fragen in `QUIZ_DATA` hinzufügen:
```python
{
    "id": 21,
    "question": "Deine neue Frage hier?",
    "options": ["a) Option 1", "b) Option 2", "c) Option 3", "d) Option 4"],
    "correct": "a",
    "answer": "a) Richtige Antwort mit Erklärung"
}
```

## 🛠️ Technische Details

### Verwendete Technologien
- **Frontend**: Streamlit 1.32.0
- **Datenverarbeitung**: Pandas 2.2.1
- **Bildverarbeitung**: Pillow 10.4.0
- **Diagramme**: Mermaid.js
- **Styling**: Custom CSS mit Cyber-Theme

### Session State Management
- `queue`: Rotations-Warteschlange der Mitarbeiter
- `log`: Historie aller Zuweisungen
- `quiz_answers`: Gespeicherte Quiz-Antworten
- `flowchart_steps`: Status des interaktiven Workflows

## 📝 Lizenz

Dieses Projekt ist für den internen Gebrauch in psycho-onkologischen Einrichtungen konzipiert.

## 🤝 Beitragen

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne eine Pull Request

## 📞 Support

Bei Fragen oder Problemen erstelle ein Issue im GitHub Repository.

---
*Entwickelt mit ❤️ für das Psycho-Onkologie Team* 