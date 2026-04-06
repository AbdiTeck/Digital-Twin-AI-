import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(layout="wide")

# -----------------------------
# DARK UI
# -----------------------------
st.markdown("""
<style>
.stApp {
    background-color: #000000;
}

.card {
    background-color: #0a1a22;
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 0px 15px rgba(0,255,150,0.1);
}

.big-number {
    font-size: 32px;
    font-weight: bold;
    color: #00ff88;
}

.label {
    color: #8aa;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# AUTO REFRESH
# -----------------------------
st_autorefresh(interval=3000, key="refresh")

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "temp" not in st.session_state:
    st.session_state.temp = 70.0
    st.session_state.vib = 5.0
    st.session_state.pres = 100.0

if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame(
        columns=["Temperature", "Vibration", "Pressure"]
    )

if "was_failure" not in st.session_state:
    st.session_state.was_failure = False

# -----------------------------
# TITLE + TOP-RIGHT GIF
# -----------------------------
col_title, col_gif = st.columns([3, 1])

with col_title:
    st.title("⚓ AI Digital Twin – Pump Monitoring")

with col_gif:
    st.image("assets/ai_alert.gif", use_container_width=True)

# -----------------------------
# MODE
# -----------------------------
mode = st.selectbox("Operating Mode", ["Normal", "Degrading", "Failure"])

# Track failure
if mode == "Failure":
    st.session_state.was_failure = True

# -----------------------------
# SIMULATION (FIXED 🔥)
# -----------------------------
if mode == "Failure":
    # ❄️ Freeze system
    pass

elif mode == "Degrading":
    st.session_state.temp += np.random.uniform(0.3, 1.0)
    st.session_state.vib += np.random.uniform(0.1, 0.5)
    st.session_state.pres -= np.random.uniform(0.3, 1.0)

elif mode == "Normal":
    # 🔄 Reset after failure
    if st.session_state.was_failure:
        st.session_state.temp = 70.0
        st.session_state.vib = 5.0
        st.session_state.pres = 100.0
        st.session_state.was_failure = False

    st.session_state.temp += np.random.uniform(-0.5, 0.5)
    st.session_state.vib += np.random.uniform(-0.2, 0.2)
    st.session_state.pres += np.random.uniform(-0.5, 0.5)

temperature = st.session_state.temp
vibration = st.session_state.vib
pressure = st.session_state.pres

# -----------------------------
# HISTORY
# -----------------------------
new_row = pd.DataFrame([{
    "Temperature": float(temperature),
    "Vibration": float(vibration),
    "Pressure": float(pressure)
}])

st.session_state.history = pd.concat(
    [st.session_state.history, new_row],
    ignore_index=True
).tail(30)

# -----------------------------
# MODEL
# -----------------------------
X = pd.DataFrame(
    np.random.rand(200, 3) * [120, 20, 120],
    columns=["Temperature", "Vibration", "Pressure"]
)

y = (
    (X["Temperature"] > 100) |
    (X["Vibration"] > 15) |
    (X["Pressure"] < 90)
).astype(int)

model = RandomForestClassifier()
model.fit(X, y)

input_df = pd.DataFrame([{
    "Temperature": temperature,
    "Vibration": vibration,
    "Pressure": pressure
}])

prediction = model.predict(input_df)[0]
confidence = model.predict_proba(input_df)[0][1]

# -----------------------------
# HEALTH
# -----------------------------
health = 100 - (
    0.5 * max(0, temperature - 70) +
    2.0 * max(0, vibration - 5) +
    1.5 * max(0, 100 - pressure)
)
health = max(0, min(100, health))

# -----------------------------
# STATUS COLORS
# -----------------------------
if mode == "Failure":
    status = "🔴 RISK"
    status_color = "red"
elif mode == "Degrading":
    status = "🟡 WARNING"
    status_color = "orange"
else:
    status = "🟢 NORMAL"
    status_color = "#00ff88"

# -----------------------------
# AGENT LOGIC
# -----------------------------
def explain(temp, vib, pres):
    reasons = []
    if temp > 100:
        reasons.append("High temperature")
    if vib > 15:
        reasons.append("High vibration")
    if pres < 90:
        reasons.append("Low pressure")
    return reasons if reasons else ["System stable"]

def agent(temp, vib, pres, health):
    actions = []
    if temp > 100:
        actions.append("Reduce load")
    if vib > 15:
        actions.append("Inspect bearings")
    if pres < 90:
        actions.append("Check pressure system")
    if health < 30 or mode == "Failure":
        actions.append("🚨 Emergency shutdown executed")
    return actions if actions else ["No action needed"]

reasons = explain(temperature, vibration, pressure)
actions = agent(temperature, vibration, pressure, health)

# -----------------------------
# TOP CARDS
# -----------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="label">Pump Health</div>
        <div class="big-number">{health:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="label">AI Confidence</div>
        <div class="big-number">{confidence*100:.0f}%</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="label">System Status</div>
        <div class="big-number" style="color:{status_color}">
            {status}
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# SENSOR CARDS
# -----------------------------
col4, col5, col6 = st.columns(3)

with col4:
    st.markdown(f"""
    <div class="card">
        <div class="label">Temperature</div>
        <div class="big-number">{temperature:.1f}°C</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="card">
        <div class="label">Vibration</div>
        <div class="big-number">{vibration:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="card">
        <div class="label">Pressure</div>
        <div class="big-number">{pressure:.1f}</div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# GIF + SHUTDOWN
# -----------------------------
col_img, col_data = st.columns([1.2, 1])

with col_img:
    if mode == "Failure":
        try:
            st.image("assets/pump_off.png", use_container_width=True)
        except:
            st.image("assets/pump.gif", use_container_width=True)

        st.markdown(
            "<h3 style='color:red; text-align:center;'>⛔ SYSTEM SHUTDOWN</h3>",
            unsafe_allow_html=True
        )
    else:
        st.image("assets/pump.gif", use_container_width=True)

# -----------------------------
# BAR CHART
# -----------------------------
with col_data:
    st.subheader("📈 Live Sensor Data")

    fig, ax = plt.subplots(figsize=(3.5, 1.8))

    latest = st.session_state.history.tail(1).iloc[0]

    labels = ["Temp", "Vib", "Press"]
    values = [
        latest["Temperature"],
        latest["Vibration"],
        latest["Pressure"]
    ]

    ax.bar(labels, values, width=0.5, color="#00ff88")
    ax.set_ylim(0, 80)

    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.tick_params(colors='white')

    for spine in ax.spines.values():
        spine.set_visible(False)

    st.pyplot(fig)

# -----------------------------
# AI PANEL
# -----------------------------
col7, col8 = st.columns(2)

with col7:
    st.subheader("🧠 WHY")
    for r in reasons:
        st.write("-", r)

with col8:
    st.subheader("🤖 AI Agent")

    if mode == "Failure":
        st.error("🚨 CRITICAL FAILURE DETECTED")
        st.write("→ AI has taken control")
        st.write("→ Pump operation terminated")
        st.write("→ Preventing damage")
        st.write("→ Awaiting inspection")

    elif mode == "Degrading":
        st.warning("⚠️ Degrading system")
        st.write("→ Maintenance recommended")
        st.write("→ Monitor closely")

    else:
        st.success("✅ System stable")
        st.write("→ Operating normally")

# -----------------------------
# FORECAST
# -----------------------------
st.subheader("🔮 Forecast")

if mode == "Failure":
    st.error("🚨 CRITICAL FAILURE → EMERGENCY SHUTDOWN")
elif mode == "Degrading":
    st.warning("⚠️ System degrading → maintenance recommended")
else:
    st.success("✅ Stable operation")