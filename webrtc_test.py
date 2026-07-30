import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av

st.title("Webcam Test")

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    return av.VideoFrame.from_ndarray(img, format="bgr24")

webrtc_streamer(key="test", video_frame_callback=video_frame_callback)