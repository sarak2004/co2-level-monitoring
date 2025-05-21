import streamlit as st
import base64

# --- Simulate CO₂ level based on health parameters ---
def simulate_co2(respiration_rate, heart_rate, spo2, people_count, max_people):
    if respiration_rate > 25 or spo2 < 90 or heart_rate < 62 or heart_rate > 100 or people_count > max_people:
        return 1000, "Critical"
    elif respiration_rate > 18 or spo2 < 95 or heart_rate >= 100 or people_count == max_people:
        return 700, "Warning"
    else:
        return 400, "Normal"

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

# --- Function to play audio in hidden HTML ---
def autoplay_audio(file_path):
    with open(file_path, "rb") as f:
        audio_data = f.read()
    b64_audio = base64.b64encode(audio_data).decode()
    audio_html = f"""
        <audio autoplay hidden>
            <source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3">
        </audio>
    """
    st.markdown(audio_html, unsafe_allow_html=True)

# --- Streamlit UI ---
st.title("🫁 CO₂ Level + Room Safety Simulation")

# --- Room Occupancy ---
st.subheader("🏠 Room & Occupancy Details")
room_length = st.number_input("Room Length (ft)", min_value=10, max_value=50, value=10, step=5)
room_width = st.number_input("Room Width (ft)", min_value=10, max_value=50, value=10, step=5)
people_count = st.number_input("Number of People in the Room", min_value=1, step=1)

room_area = room_length * room_width
max_people = get_max_people(room_area)

st.write(f"🧮 Room Area: {room_area} sq ft")
st.write(f"👥 Max Recommended Occupancy: {max_people} people")

# --- Check overcrowding ---
if people_count > max_people:
    st.error(f"🚨 Overcrowded! Room has {people_count} people (limit is {max_people}).")
elif people_count == max_people:
    st.warning(f"🚨 Room has {people_count} people, Limit Reached.")
else:
    st.info("✅ Occupancy is within safe limit.")

# --- Health Parameters ---
st.subheader("🧍 Health Monitoring")
respiration_rate = st.slider("Respiration Rate (breaths/min)", 10, 40, 16)
heart_rate = st.slider("Heart Rate (bpm)", 50, 160, 75)
spo2 = st.slider("Oxygen Saturation (%)", 80, 100, 98)

# --- Simulate CO₂ level ---
co2_level, status = simulate_co2(respiration_rate, heart_rate, spo2, people_count, max_people)

# --- Display results ---
st.metric("Simulated CO₂ Level", f"{co2_level} ppm")
st.metric("Status", status)

# --- Play alarm only if critical or overcrowded ---
if status == "Critical" or people_count > max_people:
    st.error("⚠ Critical CO₂ Level! Immediate action required!")
    autoplay_audio("alarm.mp3")
elif status == "Warning" or people_count == max_people:
    st.warning("🚨 Elevated CO₂ Level! Monitor closely.")
else:
    st.success("✅ CO₂ Level is Normal.")
