import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import streamlit_authenticator as stauth
import yaml
from pathlib import Path
import os

# Konfiguration
st.set_page_config(
    page_title="Glücksrad - Konsil-Management",
    page_icon="🎡",
    layout="wide"
)

# Authentifizierung
def init_auth():
    try:
        with open('.streamlit/secrets.toml') as file:
            config = yaml.safe_load(file)
        
        authenticator = stauth.Authenticate(
            config['credentials']['usernames'],
            'gluecksrad_cookie',
            'gluecksrad_key',
            cookie_expiry_days=30
        )
        return authenticator
    except Exception as e:
        st.error(f"Fehler bei der Authentifizierung: {str(e)}")
        return None

# Konstanten
WEATHER_STATES = {
    "Normal": "🟢",
    "Gewitter": "🔴",
    "Sonnenschein": "🟡",
    "Eisschlecken": "⚪️"
}

WEATHER_FACTORS = {
    "Normal": 1.0,
    "Gewitter": 0.0,
    "Sonnenschein": 0.8,
    "Eisschlecken": 0.3
}

# Hilfsfunktionen
def load_employee_data():
    """Lädt die Mitarbeiterdaten aus der CSV-Datei."""
    try:
        return pd.read_csv("data/employees.csv")
    except FileNotFoundError:
        st.error("Mitarbeiterdaten nicht gefunden. Bitte stellen Sie sicher, dass data/employees.csv existiert.")
        return pd.DataFrame()

def save_employee_data(df):
    """Speichert die Mitarbeiterdaten in der CSV-Datei."""
    try:
        df.to_csv("data/employees.csv", index=False)
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern der Daten: {str(e)}")
        return False

def calculate_score(row):
    """Berechnet den Score für einen Mitarbeiter."""
    weather_factor = WEATHER_FACTORS.get(row.get('weather', 'Normal'), 1.0)
    stationaer_anteil = float(row.get('stationaer_anteil', 0)) / 100
    anstellungs_prozent = float(row.get('anstellungs_prozent', 0)) / 100
    verfuegbar = 1.0 if row.get('verfuegbar', False) else 0.0
    
    return stationaer_anteil * anstellungs_prozent * verfuegbar * weather_factor

def get_next_consultation():
    """Bestimmt die nächste Person für ein Konsil."""
    df = load_employee_data()
    if df.empty:
        return None
    
    df['score'] = df.apply(calculate_score, axis=1)
    df = df[df['score'] > 0.5].sort_values('score', ascending=False)
    
    if df.empty:
        return None
    
    return df.iloc[0]

# Hauptanwendung
def main():
    st.title("🎡 Glücksrad - Konsil-Management")
    
    # Authentifizierung
    authenticator = init_auth()
    if authenticator:
        name, authentication_status, username = authenticator.login('Login', 'main')
        
        if authentication_status == False:
            st.error('Benutzername/Passwort ist falsch')
            return
        elif authentication_status == None:
            st.warning('Bitte geben Sie Benutzername und Passwort ein')
            return
        
        # Seitenauswahl
        page = st.sidebar.selectbox(
            "Navigation",
            ["Oberärzt*innen-Dashboard", "Mitarbeiter-Dashboard"]
        )
        
        if page == "Oberärzt*innen-Dashboard":
            show_doctor_dashboard()
        else:
            show_staff_dashboard()
        
        # Logout-Button
        authenticator.logout('Logout', 'sidebar')

def show_doctor_dashboard():
    st.header("🌡️ Dienst-Konsilübersicht")
    
    next_person = get_next_consultation()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if next_person is not None:
            st.metric(
                "Aktuelle Zuteilung",
                f"{next_person['kuerzel']} ({next_person['name']})"
            )
            st.metric(
                "Muss erledigt bis",
                (datetime.now() + timedelta(days=1)).strftime("%A %H:%M Uhr")
            )
        else:
            st.warning("Keine verfügbare Person gefunden")
    
    with col2:
        if st.button("Nächste Person anzeigen"):
            st.experimental_rerun()
    
    st.subheader("Teamstatus")
    df = load_employee_data()
    if not df.empty:
        st.dataframe(
            df[['kuerzel', 'name', 'weather', 'verfuegbar', 'regenschirm', 'score']],
            use_container_width=True
        )

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
        df.loc[df['name'] == selected_staff, 'weather'] = weather
        df.loc[df['name'] == selected_staff, 'regenschirm'] = regenschirm
        if save_employee_data(df):
            st.success("Status erfolgreich gespeichert!")
    
    st.subheader("Teamübersicht")
    if not df.empty:
        st.dataframe(
            df[['kuerzel', 'weather', 'verfuegbar', 'regenschirm']],
            use_container_width=True
        )

if __name__ == "__main__":
    main() 