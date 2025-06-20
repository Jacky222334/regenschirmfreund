"""
Streamlit app for psycho-oncology triage dashboard (Triagist view).
Author: Jan Schulze & AI assistant
Dependencies: streamlit, pandas
Place employees.csv in the data directory with columns: 
    kuerzel,name,anstellungs_prozent,stationaer_anteil,verfuegbar

The app shows:
  • current date/time
  • suggested next MA (by two-letter alias)
  • GO + Next buttons
  • live priority list
  • toggle to view assignment log
Manual attendance table allows marking AM/PM presence.
"""

import datetime
import pandas as pd
import streamlit as st
import json
import base64
from pathlib import Path

# ---------- CONFIGURATION ----------
PRIMARY = "#000000"
ACCENT = "#CCFF00"
SECONDARY = "#39FF14"
TERTIARY = "#FFFF00"

# ---------- SCHWEIZER DEUTSCH ----------
TEXTS = {
    "title": "Regenschirmfreunde",
    "attendance_today": "Anwesenheit hüt",
    "ma": "MA",
    "morning": "Vormittag",
    "afternoon": "Namittag", 
    "next_recommendation": "Nächschti Empfehlig",
    "go": "Zueteile",
    "go_help": "Fall dere Person zueteile",
    "next": "Nächschti",
    "next_help": "Zur nächschte Person i dr Reihefolg",
    "priority_list": "Prioritätelischte",
    "assignment_log": "Zueteiligsprotokolle",
    "employee_overview": "Mitarbeiterübersicht",
    "no_assignments": "No kei Zueteilige hüt",
    "time": "Zyt",
    "period": "Zytruum",
    "weather_sunny": "Sunne",
    "weather_rainy": "Räge",
    "weather_stormy": "Gwitter",
    "weather_cloudy": "Bewölkt",
    "weather_mixed": "Wächselhaft"
}

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="☂️ Regenschirmfreunde",
    page_icon="☂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- CYBERPUNK STYLING ----------
st.markdown(
    f"""
    <style>
         @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@100;200;300;400;500;600;700;800;900&display=swap');
         
         /* GLOBAL RESET */
         * {{
             margin: 0;
             padding: 0;
             box-sizing: border-box;
         }}
         
         /* BACKGROUND & MAIN STYLING */
         .stApp {{
             background: {PRIMARY};
             color: {ACCENT};
             font-family: 'Orbitron', monospace;
             font-weight: 200;
         }}
         
         /* FIXED HEADER WITH USZ */
         .fixed-header {{
             position: fixed;
             top: 0;
             left: 0;
             right: 0;
             height: 160px;
             background: linear-gradient(135deg, #000000f8, #111111f8);
             border-bottom: 4px solid {ACCENT};
             z-index: 1000;
             display: flex;
             align-items: flex-end;
             justify-content: center;
             backdrop-filter: blur(20px);
             box-shadow: 
                 0 0 40px {ACCENT}60,
                 0 0 80px {ACCENT}40,
                 0 4px 20px #000000aa;
         }}
         
         .usz-logo {{
             font-family: 'Orbitron', monospace;
             font-size: 4rem;
             font-weight: 300;
             color: {ACCENT};
             text-shadow: 
                 0 0 15px {ACCENT},
                 0 0 30px {ACCENT},
                 0 0 45px {ACCENT},
                 0 0 60px {ACCENT},
                 0 0 75px {ACCENT};
             animation: uszFlicker 3s ease-in-out infinite;
             letter-spacing: 0.2rem;
             margin-bottom: 20px;
             text-align: center;
             line-height: 0.8;
         }}
         
         @keyframes uszFlicker {{
             0%, 100% {{ 
                 opacity: 1;
                 text-shadow: 
                     0 0 15px {ACCENT},
                     0 0 30px {ACCENT},
                     0 0 45px {ACCENT},
                     0 0 60px {ACCENT},
                     0 0 75px {ACCENT};
                 transform: scale(1);
             }}
             25% {{ 
                 opacity: 0.7;
                 text-shadow: 
                     0 0 8px {ACCENT},
                     0 0 20px {ACCENT},
                     0 0 35px {ACCENT},
                     0 0 50px {ACCENT},
                     0 0 65px {ACCENT};
                 transform: scale(0.98);
             }}
             50% {{ 
                 opacity: 0.9;
                 text-shadow: 
                     0 0 12px {ACCENT},
                     0 0 25px {ACCENT},
                     0 0 40px {ACCENT},
                     0 0 55px {ACCENT},
                     0 0 70px {ACCENT};
                 transform: scale(1.02);
             }}
             75% {{ 
                 opacity: 0.6;
                 text-shadow: 
                     0 0 18px {ACCENT},
                     0 0 35px {ACCENT},
                     0 0 50px {ACCENT},
                     0 0 65px {ACCENT},
                     0 0 80px {ACCENT};
                 transform: scale(0.99);
             }}
         }}
         
         /* MAIN CONTENT MARGIN FOR FIXED HEADER */
         .main .block-container {{
             padding-top: 180px !important;
         }}
         
         /* MOBILE OPTIMIZATION */
         @media screen and (max-width: 768px) {{
             .fixed-header {{
                 height: 130px;
             }}
             
             .usz-logo {{
                 font-size: 2.2rem;
                 letter-spacing: 0.1rem;
                 margin-bottom: 15px;
                 line-height: 0.9;
             }}
             
             .main .block-container {{
                 padding-top: 150px !important;
             }}
             
             /* Mobile attendance styling */
             .attendance-mobile {{
                 display: flex;
                 flex-direction: column;
                 gap: 15px;
                 padding: 20px;
                 background: linear-gradient(135deg, #00000060, #111111aa);
                 border: 2px solid {ACCENT};
                 border-radius: 15px;
                 margin: 20px 0;
             }}
             
             .attendance-row {{
                 display: flex;
                 align-items: center;
                 justify-content: space-between;
                 padding: 15px;
                 background: linear-gradient(45deg, #00000080, #222222aa);
                 border: 1px solid {SECONDARY};
                 border-radius: 10px;
                 box-shadow: 0 0 15px {ACCENT}30;
             }}
             
             .ma-name-mobile {{
                 font-family: 'Orbitron', monospace;
                 font-weight: 300;
                 font-size: 1.2rem;
                 color: {ACCENT};
                 text-shadow: 0 0 8px {ACCENT};
                 flex: 1;
             }}
             
             .time-slots-mobile {{
                 display: flex;
                 gap: 20px;
                 align-items: center;
             }}
             
             .time-slot-mobile {{
                 display: flex;
                 flex-direction: column;
                 align-items: center;
                 gap: 5px;
             }}
             
             .time-label-mobile {{
                 font-family: 'Orbitron', monospace;
                 font-weight: 200;
                 font-size: 0.9rem;
                 color: {SECONDARY};
                 text-shadow: 0 0 5px {SECONDARY};
             }}
         }}
         
         /* WEATHER EFFECTS */
         .weather-container {{
             position: fixed;
             top: 0;
             left: 0;
             width: 100%;
             height: 100%;
             pointer-events: none;
             z-index: 1;
             overflow: hidden;
         }}
         
         .rain {{
             display: none;
         }}
         
         .rain::before {{
             content: '';
             position: absolute;
             top: 0;
             left: 0;
             width: 100%;
             height: 100%;
             background: linear-gradient(transparent, {ACCENT}20);
             animation: rainFall 1s linear infinite;
         }}
         
         @keyframes rainFall {{
             0% {{ transform: translateY(-100vh); }}
             100% {{ transform: translateY(100vh); }}
         }}
         
         .lightning {{
             display: none;
             position: absolute;
             width: 100%;
             height: 100%;
             opacity: 0;
             animation: lightning 8s infinite;
         }}
         
         .lightning::before {{
             content: '';
             position: absolute;
             top: 10%;
             left: 30%;
             width: 3px;
             height: 40%;
             background: linear-gradient(to bottom, 
                 {TERTIARY} 0%, 
                 #ffffff 50%, 
                 {ACCENT} 100%);
             box-shadow: 0 0 20px {TERTIARY}, 0 0 40px {ACCENT};
             animation: lightningBolt 0.1s ease-in-out;
         }}
         
         .lightning::after {{
             content: '';
             position: absolute;
             top: 20%;
             right: 25%;
             width: 2px;
             height: 35%;
             background: linear-gradient(to bottom, 
                 {ACCENT} 0%, 
                 #ffffff 30%, 
                 {SECONDARY} 100%);
             box-shadow: 0 0 15px {ACCENT}, 0 0 30px {SECONDARY};
             animation: lightningBolt 0.15s ease-in-out 0.05s;
         }}
         
         @keyframes lightning {{
             0%, 95% {{ opacity: 0; }}
             96%, 97% {{ opacity: 1; }}
             98%, 100% {{ opacity: 0; }}
         }}
         
         @keyframes lightningBolt {{
             0% {{ opacity: 0; transform: scaleY(0); }}
             50% {{ opacity: 1; transform: scaleY(1); }}
             100% {{ opacity: 0; transform: scaleY(0); }}
         }}
         
         .sunrays {{
             display: none;
             position: absolute;
             top: 50%;
             left: 50%;
             width: 200px;
             height: 200px;
             background: radial-gradient(circle, {TERTIARY}20, transparent);
             transform: translate(-50%, -50%);
             animation: rotate 20s linear infinite;
         }}
         
         @keyframes rotate {{
             0% {{ transform: translate(-50%, -50%) rotate(0deg); }}
             100% {{ transform: translate(-50%, -50%) rotate(360deg); }}
         }}
         
         .clouds {{
             display: none;
         }}
         
         .clouds::before {{
             content: '';
             position: absolute;
             top: 20%;
             left: -10%;
             width: 120%;
             height: 30%;
             background: linear-gradient(to right, transparent, {SECONDARY}10, transparent);
             animation: cloudMove 30s linear infinite;
         }}
         
         @keyframes cloudMove {{
             0% {{ transform: translateX(-100%); }}
             100% {{ transform: translateX(100%); }}
         }}
         
         .weather-particles {{
             position: absolute;
             width: 100%;
             height: 100%;
         }}
         
         .raindrop {{
             position: absolute;
             background: linear-gradient(to bottom, transparent, {ACCENT}80);
             animation: rainDrop 2s linear infinite;
         }}
         
         @keyframes rainDrop {{
             0% {{ 
                 transform: translateY(-100vh) rotate(10deg);
                 opacity: 1;
             }}
             100% {{ 
                 transform: translateY(100vh) rotate(360deg);
                 opacity: 0;
             }}
         }}
         
         /* STREAMLIT ELEMENT STYLING */
         .stSelectbox > div > div {{
             background: linear-gradient(45deg, #000000aa, #222222aa);
             border: 2px solid {ACCENT};
             border-radius: 10px;
             color: {ACCENT};
         }}
         
         .stButton > button {{
             background: {PRIMARY};
             color: {ACCENT};
             border: 3px solid {ACCENT};
             border-radius: 8px;
             font-family: 'Orbitron', monospace;
             font-weight: 400;
             font-size: 1.2rem;
             padding: 1.2rem 2.5rem;
             box-shadow: 0 0 25px {ACCENT}60;
             transition: all 0.3s ease;
             min-width: 120px;
             min-height: 60px;
         }}
         
         .stButton > button:hover {{
             background: {PRIMARY};
             color: {SECONDARY};
             box-shadow: 0 0 35px {ACCENT}80;
             transform: scale(1.08);
             border: 3px solid {SECONDARY};
         }}
         
         .stExpander {{
             background: linear-gradient(135deg, #000000aa, #111111aa);
             border: 2px solid {ACCENT};
             border-radius: 15px;
             margin: 1rem 0;
         }}
         
         .stCheckbox {{
             color: {ACCENT};
         }}
         
         .stSuccess {{
             background: linear-gradient(135deg, #00220055, #002200aa);
             border: 2px solid {SECONDARY};
             border-radius: 10px;
             color: {SECONDARY};
             font-family: 'Orbitron', monospace;
         }}
         
         .stInfo {{
             background: linear-gradient(135deg, #00002255, #000044aa);
             border: 2px solid {ACCENT};
             border-radius: 10px;
             color: {ACCENT};
             font-family: 'Orbitron', monospace;
         }}
         
         h1, h2, h3 {{
             color: {ACCENT};
             font-family: 'Orbitron', monospace;
             font-weight: 200;
             text-shadow: 0 0 10px {ACCENT};
         }}
         
         .accent {{ color: {ACCENT}; }}
         .secondary {{ color: {SECONDARY}; }}
         .tertiary {{ color: {TERTIARY}; }}
         
         .priority-item {{
             color: {ACCENT};
             font-weight: 200;
             text-shadow: 0 0 5px {ACCENT};
             margin: 0.3rem 0;
         }}
         
         /* EMPLOYEE PHOTO STYLES - SIMPLE VERSION */
         .employee-photo {{
             width: 200px;
             height: 200px;
             border-radius: 50%;
             object-fit: cover;
             border: 3px solid {ACCENT};
             margin: 1rem auto;
             display: block;
         }}
         
         .photo-container {{
             position: relative;
             text-align: center;
             margin: 2rem 0;
         }}
         
         .photo-container .ma-fallback {{
             font-size: 4rem;
             color: {ACCENT};
             font-weight: 100;
             text-shadow: 0 0 15px {ACCENT}, 0 0 30px {ACCENT};
         }}
         
         /* MINI EMPLOYEE PHOTOS FOR PRIORITY LIST - SIMPLE VERSION */
         .mini-employee-photo {{
             width: 30px;
             height: 30px;
             border-radius: 50%;
             object-fit: cover;
             border: 2px solid {ACCENT};
             display: inline-block;
             vertical-align: middle;
             margin-right: 10px;
         }}
         
         .priority-item-with-photo {{
             display: flex;
             align-items: center;
             color: {ACCENT};
             font-weight: 200;
             text-shadow: 0 0 5px {ACCENT};
             margin: 0.5rem 0;
         }}
    </style>
    """,
    unsafe_allow_html=True,
)

# Add fixed header and weather container
st.markdown('''
<div class="fixed-header">
    <div class="usz-logo">☂️ Regenschirm<br/>freund:innen</div>
</div>
<div class="weather-container">
    <div class="clouds"></div>
    <div class="rain"></div>
    <div class="lightning"></div>
    <div class="sunrays"></div>
    <div class="weather-particles"></div>
</div>
''', unsafe_allow_html=True)

# ---------- HELPER FUNCTIONS ----------
def get_employee_photo_path(ma_code):
    """Check if employee photo exists and return path or None"""
    data_dir = Path("data")
    for extension in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
        photo_path = data_dir / f"{ma_code}{extension}"
        if photo_path.exists():
            return photo_path
    return None

def display_employee_avatar(ma_code):
    """Display employee photo or fallback to MA code"""
    photo_path = get_employee_photo_path(ma_code)
    
    # Get employee name if available
    employee_name = ""
    try:
        employee_row = df_emp[df_emp["MA"] == ma_code]
        if not employee_row.empty and 'name' in df_emp.columns:
            employee_name = employee_row.iloc[0]['name']
    except:
        pass
    
    if photo_path:
        # Convert to base64 for embedding
        with open(photo_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
        
        name_display = f"<div style='text-align: center; margin-top: 1rem; color: {SECONDARY}; font-weight: 300; text-shadow: 0 0 10px {SECONDARY};'>{employee_name}</div>" if employee_name else ""
        
        return f'''
        <div class="photo-container">
            <img src="data:image/png;base64,{img_data}" 
                 class="employee-photo" 
                 alt="{ma_code}"
                 title="{ma_code}">
            {name_display}
        </div>
        '''
    else:
        return f'''
        <div class="photo-container">
            <div class="ma-fallback">{ma_code}</div>
        </div>
        '''

def get_mini_employee_avatar(ma_code):
    """Get mini employee photo for priority list"""
    photo_path = get_employee_photo_path(ma_code)
    if photo_path:
        with open(photo_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
        return f'<img src="data:image/png;base64,{img_data}" class="mini-employee-photo" alt="{ma_code}" title="{ma_code}">'
    else:
        return ""

# ---------- LOAD DATA ----------
EMP_FILE = Path("data/employees.csv")
if not EMP_FILE.exists():
    st.error("❌ data/employees.csv nöd gfunde – bitte Datei hinzuefüege.")
    st.warning("⚠️ Demo-Modus: App startet ohni Mitarbeiterdaten. Upload de CSV für volli Funktionalität.")
    # Create empty dataframe with required columns for demo mode
    df_emp = pd.DataFrame({
        "name": ["DEMO"],
        "kuerzel": ["DEMO"], 
        "anstellungs_prozent": [100],
        "stationaer_anteil": [50],
        "verfuegbar": [True]
    })
else:
    try:
        df_emp = pd.read_csv(EMP_FILE)
    except Exception as e:
        st.error(f"❌ Fehler bim Lade vo employees.csv: {e}")
        st.warning("⚠️ Demo-Modus aktiviert")
        df_emp = pd.DataFrame({
            "name": ["DEMO"],
            "kuerzel": ["DEMO"], 
            "anstellungs_prozent": [100],
            "stationaer_anteil": [50],
            "verfuegbar": [True]
        })
# Use 'name' column as the MA identifier (contains the actual abbreviations like CA, BA, etc.)
if 'name' in df_emp.columns:
    df_emp["MA"] = df_emp["name"]
elif 'kuerzel' in df_emp.columns:
    df_emp["MA"] = df_emp["kuerzel"]
else:
    st.error("CSV-Datei muess entweder 'name' oder 'kuerzel' Spalte ha")
    st.stop()

# ---------- SESSION STATE ----------
if "queue" not in st.session_state:
    # Initialize queue sorted alphabetically
    st.session_state.queue = df_emp["MA"].tolist()
if "log" not in st.session_state:
    st.session_state.log = []

# Add weather JavaScript (fixed version)
weather_js = f"""
<script>
const t = {json.dumps(TEXTS)};

const weatherPatterns = [
    {{ icon: '☀️', textKey: 'weather_sunny', duration: 8000, effects: ['sunrays'] }},
    {{ icon: '🌧️', textKey: 'weather_rainy', duration: 12000, effects: ['rain', 'clouds'] }},
    {{ icon: '⛈️', textKey: 'weather_stormy', duration: 6000, effects: ['rain', 'lightning', 'clouds'] }},
    {{ icon: '☁️', textKey: 'weather_cloudy', duration: 10000, effects: ['clouds'] }},
    {{ icon: '🌦️', textKey: 'weather_mixed', duration: 15000, effects: ['rain', 'sunrays', 'clouds'] }}
];

let currentWeatherIndex = 0;

function updateWeather() {{
    const weather = weatherPatterns[currentWeatherIndex];
    const container = document.querySelector('.weather-container');
    
    if (container) {{
        // Reset all effects
        container.querySelectorAll('.rain, .lightning, .sunrays, .clouds').forEach(el => {{
            el.style.display = 'none';
        }});
        
        // Activate current weather effects
        weather.effects.forEach(effect => {{
            const element = container.querySelector('.' + effect);
            if (element) {{
                element.style.display = 'block';
            }}
        }});
        
        // Create dynamic raindrops for rain effects
        if (weather.effects.includes('rain')) {{
            createRaindrops();
        }}
    }}
    
    currentWeatherIndex = (currentWeatherIndex + 1) % weatherPatterns.length;
    setTimeout(updateWeather, weather.duration);
}}

function createRaindrops() {{
    const particles = document.querySelector('.weather-particles');
    if (!particles) return;
    
    // Clear existing raindrops
    particles.innerHTML = '';
    
    for (let i = 0; i < 50; i++) {{
        const drop = document.createElement('div');
        drop.className = 'raindrop';
        drop.style.left = Math.random() * 100 + '%';
        drop.style.width = Math.random() * 3 + 1 + 'px';
        drop.style.height = Math.random() * 20 + 10 + 'px';
        drop.style.animationDuration = Math.random() * 2 + 1 + 's';
        drop.style.animationDelay = Math.random() * 2 + 's';
        particles.appendChild(drop);
    }}
}}

// Start weather simulation
setTimeout(updateWeather, 1000);
</script>
"""

st.markdown(weather_js, unsafe_allow_html=True)

# ---------- HEADER ----------
now = datetime.datetime.now()
st.caption(f"{now.strftime('%A, %d %B %Y – %H:%M')}")

# ---------- MOBILE-OPTIMIZED ATTENDANCE INPUT ----------
with st.expander(TEXTS["attendance_today"]):
    # Check if mobile view should be used
    st.markdown('<div class="attendance-container">', unsafe_allow_html=True)
    
    # Desktop view (original columns)
    cols = st.columns([1,1,1])
    cols[0].markdown(f"**{TEXTS['ma']}**")
    cols[1].markdown(f"**{TEXTS['morning']}**")
    cols[2].markdown(f"**{TEXTS['afternoon']}**")
    
    for i, row in df_emp.iterrows():
        c1, c2, c3 = st.columns([1,1,1])
        c1.write(row.MA)
        key_am = f"{row.MA}_AM"
        key_pm = f"{row.MA}_PM"
        # Use existing verfuegbar column as default if available
        default_avail = row.get('verfuegbar', True) if 'verfuegbar' in df_emp.columns else True
        avail_am = c2.checkbox(f"{row.MA} {TEXTS['morning']}", key=key_am, value=default_avail, label_visibility="collapsed")
        avail_pm = c3.checkbox(f"{row.MA} {TEXTS['afternoon']}", key=key_pm, value=default_avail, label_visibility="collapsed")
        # Convert boolean to string to avoid pandas dtype warning
        df_emp.loc[i, "AM"] = str(avail_am)
        df_emp.loc[i, "PM"] = str(avail_pm)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- PRIORITY CALC ----------
current_period = "AM" if now.hour < 12 else "PM"
available = df_emp[(df_emp[current_period] == "True")]
# Simple round-robin: keep session queue and pop next available
queue = [ma for ma in st.session_state.queue if ma in available.MA.values]
if not queue:
    queue = available.MA.tolist()
    st.session_state.queue = queue  # reset

next_ma = queue[0] if queue else "—"

# ---------- DASHBOARD ----------
st.markdown(f"<h2 class='tertiary'>{TEXTS['next_recommendation']}</h2>", unsafe_allow_html=True)

# Display employee photo or MA code with special effects
if next_ma != "—":
    employee_avatar = display_employee_avatar(next_ma)
    st.markdown(employee_avatar, unsafe_allow_html=True)
    st.markdown(f"<h3 class='accent' style='text-align: center; margin: 1rem 0;'>Nächschti Person: <strong>{next_ma}</strong></h3>", unsafe_allow_html=True)
else:
    st.markdown(f"<h1 class='accent' style='font-size: 4rem; text-align: center; margin: 1rem 0;'>Kei verfüegbari Persone</h1>", unsafe_allow_html=True)

col_go, col_next = st.columns(2)

go = col_go.button("GO", key="go", help="Fall zueteile")
next_btn = col_next.button("NO", key="next", help="Nächschti Person")

if go and next_ma != "—":
    # Log assignment
    st.session_state.log.append({
        "Zeit": now.strftime("%Y-%m-%d %H:%M"),
        "MA": next_ma,
        "Period": current_period,
    })
    # Move assigned person to end of queue
    assigned_person = queue.pop(0)
    queue.append(assigned_person)
    st.session_state.queue = queue
    st.success(f"Fall zueteilt a: **{next_ma}**")
    st.rerun()
elif next_btn:
    # Skip to next person
    if queue:
        queue.append(queue.pop(0))
        st.session_state.queue = queue
        st.info(f"Übersprunge: **{next_ma}**")
    st.rerun()

# ---------- PRIORITY LIST ----------
st.markdown("---")
st.markdown(f"<h3 class='secondary'>{TEXTS['priority_list']}</h3>", unsafe_allow_html=True)
for idx, ma in enumerate(queue[:8], start=1):
    mini_photo = get_mini_employee_avatar(ma)
    if mini_photo:
        st.markdown(f"""
        <div class='priority-item-with-photo'>
            {mini_photo}
            <span>{idx}. <strong>{ma}</strong></span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='priority-item'>{idx}. <strong>{ma}</strong></div>", unsafe_allow_html=True)

# ---------- LOG VIEW ----------
with st.expander(TEXTS["assignment_log"]):
    if st.session_state.log:
        # Create translated column headers for the log
        log_df = pd.DataFrame(st.session_state.log)
        if not log_df.empty:
            log_df = log_df.rename(columns={
                "Zeit": TEXTS["time"],
                "MA": TEXTS["ma"],
                "Period": TEXTS["period"]
            })
        st.table(log_df)
    else:
        st.info(TEXTS["no_assignments"])

# ---------- EMPLOYEE INFO ----------
with st.expander(TEXTS["employee_overview"]):
    st.dataframe(df_emp[['MA', 'name', 'anstellungs_prozent', 'stationaer_anteil', 'verfuegbar']] if 'name' in df_emp.columns else df_emp) 

# ---------- TAGESQUIZ ----------
st.markdown("---")
st.markdown(f"<h2 class='secondary' style='text-align: center; margin: 2rem 0;'>📚 Tagesquestions</h2>", unsafe_allow_html=True)

# Quiz data
QUIZ_DATA = {
    "regenwurm": {
        "title": "Regenwurm (liecht)",
        "emoji": "🪱",
        "questions": [
            {
                "id": 1,
                "question": "Welches Akronym beschreibt ein verbreitetes 6-Stufen-Vorgehen zum Überbringen schlechter Nachrichten in der Onkologie?",
                "options": ["a) SCORE", "b) SPIKES", "c) POPPI", "d) CARES"],
                "correct": "b",
                "answer": "b) SPIKES"
            },
            {
                "id": 2,
                "question": "Wofür steht die Abkürzung HADS, die in vielen onkologischen Studien eingesetzt wird?",
                "options": ["a) Hospital Anxiety and Depression Scale", "b) Health Assessment of Distress Symptoms", "c) Holistic Adaptation & Development Survey", "d) Human Anxiety Diagnostic Score"],
                "correct": "a",
                "answer": "a) Hospital Anxiety and Depression Scale"
            },
            {
                "id": 3,
                "question": "In den meisten Untersuchungen berichten Patient*innen als häufigste Informationslücke:",
                "options": ["a) Ernährungsempfehlungen", "b) Familiäres Coping", "c) Nebenwirkungen der Therapie", "d) Anfahrtsweg zur Klinik"],
                "correct": "c",
                "answer": "c) Nebenwirkungen der Therapie"
            },
            {
                "id": 4,
                "question": "Zu welchem Zweck wurde die EORTC QLQ-C30 entwickelt?",
                "options": ["a) Erfassung von Arztzufriedenheit", "b) Erfassung der gesundheitsbezogenen Lebensqualität bei Krebs", "c) Bestimmung der Tumorgröße", "d) Screening kognitiver Defizite"],
                "correct": "b",
                "answer": "b) Erfassung der gesundheitsbezogenen Lebensqualität bei Krebs"
            },
            {
                "id": 5,
                "question": "Welcher Kommunikationsstil wird im Review am stärksten mit höherer Patientenzufriedenheit assoziiert?",
                "options": ["a) Arztzentriert", "b) Belehrend", "c) Patientenzentriert", "d) Technikorientiert"],
                "correct": "c",
                "answer": "c) Patientenzentriert"
            }
        ]
    },
    "spatz": {
        "title": "Spatz (mittel)",
        "emoji": "🐦",
        "questions": [
            {
                "id": 6,
                "question": "Welche drei übergeordneten Bedarfs-Domänen identifizierte die Supportive-Care-Needs-Survey (SCNS) als am häufigsten unerfüllt?",
                "options": ["a) Finanzen · Ernährung · Sport", "b) Psychologie · Information/Gesundheitssystem · Körper/Alltag", "c) Spiritualität · Sexualität · Pflege", "d) Freizeit · Familie · Schlaf"],
                "correct": "b",
                "answer": "b) Psychologie · Information/Gesundheitssystem · Körper/Alltag"
            },
            {
                "id": 7,
                "question": "Welche Patient*innengruppe zeigt laut Review tendenziell das geringste Bedürfnis nach detaillierter Prognose-Information?",
                "options": ["a) Jüngere Frauen", "b) Männer < 50 J", "c) Ältere Patient*innen (> 70 J)", "d) Metastasiertes Stadium"],
                "correct": "c",
                "answer": "c) Ältere Patient*innen (> 70 J)"
            },
            {
                "id": 8,
                "question": "Welche Aussage trifft nicht auf die Meta-Analyse von Gysels et al. (2004/05) zu Kommunikationstrainings zu?",
                "options": ["a) Viele Studien wiesen methodische Schwächen auf.", "b) Es bestehen inkonsistente Effekte auf psychische Endpunkte.", "c) Trainings reduzierten eindeutig die Burn-out-Rate der Ärzt*innen.", "d) Eine einheitliche Definition von \"Kommunikationsfertigkeit\" fehlte häufig."],
                "correct": "c",
                "answer": "c) Trainings reduzierten eindeutig die Burn-out-Rate der Ärzt*innen."
            },
            {
                "id": 9,
                "question": "Welches Messinstrument erfasst Selbstwirksamkeit in der Krankheitsbewältigung speziell bei onkologischen Patient*innen?",
                "options": ["a) CBI", "b) BDI-II", "c) RIAS", "d) LOT-R"],
                "correct": "a",
                "answer": "a) CBI"
            },
            {
                "id": 10,
                "question": "In Fallowfield et al. (2002) zeigte sich nach einem Kommunikationsworkshop primär eine Zunahme von …",
                "options": ["a) offenen Fragen und empathischen Äußerungen", "b) Gesprächsdauer um 40 %", "c) Nutzung von PowerPoint-Grafiken", "d) Verordnung palliativ-medizinischer Medikamente"],
                "correct": "a",
                "answer": "a) offenen Fragen und empathischen Äußerungen"
            },
            {
                "id": 11,
                "question": "Welche Variable moderiert laut dem im Review vorgestellten Modell den Zusammenhang zwischen Kommunikation und Inanspruchnahme psychosozialer Dienste besonders stark?",
                "options": ["a) Tumorart", "b) Subjektive Zufriedenheit mit der Interaktion", "c) Wohnort (Stadt/Land)", "d) Anzahl der Chemotherapiezyklen"],
                "correct": "b",
                "answer": "b) Subjektive Zufriedenheit mit der Interaktion"
            },
            {
                "id": 12,
                "question": "Welches Trainingsformat wies in Randomized-Controlled-Trials (RCT) die nachhaltigste Verbesserung ärztlicher Fertigkeiten (12-Monats-Follow-up) auf?",
                "options": ["a) Einmaliger 90-Min-Vortrag", "b) Mehrtägiges Basistraining + Konsolidierungsworkshop", "c) E-Learning-Modul ohne Präsenz", "d) Peer-Supervision via Telefon"],
                "correct": "b",
                "answer": "b) Mehrtägiges Basistraining + Konsolidierungsworkshop"
            },
            {
                "id": 13,
                "question": "Welcher Fragebogen misst vorrangig Informations- und Entscheidungspräferenzen bei Krebs?",
                "options": ["a) MPP", "b) GHQ-12", "c) POMS", "d) MBSS"],
                "correct": "a",
                "answer": "a) MPP"
            }
        ]
    },
    "pinguin": {
        "title": "Pinguin (schwer)",
        "emoji": "🐧",
        "questions": [
            {
                "id": 14,
                "question": "Welcher k-Wert (Cohen) wurde in Söllner et al. (2001) für die Übereinstimmung zwischen ärztlicher Distress-Einschätzung und Patient*innenselbstauskunft berichtet?",
                "options": ["a) 0,65", "b) 0,42", "c) 0,25", "d) 0,05"],
                "correct": "d",
                "answer": "d) 0,05"
            },
            {
                "id": 15,
                "question": "In McLachlan et al. (2001) profitierten Patient*innen mit welchem Depressions-Cut-off (BDI-SF) am stärksten von der Interventionsgruppe?",
                "options": ["a) ≥ 4", "b) ≥ 8", "c) ≥ 12", "d) ≥ 16"],
                "correct": "c",
                "answer": "c) ≥ 12"
            },
            {
                "id": 16,
                "question": "Welche der folgenden fünf Faktoren des Measure of Patients' Preferences (MPP) zeigten in der japanischen Validierung (Fujimori et al., 2007) die höchste Faktorladung?",
                "options": ["a) Setting", "b) Emotionale Unterstützung", "c) Medizinische Information", "d) Ermutigung zur Fragenstellung"],
                "correct": "c",
                "answer": "c) Medizinische Information"
            },
            {
                "id": 17,
                "question": "Die Studie von Hagerty et al. (2004) ergab, dass > 70 % palliativ behandelter Patient*innen quantitative Überlebensdaten wünschten; welche Erhebungsform wurde verwendet?",
                "options": ["a) Videovignetten", "b) Fiktives Fallbeispiel im Fragebogen", "c) Standardisiertes Klinisches Interview", "d) Experience-Sampling-Methode"],
                "correct": "b",
                "answer": "b) Fiktives Fallbeispiel im Fragebogen"
            },
            {
                "id": 18,
                "question": "Beim RIAS-Kodiersystem repräsentiert die Kategorie \"Back-channel responses\" hauptsächlich …",
                "options": ["a) erklärende Metaphern der Ärztinnen", "b) nonverbale Zustimmungssignale der Patientinnen", "c) organisatorische Gesprächsabschlüsse", "d) Therapieentscheidungen"],
                "correct": "b",
                "answer": "b) nonverbale Zustimmungssignale der Patientinnen"
            },
            {
                "id": 19,
                "question": "Welcher Anteil der Ärzt*innen berichtete laut Baile et al. (2002) monatlich durchschnittlich ≥ 13 Erstdiagnosen mit schlechter Prognose überbringen zu müssen?",
                "options": ["a) < 10 %", "b) 25 %", "c) ≈ 50 %", "d) > 75 %"],
                "correct": "c",
                "answer": "c) ≈ 50 %"
            },
            {
                "id": 20,
                "question": "Die kombinierte Interventionsbedingung \"mündliche Information + Broschüre + Video\" (de Lorenzo et al., 2004) führte zu einer signifikanten Verbesserung welcher POMS-Subskala?",
                "options": ["a) Verwirrtheit", "b) Vitalität", "c) Feindseligkeit", "d) Depression"],
                "correct": "b",
                "answer": "b) Vitalität"
            }
        ]
    }
}

# Initialize quiz session state
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}

# Quiz sections
for level_key, level_data in QUIZ_DATA.items():
    with st.expander(f"{level_data['emoji']} {level_data['title']}"):
        for q in level_data['questions']:
            st.markdown(f"**Frag {q['id']}:** {q['question']}")
            
            # Create buttons for each option
            cols = st.columns(len(q['options']))
            for i, option in enumerate(q['options']):
                if cols[i].button(option, key=f"q{q['id']}_{i}", help=f"Frag {q['id']} Option {option[0]}"):
                    # Store answer and show result immediately
                    st.session_state.quiz_answers[q['id']] = option[0]
                    
                    # Show result
                    if option[0] == q['correct']:
                        st.success(f"✅ Richtig! {q['answer']}")
                    else:
                        st.error(f"❌ Falsch! Richtig wär: {q['answer']}")
                    
                    st.rerun()
            
            # Show current answer if exists
            if q['id'] in st.session_state.quiz_answers:
                user_answer = st.session_state.quiz_answers[q['id']]
                if user_answer == q['correct']:
                    st.success(f"✅ Du hesch richtig gantwortet: {q['answer']}")
                else:
                    st.error(f"❌ Du hesch falsch gantwortet. Richtig wär: {q['answer']}")
            
            st.markdown("---")

# Quiz statistics
total_questions = sum(len(level_data['questions']) for level_data in QUIZ_DATA.values())
answered_questions = len(st.session_state.quiz_answers)
correct_answers = sum(1 for q_id, user_answer in st.session_state.quiz_answers.items() 
                     for level_data in QUIZ_DATA.values() 
                     for q in level_data['questions'] 
                     if q['id'] == q_id and user_answer == q['correct'])

if answered_questions > 0:
    st.markdown("---")
    st.markdown(f"<h3 class='accent'>📊 Dini Statistik</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Gantwortet", f"{answered_questions}/{total_questions}")
    col2.metric("Richtig", f"{correct_answers}/{answered_questions}")
    if answered_questions > 0:
        percentage = round((correct_answers / answered_questions) * 100, 1)
        col3.metric("Erfolgsquote", f"{percentage}%")

st.markdown(f"""
<div style='text-align: center; margin-top: 2rem; font-size: 0.8rem; color: #666;'>
    Alli Frage basiere uf Befund und Instrument, wo im Literatur-Review vo Lehmann et al. (2009, Psychother Psych Med 59:e3-e27) zämmegfasst sind.
</div>
""", unsafe_allow_html=True) 

# ---------- SOPS (STANDARD OPERATING PROCEDURES) ----------
st.markdown("---")
st.markdown(f"<h2 class='secondary' style='text-align: center; margin: 2rem 0;'>📋 SOPs - Standard Operating Procedures</h2>", unsafe_allow_html=True)

# Function to get SOP image as base64
def get_sop_image_base64(sop_file):
    """Convert SOP image to base64 for embedding"""
    try:
        with open(f"data/{sop_file}", "rb") as img_file:
            import base64
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return None

# Function to find all SOP files
def get_all_sop_files():
    """Find all SOP files in data directory"""
    import os
    import glob
    sop_files = []
    if os.path.exists("data"):
        sop_pattern = os.path.join("data", "SOP*.png")
        found_files = glob.glob(sop_pattern)
        for file_path in found_files:
            filename = os.path.basename(file_path)
            # Extract SOP number from filename (e.g., SOP01.png -> 01)
            sop_number = filename.replace("SOP", "").replace(".png", "")
            sop_files.append({
                "filename": filename,
                "number": sop_number,
                "title": f"SOP {sop_number}"
            })
    # Sort by SOP number
    sop_files.sort(key=lambda x: x['number'])
    return sop_files

# Get all available SOPs
available_sops = get_all_sop_files()

# ---------- INTERACTIVE FLOWCHART ----------
st.markdown("---")
st.markdown(f"<h3 class='accent' style='text-align: center; margin: 1.5rem 0;'>🔄 Interaktivs Flowchart - Konsil-Workflow</h3>", unsafe_allow_html=True)

# Initialize flowchart session state
if "flowchart_steps" not in st.session_state:
    st.session_state.flowchart_steps = {
        "start": False,
        "konsil_angenommen": None,  # None, True, False
        "vor_ort_abgeschlossen": None,
        "eintrag_erstellt": False,
        "patient_erreichbar": None,
        "datum_eingetragen": False,
        "sekretariat_benachrichtigt": False,
        "patient_angerufen": False,
        "team_benachrichtigt": False
    }

# CSS for flowchart cards and arrows
flowchart_css = """
<style>
.flowchart-card {
    background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
    border: 2px solid #CCFF00;
    border-radius: 12px;
    padding: 1rem;
    margin: 0.5rem;
    text-align: center;
    box-shadow: 0 0 20px rgba(204, 255, 0, 0.3);
    transition: all 0.3s ease;
}
.flowchart-card:hover {
    box-shadow: 0 0 30px rgba(204, 255, 0, 0.5);
    transform: translateY(-2px);
}
.flowchart-card.completed {
    border-color: #39FF14;
    background: linear-gradient(135deg, #1a3a1a, #2a4a2a);
}
.flowchart-card.inactive {
    border-color: #666;
    background: linear-gradient(135deg, #1a1a1a, #1a1a1a);
    opacity: 0.5;
}
.flowchart-arrow {
    text-align: center;
    font-size: 2rem;
    color: #CCFF00;
    margin: 0.5rem 0;
    text-shadow: 0 0 10px rgba(204, 255, 0, 0.5);
}
.flowchart-decision {
    background: linear-gradient(135deg, #3a1a1a, #4a2a2a);
    border: 2px solid #FFFF00;
}
.flowchart-decision.completed {
    border-color: #39FF14;
    background: linear-gradient(135deg, #1a3a1a, #2a4a2a);
}
.choice-buttons {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 10px;
}
.choice-btn {
    background: #000;
    border: 2px solid #CCFF00;
    color: #CCFF00;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s;
}
.choice-btn:hover {
    background: #CCFF00;
    color: #000;
}
.choice-btn.selected {
    background: #39FF14;
    border-color: #39FF14;
    color: #000;
}
</style>
"""

st.markdown(flowchart_css, unsafe_allow_html=True)

# Reset button at the top
if any(v for v in st.session_state.flowchart_steps.values() if v):
    col_reset, col_spacer = st.columns([1, 4])
    with col_reset:
        if st.button("🔄 Reset", key="reset_workflow", help="Workflow neu starte"):
            st.session_state.flowchart_steps = {key: False if isinstance(val, bool) else None for key, val in st.session_state.flowchart_steps.items()}
            st.rerun()

# Step 1: Start
card_class = "completed" if st.session_state.flowchart_steps["start"] else ""
st.markdown(f"""
<div class="flowchart-card {card_class}">
    <h4>🚀 Start</h4>
    <p>Konsilanfrag erhalte</p>
</div>
""", unsafe_allow_html=True)

if not st.session_state.flowchart_steps["start"]:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("✅ Start", key="step_start", help="Workflow starte"):
            st.session_state.flowchart_steps["start"] = True
            st.rerun()
else:
    st.markdown('<div class="flowchart-arrow">⬇️</div>', unsafe_allow_html=True)
    
    # Step 2: Konsil Decision
    decision_class = "completed" if st.session_state.flowchart_steps["konsil_angenommen"] is not None else ""
    st.markdown(f"""
    <div class="flowchart-card flowchart-decision {decision_class}">
        <h4>❓ Entscheidig</h4>
        <p>Konsil agnoh oder abglehnt?</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.flowchart_steps["konsil_angenommen"] is None:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                if st.button("✅ Agnoh", key="konsil_ja", help="Konsil agnoh"):
                    st.session_state.flowchart_steps["konsil_angenommen"] = True
                    st.rerun()
            with subcol2:
                if st.button("❌ Abglehnt", key="konsil_nein", help="Konsil abglehnt"):
                    st.session_state.flowchart_steps["konsil_angenommen"] = False
                    st.rerun()
    
    # Show result of konsil decision
    if st.session_state.flowchart_steps["konsil_angenommen"] == False:
        st.markdown('<div class="flowchart-arrow">⬇️</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="flowchart-card completed">
            <h4>🛑 Ende</h4>
            <p>Kei witeri Schritt - Konsil abglehnt</p>
        </div>
        """, unsafe_allow_html=True)
    
    elif st.session_state.flowchart_steps["konsil_angenommen"] == True:
        st.markdown('<div class="flowchart-arrow">⬇️</div>', unsafe_allow_html=True)
        
        # Step 3: Vor Ort Decision
        decision_class = "completed" if st.session_state.flowchart_steps["vor_ort_abgeschlossen"] is not None else ""
        st.markdown(f"""
        <div class="flowchart-card flowchart-decision {decision_class}">
            <h4>🏥 Vor Ort</h4>
            <p>Am selbe Tag vor Ort abgschlosse?</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.flowchart_steps["vor_ort_abgeschlossen"] is None:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                subcol1, subcol2 = st.columns(2)
                with subcol1:
                    if st.button("✅ Ja", key="vor_ort_ja", help="Vor Ort erledigt"):
                        st.session_state.flowchart_steps["vor_ort_abgeschlossen"] = True
                        st.rerun()
                with subcol2:
                    if st.button("❌ Nei", key="vor_ort_nein", help="Nöd vor Ort erledigt"):
                        st.session_state.flowchart_steps["vor_ort_abgeschlossen"] = False
                        st.rerun()
        
        # Branch A: Vor Ort abgeschlossen
        if st.session_state.flowchart_steps["vor_ort_abgeschlossen"] == True:
            st.markdown('<div class="flowchart-arrow">⬇️</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="flowchart-card completed">
                <h4>🎉 Workflow übersprunge</h4>
                <p>Konsil bereits erledigt - kei witeri Schritt nötig</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Branch B: Nicht vor Ort abgeschlossen
        elif st.session_state.flowchart_steps["vor_ort_abgeschlossen"] == False:
            st.markdown('<div class="flowchart-arrow">⬇️</div>', unsafe_allow_html=True)
            
            # Step 4: Eintrag erstellen
            card_class = "completed" if st.session_state.flowchart_steps["eintrag_erstellt"] else ""
            st.markdown(f"""
            <div class="flowchart-card {card_class}">
                <h4>📝 Konsil-Iitrag</h4>
                <p>Konsil-Iitrag im System erstelle</p>
            </div>
            """, unsafe_allow_html=True)
            
            if not st.session_state.flowchart_steps["eintrag_erstellt"]:
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("✅ Erstellt", key="eintrag_erstellt", help="Iitrag erstellt"):
                        st.session_state.flowchart_steps["eintrag_erstellt"] = True
                        st.rerun()
            else:
                st.markdown('<div class="flowchart-arrow">⬇️</div>', unsafe_allow_html=True)
                
                # Step 5: Patient erreichbar?
                decision_class = "completed" if st.session_state.flowchart_steps["patient_erreichbar"] is not None else ""
                st.markdown(f"""
                <div class="flowchart-card flowchart-decision {decision_class}">
                    <h4>📞 Patient</h4>
                    <p>Patient am gplante Tag erreichbar?</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.session_state.flowchart_steps["patient_erreichbar"] is None:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        subcol1, subcol2 = st.columns(2)
                        with subcol1:
                            if st.button("✅ Erreichbar", key="patient_ja", help="Patient erreichbar"):
                                st.session_state.flowchart_steps["patient_erreichbar"] = True
                                st.rerun()
                        with subcol2:
                            if st.button("❌ Nöd erreichbar", key="patient_nein", help="Patient nöd erreichbar"):
                                st.session_state.flowchart_steps["patient_erreichbar"] = False
                                st.rerun()
                
                # Patient erreichbar - Path A
                if st.session_state.flowchart_steps["patient_erreichbar"] == True:
                    st.markdown('<div class="flowchart-arrow">⬇️</div>', unsafe_allow_html=True)
                    
                    # Datum eintragen
                    card_class = "completed" if st.session_state.flowchart_steps["datum_eingetragen"] else ""
                    st.markdown(f"""
                    <div class="flowchart-card {card_class}">
                        <h4>📅 Datum</h4>
                        <p>Vorläufigs Besuchsdatum iitrage</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if not st.session_state.flowchart_steps["datum_eingetragen"]:
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col2:
                            if st.button("✅ Iitrage", key="datum_eingetragen", help="Datum iitrage"):
                                st.session_state.flowchart_steps["datum_eingetragen"] = True
                                st.rerun()
                    else:
                        st.markdown('<div class="flowchart-arrow">⬇️</div>', unsafe_allow_html=True)
                        
                        # Team benachrichtigen
                        card_class = "completed" if st.session_state.flowchart_steps["team_benachrichtigt"] else ""
                        st.markdown(f"""
                        <div class="flowchart-card {card_class}">
                            <h4>👥 Team</h4>
                            <p>Team benachrichtige - Konsil sichtbar mache</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if not st.session_state.flowchart_steps["team_benachrichtigt"]:
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col2:
                                if st.button("✅ Benachrichtigt", key="team_benachrichtigt", help="Team informiert"):
                                    st.session_state.flowchart_steps["team_benachrichtigt"] = True
                                    st.rerun()
                        else:
                            st.markdown('<div class="flowchart-arrow">⬇️</div>', unsafe_allow_html=True)
                            st.markdown("""
                            <div class="flowchart-card completed">
                                <h4>🏁 Workflow abgschlosse</h4>
                                <p>Team isch informiert - Konsil bereit</p>
                            </div>
                            """, unsafe_allow_html=True)
                
                # Patient nicht erreichbar - Path B
                elif st.session_state.flowchart_steps["patient_erreichbar"] == False:
                    st.markdown('<div class="flowchart-arrow">⬇️</div>', unsafe_allow_html=True)
                    
                    # Sekretariat benachrichtigen
                    card_class = "completed" if st.session_state.flowchart_steps["sekretariat_benachrichtigt"] else ""
                    st.markdown(f"""
                    <div class="flowchart-card {card_class}">
                        <h4>📞 Sekretariat</h4>
                        <p>Sekretariat benachrichtige - Status in KISIM aktualisiere</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if not st.session_state.flowchart_steps["sekretariat_benachrichtigt"]:
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col2:
                            if st.button("✅ Benachrichtigt", key="sek_benachrichtigt", help="Sekretariat informiert"):
                                st.session_state.flowchart_steps["sekretariat_benachrichtigt"] = True
                                st.rerun()
                    else:
                        st.markdown('<div class="flowchart-arrow">⬇️</div>', unsafe_allow_html=True)
                        
                        # Patient anrufen
                        card_class = "completed" if st.session_state.flowchart_steps["patient_angerufen"] else ""
                        st.markdown(f"""
                        <div class="flowchart-card {card_class}">
                            <h4>📱 Anruf</h4>
                            <p>Sekretariat rueft Patient a, fragt nach PO-Bedarf, dokumentiert in KISIM</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if not st.session_state.flowchart_steps["patient_angerufen"]:
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col2:
                                if st.button("✅ Agrueffe", key="patient_angerufen", help="Patient kontaktiert"):
                                    st.session_state.flowchart_steps["patient_angerufen"] = True
                                    st.rerun()
                        else:
                            st.markdown('<div class="flowchart-arrow">⬇️</div>', unsafe_allow_html=True)
                            st.markdown("""
                            <div class="flowchart-card completed">
                                <h4>🏁 Workflow abgschlosse</h4>
                                <p>Patient isch kontaktiert - Bedarf dokumentiert</p>
                            </div>
                            """, unsafe_allow_html=True)

# Progress indicator
if st.session_state.flowchart_steps["start"]:
    total_steps = 0
    completed_steps = 0
    
    # Count possible steps based on path taken
    if st.session_state.flowchart_steps["konsil_angenommen"] == True:
        if st.session_state.flowchart_steps["vor_ort_abgeschlossen"] == True:
            total_steps = 3  # Start + Konsil + Vor Ort
            completed_steps = sum([st.session_state.flowchart_steps["start"], 
                                 st.session_state.flowchart_steps["konsil_angenommen"] is not None,
                                 st.session_state.flowchart_steps["vor_ort_abgeschlossen"] is not None])
        elif st.session_state.flowchart_steps["vor_ort_abgeschlossen"] == False:
            if st.session_state.flowchart_steps["patient_erreichbar"] == True:
                total_steps = 6  # Full path A
                completed_steps = sum([st.session_state.flowchart_steps["start"], 
                                     st.session_state.flowchart_steps["konsil_angenommen"] is not None,
                                     st.session_state.flowchart_steps["vor_ort_abgeschlossen"] is not None,
                                     st.session_state.flowchart_steps["eintrag_erstellt"],
                                     st.session_state.flowchart_steps["patient_erreichbar"] is not None,
                                     st.session_state.flowchart_steps["datum_eingetragen"],
                                     st.session_state.flowchart_steps["team_benachrichtigt"]])
            elif st.session_state.flowchart_steps["patient_erreichbar"] == False:
                total_steps = 6  # Full path B
                completed_steps = sum([st.session_state.flowchart_steps["start"], 
                                     st.session_state.flowchart_steps["konsil_angenommen"] is not None,
                                     st.session_state.flowchart_steps["vor_ort_abgeschlossen"] is not None,
                                     st.session_state.flowchart_steps["eintrag_erstellt"],
                                     st.session_state.flowchart_steps["patient_erreichbar"] is not None,
                                     st.session_state.flowchart_steps["sekretariat_benachrichtigt"],
                                     st.session_state.flowchart_steps["patient_angerufen"]])
            else:
                total_steps = 4
                completed_steps = sum([st.session_state.flowchart_steps["start"], 
                                     st.session_state.flowchart_steps["konsil_angenommen"] is not None,
                                     st.session_state.flowchart_steps["vor_ort_abgeschlossen"] is not None,
                                     st.session_state.flowchart_steps["eintrag_erstellt"]])
        else:
            total_steps = 2
            completed_steps = sum([st.session_state.flowchart_steps["start"], 
                                 st.session_state.flowchart_steps["konsil_angenommen"] is not None])
    elif st.session_state.flowchart_steps["konsil_angenommen"] == False:
        total_steps = 2
        completed_steps = 2
    else:
        total_steps = 1
        completed_steps = 1
    
    if total_steps > 0:
        progress = completed_steps / total_steps
        st.progress(progress, text=f"Fortschritt: {completed_steps}/{total_steps} Schritt abgschlosse")

st.markdown("---")

# ---------- STATIC SOPs ----------
st.markdown("---")
st.markdown(f"<h3 class='accent' style='text-align: center; margin: 1.5rem 0;'>📋 Statischi SOP-Dokument</h3>", unsafe_allow_html=True)

if available_sops:
    st.markdown(f"<p style='text-align: center; color: #CCFF00;'>Verfüegbari SOPs: {len(available_sops)} Dokument</p>", unsafe_allow_html=True)
    
    # Display SOPs in expandable sections
    for sop in available_sops:
        with st.expander(f"📄 {sop['title']} - Standard Operating Procedure"):
            # Get image as base64
            sop_base64 = get_sop_image_base64(sop['filename'])
            
            if sop_base64:
                # Display the SOP image
                st.markdown(f"""
                <div style='text-align: center; margin: 1rem 0;'>
                    <img src="data:image/png;base64,{sop_base64}" 
                         style='max-width: 100%; height: auto; border: 2px solid #CCFF00; border-radius: 8px; box-shadow: 0 0 20px rgba(204, 255, 0, 0.3);' 
                         alt="{sop['title']}"/>
                </div>
                """, unsafe_allow_html=True)
                
                # Add download link
                st.markdown(f"""
                <div style='text-align: center; margin: 1rem 0;'>
                    <a href="data:image/png;base64,{sop_base64}" download="{sop['filename']}" 
                       style='background: linear-gradient(45deg, #000000, #1a1a1a); 
                              color: #CCFF00; 
                              border: 2px solid #CCFF00; 
                              padding: 0.5rem 1rem; 
                              text-decoration: none; 
                              border-radius: 5px;
                              box-shadow: 0 0 15px rgba(204, 255, 0, 0.3);
                              font-weight: bold;'>
                        💾 {sop['title']} Download
                    </a>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"SOP-Datei {sop['filename']} nöd gfunde")
else:
    st.info("🔍 Momentan sind kei SOPs verfüegbar. Dateie im 'data' Ordner als SOP01.png, SOP02.png, etc. speichere.") 