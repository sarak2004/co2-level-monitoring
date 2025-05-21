import streamlit as st
from simulator import simulate_co2
import streamlit.components.v1 as components

st.title("🫁 CO₂ Level + Room Safety Simulation")

# --- Room Safety Section ---
st.subheader("🏠 Room & Occupancy Details")
col1, col2 = st.columns(2)
with col1:
    room_length = st.number_input("Room Length (ft)", min_value=10, max_value=50, value=10, step=5)
with col2:
    room_width = st.number_input("Room Width (ft)", min_value=10, max_value=50, value=10, step=5)

people_count = st.number_input("Number of People in the Room", min_value=1, step=1)
room_area = room_length * room_width

# Calculate max occupancy (1 person per 25 sq ft)
max_people = max(1, int(room_area / 25))

st.info(f"""
🧮 *Room Area:* {room_area} sq ft  
👥 *Max Recommended Occupancy:* {max_people} people  
👤 *Current Occupancy:* {people_count} people
""")

# --- Health Monitoring Section ---
st.subheader("🧍 Health Parameters")
respiration_rate = st.slider("Respiration Rate (breaths/min)", 10, 40, 16)
heart_rate = st.slider("Heart Rate (bpm)", 50, 160, 75)
spo2 = st.slider("Oxygen Saturation (%)", 80, 100, 98)

# --- Simulate CO₂ level ---
co2_level, status = simulate_co2(respiration_rate, heart_rate, spo2)

# Adjust status based on room occupancy
if people_count > max_people:
    status = "Critical"  # Overcrowding takes highest priority
elif people_count == max_people and status == "Normal":
    status = "Warning"  # At capacity raises warning

# --- Display Results ---
st.subheader("🌬 Air Quality Status")
col1, col2 = st.columns(2)
with col1:
    st.metric("CO₂ Level", f"{co2_level} ppm")
with col2:
    if status == "Critical":
        st.metric("Status", "CRITICAL", delta_color="off")
    elif status == "Warning":
        st.metric("Status", "WARNING", delta_color="off")
    else:
        st.metric("Status", "NORMAL", delta_color="off")

# --- Status Alerts ---
if status == "Critical":
    st.error("""
    🚨 CRITICAL ALERT! 
    - CO₂ levels dangerously high
    - Room is overcrowded (if applicable)
    - Immediate action required!
    """)
    
    # Play alarm sound (loop until conditions improve)
    components.html("""
    <audio autoplay loop>
        <source src="https://assets.mixkit.co/sfx/preview/mixkit-alarm-digital-clock-beep-989.mp3" type="audio/mpeg">
        Your browser does not support the audio element.
    </audio>
    <script>
    document.querySelector('audio').play();
    </script>
    """, height=0)

elif status == "Warning":
    st.warning("""
    ⚠ WARNING 
    - Elevated CO₂ levels detected
    - Room at maximum capacity (if applicable)
    - Monitor closely
    """)
    
    # Single beep for warning
    components.html("""
    <audio autoplay>
        <source src="https://assets.mixkit.co/sfx/preview/mixkit-alarm-digital-clock-beep-989.mp3" type="audio/mpeg">
    </audio>
    """, height=0)
else:
    st.success("✅ All parameters normal - Safe environment")

# --- Room Safety Alerts ---
if people_count > max_people:
    st.error(f"🚨 OVERCROWDING: {people_count} people in {room_area} sq ft (max {max_people})")
elif people_count == max_people:
    st.warning(f"⚠ AT CAPACITY: {people_count} people (max {max_people})")

# Manual alarm controls
st.subheader("🔊 Alarm Controls")
if st.button("Test Alarm"):
    components.html("""
    <audio autoplay>
        <source src="https://assets.mixkit.co/sfx/preview/mixkit-alarm-digital-clock-beep-989.mp3" type="audio/mpeg">
    </audio>
    """, height=0)

if st.button("Stop Alarm"):
    components.html("""
    <script>
    var audios = document.getElementsByTagName('audio');
    for (var i = 0; i < audios.length; i++) {
        audios[i].pause();
        audios[i].currentTime = 0;
    }
    </script>
    """, height=0)
