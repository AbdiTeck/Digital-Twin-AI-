import streamlit as st
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier

st.markdown("""
<style>
.blink {
    animation: blinker 1s linear infinite;
    color: red;
    font-size: 28px;
    font-weight: bold;
    text-align: center;
}
@keyframes blinker {
    50% { opacity: 0; }
}
</style>
""", unsafe_allow_html=True)

st.set_page_config(layout="wide")

# -----------------------------
# SESSION STATE (IMPORTANT)
# -----------------------------
if "mode" not in st.session_state:
    st.session_state.mode = "Normal"

if "data" not in st.session_state:
    st.session_state.data = []

# -----------------------------
# HEADER
# -----------------------------
st.title("🧠 Digital Twin Pump Dashboard")

# -----------------------------
# MODE SELECTOR (SOFT RESET)
# -----------------------------
mode = st.selectbox("Operating Mode", ["Normal", "Degrading", "Failure"])

# Reset hvis mode endres
if mode != st.session_state.mode:
    st.session_state.mode = mode
    st.session_state.data = []

# -----------------------------
# GENERATE SENSOR DATA
# -----------------------------
def generate_data(mode):
    if mode == "Normal":
        return (
            np.random.normal(70, 2),   # temp
            np.random.normal(5, 1),    # vib
            np.random.normal(100, 2)   # pressure
        )
    elif mode == "Degrading":
        return (
            np.random.normal(90, 5),
            np.random.normal(10, 2),
            np.random.normal(95, 3)
        )
    else:  # Failure
        return (
            np.random.normal(110, 5),
            np.random.normal(18, 3),
            np.random.normal(85, 4)
        )

# -----------------------------
# UPDATE DATA (LIVE)
# -----------------------------
temp, vib, pres = generate_data(mode)

st.session_state.data.append({
    "temperature": temp,
    "vibration": vib,
    "pressure": pres
})

df = pd.DataFrame(st.session_state.data)

# Keep last 50 points
df = df.tail(50)

# -----------------------------
# TRAIN AI MODEL
# -----------------------------
# Synthetic training data
X = pd.DataFrame({
    "temperature": np.random.uniform(60, 120, 500),
    "vibration": np.random.uniform(2, 20, 500),
    "pressure": np.random.uniform(80, 110, 500)
})

y = ((X["temperature"] > 100) | 
     (X["vibration"] > 15) | 
     (X["pressure"] < 90)).astype(int)

model = RandomForestClassifier()
model.fit(X, y)

# -----------------------------
# PREDICTION INPUT
# -----------------------------
input_df = pd.DataFrame({
    "temperature": [temp],
    "vibration": [vib],
    "pressure": [pres]
})

prediction = model.predict(input_df)[0]

# -----------------------------
# HEALTH SCORE
# -----------------------------
health = 100 - (
    0.7 * max(0, temp - 70) +
    2.0 * max(0, vib - 5) +
    1.5 * max(0, 100 - pres)
)

health = max(0, min(100, health))

# -----------------------------
# STATUS LOGIC (FIXED)
# -----------------------------
if temp > 100 or vib > 15 or pres < 90:
    status = "🔴 FAILURE LIKELY"
    color = "red"
elif temp > 85 or vib > 10 or pres < 95:
    status = "🟡 DEGRADING"
    color = "orange"
else:
    status = "🟢 NORMAL"
    color = "green"

# -----------------------------
# LAYOUT (NO SCROLL)
# -----------------------------
col1, col2 = st.columns([2, 1])

# -----------------------------
# LEFT: SENSOR DATA
# -----------------------------
with col1:
    st.subheader("📈 Live Sensor Data (Digital Twin)")
    st.line_chart(df, width='stretch')

# -----------------------------
# RIGHT: AI VOTING
# -----------------------------
with col2:
    st.subheader("🧠 AI Voting System")

    votes = [tree.predict(input_df.values)[0] for tree in model.estimators_]

    normal_votes = votes.count(0)
    failure_votes = votes.count(1)

    vote_df = pd.DataFrame({
        "Prediction": ["Normal", "Failure"],
        "Votes": [normal_votes, failure_votes]
    })

    fig2, ax2 = plt.subplots()

    colors = ["green", "red"]

    ax2.bar(vote_df["Prediction"], vote_df["Votes"], color=colors)
    ax2.set_ylabel("Votes")
    ax2.set_title("AI Decision Votes")
    ax2.set_ylim(0, len(model.estimators_))

    st.pyplot(fig2, width='stretch')

# -----------------------------
# STATUS PANEL
# -----------------------------
st.markdown("---")

col3, col4, col5 = st.columns(3)

with col3:
    st.metric("🌡️ Temperature", f"{temp:.1f} °C")

with col4:
    st.metric("📳 Vibration", f"{vib:.1f}")

with col5:
    st.metric("⚙️ Pressure", f"{pres:.1f}")

# -----------------------------
# HEALTH DISPLAY
# -----------------------------
st.markdown(f"### ❤️ Health Score: {health:.1f}%")

st.progress(health / 100)

# -----------------------------
# STATUS TEXT
# -----------------------------
if "FAILURE" in status:
    st.markdown('<div class="blink">🚨 CRITICAL FAILURE 🚨</div>', unsafe_allow_html=True)
else:
    st.markdown(f"## {status}")

# -----------------------------
# AUTO REFRESH
# -----------------------------
time.sleep(1)
st.rerun()