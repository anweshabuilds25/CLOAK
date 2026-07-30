import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
from detection import process_frame

st.title("MediaPipe Hands Test")

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    img = process_frame(img)
    return av.VideoFrame.from_ndarray(img, format="bgr24")

webrtc_streamer(key="mediapipe-test", video_frame_callback=video_frame_callback)