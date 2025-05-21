import streamlit as st
import time
import numpy as np
from datetime import datetime

# Configuration
CO2_CRITICAL_THRESHOLD = 800  # ppm
CO2_WARNING_THRESHOLD = 600   # ppm
CHECK_INTERVAL = 5  # seconds between checks

# --- Simulate CO₂ level based on health parameters ---
def simulate_co2(respiration_rate, heart_rate, spo2, people_count, max_people):
    # Base CO2 level based on number of people
    base_co2 = 400 + (people_count * 100)
    
    # Adjust based on health parameters
    if respiration_rate > 25 or spo2 < 90 or heart_rate < 62 or heart_rate > 100:
        co2_level = base_co2 + 600  # Critical health condition
    elif respiration_rate > 18 or spo2 < 95 or heart_rate >= 100:
        co2_level = base_co2 + 300   # Warning health condition
    else:
        co2_level = base_co2         # Normal
    
    # Cap the maximum CO2 level
    co2_level = min(co2_level, 1200)
    
    # Determine status
    if co2_level > CO2_CRITICAL_THRESHOLD or people_count > max_people:
        return co2_level, "Critical"
    elif co2_level > CO2_WARNING_THRESHOLD or people_count == max_people:
        return co2_level, "Warning"
    else:
        return co2_level, "Normal"

# --- Get max people based on area ---
def get_max_people(area):
    if area <= 100:
        return 4
    elif area <= 150:
        return 6
    elif area <= 300:
        return 10
    elif area <= 500:
        return 15
    else:
        return 25

# --- JavaScript Audio Alert ---
def js_alert():
    js_code = """
    <script>
    function playAlert() {
        var audio = new Audio('https://assets.mixkit.co/sfx/preview/mixkit-alarm-digital-clock-beep-989.mp3');
        audio.loop = true;
        audio.play();
        return audio;
    }
    window.alertAudio = playAlert();
    </script>
    """
    st.components.v1.html(js_code, height=0)

def js_stop_alert():
    st.components.v1.html("""
    <script>
    if (window.alertAudio) {
        window.alertAudio.pause();
        window.alertAudio.currentTime = 0;
    }
    </script>
    """, height=0)

# --- Streamlit UI ---
st.title("🫁 Smart CO₂ Level Monitoring System")

# Initialize session state
if 'alarm_active' not in st.session_state:
    st.session_state.alarm_active = False

# --- Room Occupancy ---
st.subheader("🏠 Room & Occupancy Details")
col1, col2 = st.columns(2)
with col1:
    room_length = st.number_input("Room Length (ft)", min_value=10, max_value=50, value=10, step=5)
with col2:
    room_width = st.number_input("Room Width (ft)", min_value=10, max_value=50, value=10, step=5)

people_count = st.number_input("Number of People in the Room", min_value=1, step=1)
room_area = room_length * room_width
max_people = get_max_people(room_area)

st.info(f"""
🧮 *Room Area:* {room_area} sq ft  
👥 *Max Recommended Occupancy:* {max_people} people  
👤 *Current Occupancy:* {people_count} people
""")

# --- Check overcrowding ---
if people_count > max_people:
    st.error(f"🚨 Overcrowded! Room has {people_count} people (limit is {max_people}).")
elif people_count == max_people:
    st.warning(f"⚠ Room has {people_count} people (limit reached).")
else:
    st.success("✅ Occupancy is within safe limit.")

# --- Health Parameters ---
st.subheader("🧍 Health Monitoring")
respiration_rate = st.slider("Respiration Rate (breaths/min)", 10, 40, 16)
heart_rate = st.slider("Heart Rate (bpm)", 50, 160, 75)
spo2 = st.slider("Oxygen Saturation (%)", 80, 100, 98)

# --- Simulate CO₂ level ---
co2_level, status = simulate_co2(respiration_rate, heart_rate, spo2, people_count, max_people)

# --- Display results ---
st.subheader("🌬 Air Quality Status")
col1, col2 = st.columns(2)
with col1:
    st.metric("CO₂ Level", f"{co2_level} ppm", 
              delta="Critical" if co2_level > CO2_CRITICAL_THRESHOLD else 
                    "Warning" if co2_level > CO2_WARNING_THRESHOLD else "Normal")
with col2:
    status_placeholder = st.empty()

# --- Alarm control ---
if status == "Critical" or people_count > max_people:
    status_placeholder.error("🚨 CRITICAL: Immediate action required!")
    if not st.session_state.alarm_active:
        js_alert()
        st.session_state.alarm_active = True
elif status == "Warning" or people_count == max_people:
    status_placeholder.warning("⚠ WARNING: Monitor closely")
    if st.session_state.alarm_active:
        js_stop_alert()
        st.session_state.alarm_active = False
else:
    status_placeholder.success("✅ NORMAL: All parameters OK")
    if st.session_state.alarm_active:
        js_stop_alert()
        st.session_state.alarm_active = False

# Add manual alarm control
st.subheader("🔊 Alarm Controls")
if st.button("Test Alarm"):
    js_alert()
    st.session_state.alarm_active = True
    time.sleep(2)
    js_stop_alert()
    st.session_state.alarm_active = False

if st.button("Stop Alarm"):
    js_stop_alert()
    st.session_state.alarm_active = False

# Add automatic refresh
time.sleep(CHECK_INTERVAL)
st.experimental_rerun()
