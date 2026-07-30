import streamlit as st
import time
import cv2
import av
import mediapipe as mp
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh
from classifier import predict

st.set_page_config(page_title="Weather", layout="centered")

# ---- Session state ----
if "alert_log" not in st.session_state:
    st.session_state.alert_log = []
if "last_trigger_time" not in st.session_state:
    st.session_state.last_trigger_time = 0

TRUSTED_CONTACTS = ["Mom", "Dad", "Priya (Friend)"]
COOLDOWN_SECONDS = 15  # prevent spamming repeat alerts

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils


class SignalProcessor:
    def __init__(self):
        self.hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.signal_start_time = None
        self.triggered = False

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]

            # Draw landmarks on the frame so demo mode can show them
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            pred = predict(landmarks)

            if pred == 1:
                if self.signal_start_time is None:
                    self.signal_start_time = time.time()
                elapsed = time.time() - self.signal_start_time
                if elapsed >= 1.5:
                    self.triggered = True
                    cv2.putText(img, "SIGNAL DETECTED", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                else:
                    cv2.putText(img, f"Holding... {elapsed:.1f}s", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
            else:
                self.signal_start_time = None
                self.triggered = False
        else:
            self.signal_start_time = None
            self.triggered = False

        return av.VideoFrame.from_ndarray(img, format="bgr24")


# ---- Demo mode toggle (moved up so we know its value before hiding/showing video) ----
st.divider()
with st.expander("⚙️ App Settings"):
    demo_mode = st.checkbox("Demo Mode (show detection dashboard)", value=False)

# ---- Webcam processor ----
ctx = webrtc_streamer(
    key="cloak-detector",
    mode=WebRtcMode.SENDRECV,
    video_processor_factory=SignalProcessor,
    media_stream_constraints={
        "video": {"width": 320, "height": 240, "frameRate": 15},
        "audio": False,
    },
    desired_playing_state=True,
)

# ---- Hide video feed UNLESS demo mode is on ----
if not demo_mode:
    st.markdown("""
        <style>
        iframe {
            height: 0px !important;
            min-height: 0px !important;
            max-height: 0px !important;
            border: none !important;
            visibility: hidden !important;
            position: absolute !important;
            pointer-events: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.info("🔍 Demo Mode: live detection feed visible below (hidden in real deployment)")

# ---- Poll every second for trigger state ----
st_autorefresh(interval=1000, key="poll")

if ctx.video_processor:
    if ctx.video_processor.triggered:
        now = time.time()
        if now - st.session_state.last_trigger_time > COOLDOWN_SECONDS:
            st.session_state.last_trigger_time = now
            st.session_state.alert_log.append({
                "contacts": TRUSTED_CONTACTS,
                "time": time.strftime("%H:%M:%S"),
                "location": "Last known: VIT Bhopal Campus"
            })
        ctx.video_processor.triggered = False  # reset after logging

# ---- Decoy Weather UI ----
st.title("🌤️ Weather")
st.subheader("Bhopal, MP")
st.metric(label="Temperature", value="31°C", delta="1.2°C")
st.write("Partly cloudy · Humidity 58% · Wind 12 km/h")

st.divider()
st.caption("5-Day Forecast")

cols = st.columns(5)
days = ["Thu", "Fri", "Sat", "Sun", "Mon"]
temps = ["31°", "29°", "33°", "30°", "28°"]
icons = ["🌤️", "🌧️", "☀️", "⛅", "🌦️"]

for col, day, temp, icon in zip(cols, days, temps, icons):
    with col:
        st.write(day)
        st.write(icon)
        st.write(temp)

# ---- Alert Log (only shown in demo mode) ----
if demo_mode:
    st.divider()
    st.subheader("🚨 Alert Log (Demo View)")
    if not st.session_state.alert_log:
        st.info("No alerts triggered yet.")
    else:
        for alert in reversed(st.session_state.alert_log):
            st.error(
                f"**{alert['time']}** — Alert sent to: {', '.join(alert['contacts'])}\n\n"
                f"📍 {alert['location']}"
            )