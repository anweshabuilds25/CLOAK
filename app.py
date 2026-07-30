import streamlit as st

st.set_page_config(page_title="Weather", layout="centered")

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