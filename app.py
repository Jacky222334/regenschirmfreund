import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
import os

# Logging Konfiguration
def setup_logging():
    """Konfiguriert das Logging-System."""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    log_file = f'logs/konsil_{datetime.now().strftime("%Y%m%d")}.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Konfiguration
st.set_page_config(
    page_title="Glücksrad - Konsil-Management",
    page_icon="🎡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Konstanten
WEATHER_STATES = {
    "Normal": "🌤️",
    "Gewitter": "⛈️",
    "Sonnenschein": "☀️",
    "Eisschlecken": "🍦"
}

WEATHER_FACTORS = {
    "Normal": 1.0,
    "Gewitter": 0.0,
    "Sonnenschein": 0.8,
    "Eisschlecken": 0.3
}

# Neo Black & Green Design with Ice Dots
st.markdown(
    """
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #000000 0%, #0a0a0a 50%, #000000 100%);
        color: #00ff88;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #00ff88 !important;
        text-shadow: 0 0 10px #00ff88, 0 0 20px #00ff88, 0 0 30px #00ff88;
        font-family: 'Courier New', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Main title */
    h1 {
        text-align: center;
        animation: pulse-glow 2s ease-in-out infinite alternate;
        margin-bottom: 30px;
        border: 2px solid #00ff88;
        padding: 20px;
        border-radius: 10px;
        background: rgba(0, 255, 136, 0.1);
    }
    
    @keyframes pulse-glow {
        from { text-shadow: 0 0 10px #00ff88, 0 0 20px #00ff88; }
        to { text-shadow: 0 0 20px #00ff88, 0 0 30px #00ff88, 0 0 40px #00ff88; }
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, #001a0f, #003d26) !important;
        color: #00ff88 !important;
        border: 2px solid #00ff88 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.3) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #003d26, #00ff88) !important;
        color: #000000 !important;
        box-shadow: 0 0 25px rgba(0, 255, 136, 0.8) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Primary button special styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(45deg, #00ff88, #00cc6a) !important;
        color: #000000 !important;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.6) !important;
    }
    
    /* Text and metrics */
    .metric-value {
        color: #00ff88 !important;
        font-weight: bold !important;
    }
    
    /* Containers and cards */
    .stContainer, .stColumns, .element-container {
        background: rgba(0, 255, 136, 0.05) !important;
        border-radius: 10px !important;
        padding: 15px !important;
        margin: 10px 0 !important;
        border: 1px solid rgba(0, 255, 136, 0.2) !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #000000, #0a0a0a) !important;
        border-right: 2px solid #00ff88 !important;
    }
    
    /* Success messages */
    .stSuccess {
        background: rgba(0, 255, 136, 0.2) !important;
        border: 1px solid #00ff88 !important;
        color: #00ff88 !important;
    }
    
    /* Warning messages */
    .stWarning {
        background: rgba(255, 193, 7, 0.2) !important;
        border: 1px solid #ffc107 !important;
        color: #ffc107 !important;
    }
    
    /* Info messages */
    .stInfo {
        background: rgba(0, 123, 255, 0.2) !important;
        border: 1px solid #007bff !important;
        color: #007bff !important;
    }
    
    /* Ice dots animation */
    .ice-dots {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
        overflow: hidden;
    }
    
    .ice-dot {
        position: absolute;
        color: #00ffff;
        font-size: 8px;
        animation: ice-fall linear infinite;
        opacity: 0.7;
    }
    
    @keyframes ice-fall {
        0% {
            transform: translateY(-100vh) rotate(0deg);
            opacity: 0;
        }
        10% {
            opacity: 0.7;
        }
        90% {
            opacity: 0.7;
        }
        100% {
            transform: translateY(100vh) rotate(360deg);
            opacity: 0;
        }
    }
    
    /* Matrix-style text effect */
    .matrix-text {
        color: #00ff88;
        font-family: 'Courier New', monospace;
        text-shadow: 0 0 5px #00ff88;
    }
    
    /* Glowing borders */
    .glow-border {
        border: 2px solid #00ff88 !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.5) !important;
        border-radius: 10px !important;
    }
    
    /* Tables */
    .stDataFrame, table {
        background: rgba(0, 0, 0, 0.8) !important;
        color: #00ff88 !important;
        border: 1px solid #00ff88 !important;
    }
    
    /* Input fields */
    .stSelectbox > div > div, .stTextInput > div > div > input {
        background: rgba(0, 0, 0, 0.8) !important;
        color: #00ff88 !important;
        border: 1px solid #00ff88 !important;
    }
    
    /* Scrollbars */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #000000;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #00ff88;
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #00cc6a;
    }
    </style>
    
    <div class="ice-dots" id="ice-dots"></div>
    
    <script>
    // Create ice dots effect
    function createIceDots() {
        const container = document.getElementById('ice-dots');
        if (!container) return;
        
        // Clear existing dots
        container.innerHTML = '';
        
        const iceSymbols = ['❄️', '❅', '🧊', '💎', '⭐'];
        
        for (let i = 0; i < 30; i++) {
            const dot = document.createElement('div');
            dot.className = 'ice-dot';
            dot.innerHTML = iceSymbols[Math.floor(Math.random() * iceSymbols.length)];
            dot.style.left = Math.random() * 100 + '%';
            dot.style.animationDuration = (Math.random() * 8 + 4) + 's';
            dot.style.animationDelay = Math.random() * 5 + 's';
            dot.style.fontSize = (Math.random() * 10 + 8) + 'px';
            container.appendChild(dot);
        }
    }
    
    // Initialize ice dots
    setTimeout(createIceDots, 500);
    
    // Recreate dots periodically
    setInterval(createIceDots, 30000);
    
    // Add hover effects to buttons
    document.addEventListener('DOMContentLoaded', function() {
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px) scale(1.05)';
            });
            button.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1)';
            });
        });
    });
    </script>
    """,
    unsafe_allow_html=True
)



# Hilfsfunktionen
def load_employee_data():
    """Lädt die Mitarbeiterdaten aus der Excel-Datei."""
    try:
        df = pd.read_excel("data/employees.xlsx")
        # Konvertiere String-Werte in die richtigen Typen
        df['anstellungs_prozent'] = pd.to_numeric(df['anstellungs_prozent'], errors='coerce')
        df['stationaer_anteil'] = pd.to_numeric(df['stationaer_anteil'], errors='coerce')
        df['verfuegbar'] = df['verfuegbar'].fillna(True)  # Standard: verfügbar
        df['regenschirm'] = df['regenschirm'].fillna(False)  # Standard: kein Regenschirm
        df['weather'] = df['weather'].fillna('Normal')  # Standard: Normal
        # Filtere nur aktive Mitarbeiter (mit anstellungs_prozent > 20)
        df = df[df['anstellungs_prozent'] > 20]
        logger.info("Mitarbeiterdaten erfolgreich geladen")
        return df
    except FileNotFoundError:
        logger.error("Mitarbeiterdaten nicht gefunden")
        st.error("Mitarbeiterdaten nicht gefunden. Bitte stellen Sie sicher, dass data/employees.xlsx existiert.")
        return pd.DataFrame()

def save_employee_data(df):
    """Speichert die Mitarbeiterdaten in der Excel-Datei."""
    try:
        df.to_excel("data/employees.xlsx", index=False)
        logger.info("Mitarbeiterdaten erfolgreich gespeichert")
        return True
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Daten: {str(e)}")
        st.error(f"Fehler beim Speichern der Daten: {str(e)}")
        return False

def calculate_score(row, umbrella_lovers_count, is_day_before_vacation):
    """Berechnet den Score für einen Mitarbeiter und berücksichtigt alle relevanten Faktoren."""
    try:
        # Grundlegende Faktoren
        weather_factor = WEATHER_FACTORS.get(row['weather'], 1.0)
        stationaer_anteil = float(row['stationaer_anteil']) / 100  # Anteil stationäre Arbeit
        anstellungs_prozent = float(row['anstellungs_prozent']) / 100  # Anstellungsprozent
        
        # Verfügbarkeit prüfen - wenn nicht verfügbar, Score = 0
        if not row.get('verfuegbar', True):
            return 0.0
        
        # Anwesenheit prüfen (falls Anwesenheitsdaten vorhanden)
        if hasattr(row, 'is_present') and not row.get('is_present', True):
            return 0.0
        
        # Bonus für Regenschirmfreunde bei Eisschlecken
        if row['weather'] == "Eisschlecken" and row.get('regenschirm', False):
            weather_factor = 1.0  # Volle Punktzahl für Regenschirmfreunde bei Eisschlecken
        
        # Reduziere den Score, wenn es viele Regenschirmfreunde gibt
        if umbrella_lovers_count > 1:
            weather_factor *= 0.9  # Reduziere den Wetterfaktor um 10%
        
        # Reduziere den Score, wenn es der Tag vor dem Urlaub ist
        if is_day_before_vacation:
            weather_factor *= 0.8  # Reduziere den Wetterfaktor um 20%
        
        # Score-Berechnung: 
        # - stationaer_anteil: Wie viel stationäre Arbeit der Mitarbeiter macht (0.0-1.0)
        # - anstellungs_prozent: Anstellungsprozent (0.2-1.0, da < 20% bereits gefiltert)
        # - weather_factor: Wetterabhängiger Faktor (0.0-1.0)
        score = stationaer_anteil * anstellungs_prozent * weather_factor
        
        logger.debug(f"Score für {row['name']}: {score:.2f} (Stationär: {stationaer_anteil:.0%}, Anstellung: {anstellungs_prozent:.0%}, Wetter: {weather_factor:.2f})")
        return round(score, 2)
    except Exception as e:
        logger.error(f"Fehler bei der Score-Berechnung für {row.get('name', 'Unbekannt')}: {str(e)}")
        return 0.0

def get_available_staff():
    """Gibt eine sortierte Liste aller verfügbaren Mitarbeiter zurück."""
    df = load_employee_data()
    if df.empty:
        return pd.DataFrame()
    
    # Prüfe Anwesenheit - nur anwesende Mitarbeiter sind verfügbar
    if 'morning_attendance' in st.session_state and 'afternoon_attendance' in st.session_state:
        # Ein Mitarbeiter ist verfügbar, wenn er morgens ODER nachmittags anwesend ist
        def is_present(name):
            morning_present = st.session_state.morning_attendance.get(name, False)
            afternoon_present = st.session_state.afternoon_attendance.get(name, False)
            return morning_present or afternoon_present
        
        # Filtere nur anwesende Mitarbeiter
        df['is_present'] = df['name'].apply(is_present)
        df = df[df['is_present'] == True]
        
        if df.empty:
            logger.warning("Keine anwesenden Mitarbeiter gefunden")
            return pd.DataFrame()
    else:
        # Wenn keine Anwesenheitsdaten vorliegen, nutze das 'verfuegbar' Feld
        df = df[df['verfuegbar'] == True]
    
    # Zähle die Regenschirmfreunde (nur bei anwesenden/verfügbaren Mitarbeitern)
    umbrella_lovers_count = df['regenschirm'].sum()
    
    # Berechne Scores für alle verfügbaren Mitarbeiter
    df['score'] = df.apply(lambda row: calculate_score(row, umbrella_lovers_count, is_day_before_vacation=False), axis=1)
    
    # Filtere verfügbare Mitarbeiter (Score > 0) und sortiere nach Score
    available_df = df[df['score'] > 0].sort_values('score', ascending=False)
    logger.info(f"Verfügbare Mitarbeiter: {len(available_df)}")
    return available_df

def get_next_consultation():
    """Bestimmt die nächste Person für ein Konsil ohne sie zuzuweisen."""
    # Initialisiere oder hole die Liste der zugewiesenen Personen
    if 'assigned_kuerzel' not in st.session_state:
        st.session_state.assigned_kuerzel = []
    
    # Hole alle verfügbaren Mitarbeiter
    available_df = get_available_staff()
    if available_df.empty:
        logger.warning("Keine verfügbaren Mitarbeiter gefunden")
        return None
    
    # Für die Anzeige der nächsten Person: verwende die Preview-Liste falls vorhanden
    # Für echte Zuweisung: verwende nur die assigned_kuerzel Liste
    excluded_list = st.session_state.assigned_kuerzel.copy()
    
    # Wenn alle Mitarbeiter bereits zugewiesen wurden, setze die Liste zurück
    if len(excluded_list) >= len(available_df):
        logger.info("Alle Mitarbeiter wurden zugewiesen, Liste wird zurückgesetzt")
        st.session_state.assigned_kuerzel = []
        excluded_list = []
    
    # Filtere die bereits zugewiesenen Personen aus
    available_df = available_df[~available_df['kuerzel'].isin(excluded_list)]
    
    if available_df.empty:
        logger.warning("Keine weiteren verfügbaren Mitarbeiter")
        return None
    
    # Nimm die Person mit dem höchsten Score (aber weise sie noch nicht zu)
    next_person = available_df.iloc[0]
    
    logger.info(f"Nächste Person bereit: {next_person['name']} ({next_person['kuerzel']}) mit Score {next_person['score']:.2f}")
    return next_person

def get_next_consultation_preview():
    """Bestimmt die nächste Person für die Vorschau mit der Preview-Liste."""
    # Initialisiere Listen
    if 'assigned_kuerzel' not in st.session_state:
        st.session_state.assigned_kuerzel = []
    if 'preview_assigned' not in st.session_state:
        st.session_state.preview_assigned = []
    
    # Hole alle verfügbaren Mitarbeiter
    available_df = get_available_staff()
    if available_df.empty:
        return None
    
    # Kombiniere echte Zuteilungen und Preview-Zuweisungen für die Anzeige
    excluded_list = st.session_state.assigned_kuerzel + st.session_state.preview_assigned
    
    # Wenn alle in der Preview angezeigt wurden, verwende nur die echten Zuteilungen
    if len(st.session_state.preview_assigned) >= len(available_df):
        excluded_list = st.session_state.assigned_kuerzel.copy()
    
    # Filtere die bereits angezeigten/zugewiesenen Personen aus
    available_df = available_df[~available_df['kuerzel'].isin(excluded_list)]
    
    if available_df.empty:
        return None
    
    # Nimm die Person mit dem höchsten Score für die Vorschau
    next_person = available_df.iloc[0]
    
    return next_person

def assign_next_person():
    """Weist die nächste Person zu."""
    next_person = get_next_consultation()
    if next_person is not None:
        # Füge sie zur Liste der zugewiesenen Personen hinzu
        st.session_state.assigned_kuerzel.append(next_person['kuerzel'])
        logger.info(f"Person zugewiesen: {next_person['name']} ({next_person['kuerzel']}) mit Score {next_person['score']:.2f}")
        return next_person
    return None

def show_priority_queue():
    """Zeigt die Prioritätswarteschlange an."""
    available_df = get_available_staff()
    if available_df.empty:
        return
    
    # Initialisiere die Liste der zugewiesenen Personen
    if 'assigned_kuerzel' not in st.session_state:
        st.session_state.assigned_kuerzel = []
    
    # Erstelle eine Kopie der verfügbaren Mitarbeiter
    queue_df = available_df.copy()
    
    # Markiere bereits zugewiesene Personen
    queue_df['status'] = queue_df['kuerzel'].apply(
        lambda x: '🔴 Bereits zugewiesen' if x in st.session_state.assigned_kuerzel else '🟢 Verfügbar'
    )
    
    # Füge eine Spalte für die Position in der Warteschlange hinzu
    queue_df['position'] = range(1, len(queue_df) + 1)
    
    # Formatiere die Anzeige
    display_df = queue_df[['position', 'kuerzel', 'name', 'weather', 'score', 'status']].copy()
    display_df['weather'] = display_df['weather'].map(lambda x: f"{WEATHER_STATES.get(x, '')} {x}")
    display_df['score'] = display_df['score'].map(lambda x: f"{x:.2f}")
    
    # Zeige die Warteschlange an
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'position': st.column_config.NumberColumn(
                'Position',
                help='Position in der Warteschlange',
                format='%d.'
            ),
            'kuerzel': 'Kürzel',
            'name': 'Name',
            'weather': 'Wetter',
            'score': 'Score',
            'status': 'Status'
        }
    )

def show_team_status(df):
    """Zeigt den aktuellen Team-Status an"""
    # Berechne Scores für die Anzeige
    umbrella_lovers_count = df['regenschirm'].sum()
    df['score'] = df.apply(lambda row: calculate_score(row, umbrella_lovers_count, is_day_before_vacation=False), axis=1)
    
    # Formatiere die Anzeige
    display_df = df[['kuerzel', 'name', 'weather', 'verfuegbar', 'regenschirm', 'score']].copy()
    display_df['weather'] = display_df['weather'].map(lambda x: f"{WEATHER_STATES.get(x, '')} {x}")
    display_df['verfuegbar'] = display_df['verfuegbar'].map({True: '✅', False: '❌'})
    display_df['regenschirm'] = display_df['regenschirm'].map({True: '☂️', False: '-'})
    display_df['score'] = display_df['score'].map(lambda x: f"{x:.2f}")
    
    # Zeige den Team-Status an
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def create_assignment_visualization(df):
    """Erstellt eine retro-gaming Visualisierung mit tanzenden Psychologinnen und Wettereffekten"""
    # Berechne die Anzahl der Zuteilungen pro Person für die aktuelle Woche
    current_week = datetime.now().isocalendar()[1]
    
    # Erstelle ein Dictionary mit den Zuteilungen aus dem Session State
    # Speichere die Zuteilungen pro Woche
    if 'weekly_assignments' not in st.session_state:
        st.session_state.weekly_assignments = {}
    
    # Initialisiere die aktuelle Woche, falls noch nicht vorhanden
    if current_week not in st.session_state.weekly_assignments:
        st.session_state.weekly_assignments[current_week] = {}
    
    # Aktualisiere die Zuteilungen für die aktuelle Woche
    for kuerzel in st.session_state.get('assigned_kuerzel', []):
        if kuerzel in st.session_state.weekly_assignments[current_week]:
            st.session_state.weekly_assignments[current_week][kuerzel] += 1
        else:
            st.session_state.weekly_assignments[current_week][kuerzel] = 1
    
    # Erstelle DataFrame mit den Zuteilungen der aktuellen Woche
    assignments = pd.DataFrame({
        'kuerzel': list(st.session_state.weekly_assignments[current_week].keys()),
        'zuteilungen': list(st.session_state.weekly_assignments[current_week].values())
    })
    
    # Füge Namen und Regenschirm-Status hinzu
    assignments = assignments.merge(df[['kuerzel', 'name', 'regenschirm', 'weather']].drop_duplicates(), on='kuerzel')
    
    # Füge auch Mitarbeiter ohne Zuteilungen hinzu
    all_employees = df[['kuerzel', 'name', 'regenschirm', 'weather']].drop_duplicates()
    assignments = pd.merge(all_employees, assignments, how='left', on=['kuerzel', 'name', 'regenschirm', 'weather'])
    assignments['zuteilungen'] = assignments['zuteilungen'].fillna(0)
    
    # Berechne den relativen Anteil (in Prozent)
    total_assignments = assignments['zuteilungen'].sum()
    if total_assignments > 0:
        assignments['anteil'] = (assignments['zuteilungen'] / total_assignments * 100).round(1)
    else:
        assignments['anteil'] = 0
    
    # Retro Gaming Farbpalette basierend auf Wetter
    retro_colors = {
        'Normal': '#4ECDC4',    # Türkis
        'Sonnenschein': '#FFEAA7',  # Gelb
        'Gewitter': '#FF6B6B',   # Rot
        'Eisschlecken': '#DDA0DD'  # Lila
    }
    
    # Erstelle das Balkendiagramm mit Plotly Express
    fig = px.bar(
        assignments,
        x='name',
        y='anteil',
        color='weather',
        color_discrete_map=retro_colors,
        text='anteil',
        title=f'🎮 RETRO GLÜCKSRAD - KW {current_week} 🎮',
        labels={'name': 'Mitarbeiter', 'anteil': 'Anteil (%)', 'weather': 'Wetter-Status'}
    )
    
    # Retro Gaming Layout
    fig.update_layout(
        showlegend=True,
        legend_title='🌤️ Wetter-Status',
        height=600,
        plot_bgcolor='rgba(0,0,0,0.1)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Courier New, monospace",
            size=14,
            color="#333"
        ),
        title_font=dict(
            size=24,
            color="#FF6B6B"
        ),
        xaxis_tickangle=-45,
        yaxis_title='🎯 Anteil an Zuteilungen (%)',
        yaxis_range=[0, max(assignments['anteil']) * 1.3 if max(assignments['anteil']) > 0 else 30],
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.3)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.3)'
        )
    )
    
    # Text-Position anpassen mit Retro Style
    fig.update_traces(
        texttemplate='%{text:.1f}%', 
        textposition='outside',
        textfont=dict(size=16, color="white"),
        marker=dict(
            line=dict(color='#333', width=2)
        )
    )
    
    # Füge animierte Symbole basierend auf Wetter und Status hinzu
    for i, row in assignments.iterrows():
        y_pos = row['anteil'] + 5
        
        # Wetter-spezifische Symbole
        if row['weather'] == 'Eisschlecken':
            fig.add_annotation(
                x=row['name'],
                y=y_pos,
                text='🍦🧊',
                showarrow=False,
                font=dict(size=30)
            )
        elif row['weather'] == 'Gewitter':
            fig.add_annotation(
                x=row['name'],
                y=y_pos,
                text='⚡⛈️',
                showarrow=False,
                font=dict(size=30)
            )
        elif row['weather'] == 'Sonnenschein':
            fig.add_annotation(
                x=row['name'],
                y=y_pos,
                text='☀️🌻',
                showarrow=False,
                font=dict(size=30)
            )
        else:  # Normal
            fig.add_annotation(
                x=row['name'],
                y=y_pos,
                text='🌤️✨',
                showarrow=False,
                font=dict(size=30)
            )
        
        # Regenschirm-Status
        if row['regenschirm']:
            fig.add_annotation(
                x=row['name'],
                y=y_pos + 8,
                text='☂️',
                showarrow=False,
                font=dict(size=35)
            )
        
        # Tanzende Psychologin für hohe Scores
        if row['anteil'] > 20:
            fig.add_annotation(
                x=row['name'],
                y=y_pos + 15,
                text='💃🎭',
                showarrow=False,
                font=dict(size=25)
            )
    
    return fig

# Hauptanwendung
def main():
    # Neo Black & Green Design applied via CSS above
    
    st.title("🧊 NEO GLÜCKSRAD - KONSIL MATRIX 💎")
    
    # Lade Mitarbeiterdaten für Anwesenheits-Widgets
    employee_data = load_employee_data()
    if not employee_data.empty:
        # Anwesenheits-Widgets in der Sidebar
        st.sidebar.header('Anwesenheit')
        
        # Initialisiere Session State für Anwesenheit
        if 'morning_attendance' not in st.session_state:
            st.session_state.morning_attendance = {emp: False for emp in employee_data['name']}
        if 'afternoon_attendance' not in st.session_state:
            st.session_state.afternoon_attendance = {emp: False for emp in employee_data['name']}
        
        # Morgens Anwesenheit
        st.sidebar.subheader('Morgens')
        for emp in employee_data['name']:
            st.session_state.morning_attendance[emp] = st.sidebar.checkbox(
                emp, 
                value=st.session_state.morning_attendance[emp], 
                key=f'morning_{emp}'
            )
        
        # Nachmittags Anwesenheit
        st.sidebar.subheader('Nachmittags')
        for emp in employee_data['name']:
            st.session_state.afternoon_attendance[emp] = st.sidebar.checkbox(
                emp, 
                value=st.session_state.afternoon_attendance[emp], 
                key=f'afternoon_{emp}'
            )
    
    # Seitenauswahl
    page = st.sidebar.selectbox(
        "Navigation",
        ["Oberärzt*innen-Dashboard", "Mitarbeiter-Dashboard"]
    )
    
    # Anwesenheit wird nur im Algorithmus berücksichtigt, nicht separat angezeigt
    
    if page == "Oberärzt*innen-Dashboard":
        show_doctor_dashboard()
    else:
        show_staff_dashboard()

def show_doctor_dashboard():
    """Zeigt das Dashboard für Oberärzt*innen"""
    st.header("🌡️ Dienst-Konsilübersicht")
    
    # Lade die Daten
    df = load_employee_data()
    if df is None:
        return
    
    # Initialisiere Session State für zugewiesene Kürzel
    if 'assigned_kuerzel' not in st.session_state:
        st.session_state.assigned_kuerzel = []
    
    # Zeige aktuelle Zuteilung
    st.subheader("🎯 Nächste Zuteilung")
    
    # Zeige die nächste Person für echte Zuweisung (nur assigned_kuerzel)
    next_person = get_next_consultation()
    
    # Zeige alternative Vorschau falls der "Nächste Person anzeigen" Button verwendet wurde
    if 'preview_assigned' in st.session_state and len(st.session_state.preview_assigned) > 0:
        preview_person = get_next_consultation_preview()
        if preview_person is not None:
            st.info(f"👁️ **Vorschau**: Nächste Person wäre {preview_person['name']} ({preview_person['kuerzel']}) mit Score {preview_person['score']:.2f}")
    
    if next_person is not None:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.metric("Nächste Person", f"{next_person['name']} ({next_person['kuerzel']})")
        with col2:
            st.metric("Score", f"{next_person['score']:.2f}")
        with col3:
            # GO Button für echte Zuweisung
            if st.button("🚀 GO!", type="primary", help="Person zuweisen"):
                assign_next_person()
                st.success(f"✅ {next_person['name']} wurde zugewiesen!")
                # Zurücksetzen der Preview-Liste nach echter Zuweisung
                if 'preview_assigned' in st.session_state:
                    st.session_state.preview_assigned = []
                st.rerun()
    else:
        st.warning("Keine weiteren verfügbaren Personen")
        if st.button("🔄 Zuteilungen zurücksetzen", type="secondary"):
            st.session_state.assigned_kuerzel = []
            if 'preview_assigned' in st.session_state:
                st.session_state.preview_assigned = []
            st.rerun()
    
    # Zeige alle bereits zugewiesenen Personen und Nächste Person Button
    if len(st.session_state.assigned_kuerzel) > 0:
        st.subheader("📋 Bereits zugewiesene Personen")
        assigned_text = ", ".join([f"{kuerzel}" for kuerzel in st.session_state.assigned_kuerzel])
        st.info(f"✅ **Zugewiesen**: {assigned_text}")
    
    # Zeige Preview-Liste falls vorhanden
    if 'preview_assigned' in st.session_state and len(st.session_state.preview_assigned) > 0:
        st.subheader("👁️ Vorschau-Liste")
        preview_text = ", ".join([f"{kuerzel}" for kuerzel in st.session_state.preview_assigned])
        st.warning(f"👁️ **Nur Vorschau** (noch nicht zugewiesen): {preview_text}")
        if st.button("🗑️ Vorschau löschen", type="secondary", help="Vorschau-Liste zurücksetzen"):
            st.session_state.preview_assigned = []
            st.rerun()
    
    # Button zum Anzeigen der nächsten Person (nur Vorschau, keine echte Zuweisung)
    if st.button("🔄 Nächste Person anzeigen", type="secondary"):
        # Erstelle eine separate Preview-Liste für die Anzeige
        if 'preview_assigned' not in st.session_state:
            st.session_state.preview_assigned = []
        
        available_df = get_available_staff()
        if not available_df.empty:
            # Wenn alle in der Preview angezeigt wurden, setze Preview-Liste zurück
            if len(st.session_state.preview_assigned) >= len(available_df):
                st.session_state.preview_assigned = []
            else:
                # Füge die aktuelle Person nur zur Preview-Liste hinzu (nicht zur echten Zuweisung)
                if next_person is not None and next_person['kuerzel'] not in st.session_state.preview_assigned:
                    st.session_state.preview_assigned.append(next_person['kuerzel'])
        st.rerun()
    
    # Log-Anzeige Button
    if st.button("📜 Log anzeigen", type="secondary"):
        if 'show_log' not in st.session_state:
            st.session_state.show_log = False
        st.session_state.show_log = not st.session_state.show_log
        st.rerun()
    
    # Zeige Log wenn aktiviert
    if st.session_state.get('show_log', False):
        st.subheader("📜 System Log")
        try:
            log_files = [f for f in os.listdir('logs') if f.endswith('.log')]
            if log_files:
                latest_log = max(log_files)
                with open(f'logs/{latest_log}', 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    # Zeige nur die letzten 50 Zeilen
                    log_lines = log_content.split('\n')
                    recent_lines = log_lines[-50:] if len(log_lines) > 50 else log_lines
                    st.text_area("Log Inhalt", value='\n'.join(recent_lines), height=400)
            else:
                st.warning("Keine Log-Dateien gefunden")
        except Exception as e:
            st.error(f"Fehler beim Laden der Log-Datei: {str(e)}")
    
    # Zeige Visualisierung
    st.subheader("Verteilung der Zuteilungen")
    fig = create_assignment_visualization(df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Zeige Team-Status
    st.subheader("Team-Status")
    show_team_status(df)

def show_staff_dashboard():
    st.header("👤 Mein Status")
    
    # Mitarbeiterauswahl
    df = load_employee_data()
    selected_staff = st.selectbox(
        "Mitarbeiter auswählen",
        df['name'].tolist()
    )
    
    st.subheader("🌀 WETTER EINSTELLEN")
    weather = st.selectbox(
        "Aktueller Status",
        list(WEATHER_STATES.keys()),
        format_func=lambda x: f"{WEATHER_STATES[x]} {x}"
    )
    
    st.subheader("☂️ Regenschirmfreund")
    regenschirm = st.checkbox("Ja, kann evtl. einspringen")
    
    # Speichern der Änderungen
    if st.button("Status speichern"):
        old_weather = df.loc[df['name'] == selected_staff, 'weather'].iloc[0]
        old_regenschirm = df.loc[df['name'] == selected_staff, 'regenschirm'].iloc[0]
        
        df.loc[df['name'] == selected_staff, 'weather'] = weather
        df.loc[df['name'] == selected_staff, 'regenschirm'] = regenschirm
        
        if save_employee_data(df):
            logger.info(f"Status aktualisiert für {selected_staff}: Wetter von {old_weather} zu {weather}, Regenschirm von {old_regenschirm} zu {regenschirm}")
            st.success("Status erfolgreich gespeichert!")
    
    st.subheader("Teamübersicht")
    if not df.empty:
        display_df = df[['kuerzel', 'weather', 'verfuegbar', 'regenschirm']].copy()
        display_df['weather'] = display_df['weather'].map(lambda x: f"{WEATHER_STATES.get(x, '')} {x}")
        display_df['verfuegbar'] = display_df['verfuegbar'].map({True: '✅', False: '❌'})
        display_df['regenschirm'] = display_df['regenschirm'].map({True: '☂️', False: '-'})
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    
    st.subheader("Prioritätswarteschlange")
    show_priority_queue()
    
    # Log-Anzeige Button auch im Staff Dashboard
    if st.button("📜 Log anzeigen", key="staff_log_button", type="secondary"):
        if 'show_staff_log' not in st.session_state:
            st.session_state.show_staff_log = False
        st.session_state.show_staff_log = not st.session_state.show_staff_log
        st.rerun()
    
    # Zeige Log wenn aktiviert
    if st.session_state.get('show_staff_log', False):
        st.subheader("📜 System Log")
        try:
            log_files = [f for f in os.listdir('logs') if f.endswith('.log')]
            if log_files:
                latest_log = max(log_files)
                with open(f'logs/{latest_log}', 'r', encoding='utf-8') as f:
                    log_content = f.read()
                    # Zeige nur die letzten 50 Zeilen
                    log_lines = log_content.split('\n')
                    recent_lines = log_lines[-50:] if len(log_lines) > 50 else log_lines
                    st.text_area("Log Inhalt", value='\n'.join(recent_lines), height=400, key="staff_log_area")
            else:
                st.warning("Keine Log-Dateien gefunden")
        except Exception as e:
            st.error(f"Fehler beim Laden der Log-Datei: {str(e)}")



# Adjust the display settings for mobile
st.markdown(
    "<style>\n"
    "@media (max-width: 600px) {\n"
    "    .stDataFrame {\n"
    "        overflow-x: auto;\n"
    "    }\n"
    "    .stMarkdown {\n"
    "        font-size: 14px;\n"
    "    }\n"
    "}\n"
    "</style>",
    unsafe_allow_html=True
)

if __name__ == "__main__":
    main() 