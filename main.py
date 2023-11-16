import streamlit as st
import cv2
import numpy as np
from pypylon import pylon
import time

# Page title and description
st.title("Display Camera feed")

# Sidebar for camera selection and settings
st.sidebar.header("Camera Settings")
selected_camera = st.sidebar.selectbox("Select Camera", ["Webcam", "Basler Camera USB", "Basler Camera Gige"])
st.sidebar.header("Camera")

# Add a toggle for camera on/off
camera_on = st.sidebar.toggle("On/Off", value=False)   
if camera_on:
    st.sidebar.write("Camera is On")
else:

    st.sidebar.write("Camera is Off")
    
# Initialize variables for camera settings
exposure_time = 10000
gain = 6
brightness = 0
sharpness = 50
contrast = 0
saturation = 0
white_balance = 5000

# Function to capture and display camera feed
def display_camera_feed(camera_id, camera_on, basler_camera=False):
    global exposure_time, gain, brightness, sharpness, contrast, saturation, white_balance

    if not basler_camera:
        cap = cv2.VideoCapture(camera_id)
    else:
        # Connect Basler camera
        available_cameras = pylon.TlFactory.GetInstance().EnumerateDevices()
        if not available_cameras:
            st.warning("No Basler cameras found. Please make sure your Basler camera is connected.")
            return
        selected_camera_index = 0
        camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(available_cameras[selected_camera_index]))
        camera.Open()
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        # Configurations for Basler camera 
        st.sidebar.header("Config Camera")
        exposure_time = st.sidebar.slider("Exposure Time (us)", 1, 50000, exposure_time)
        gain = st.sidebar.slider("Gain (dB)", 0, 24, gain)
        brightness = st.sidebar.slider("Brightness", -50, 50, brightness)
        sharpness = st.sidebar.slider("Sharpness", 0, 100, sharpness)
        contrast = st.sidebar.slider("Contrast", -100, 100, contrast)  
        saturation = st.sidebar.slider("Saturation", -100, 100, saturation)
        white_balance = st.sidebar.slider("White Balance", 2000, 10000, white_balance)

    frame_placeholder = st.empty()
    while camera_on:  # Keep capturing while the camera is on
        if not basler_camera:
            ret, frame = cap.read()
            if not ret:
                break  
        else:
            grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grab_result.GrabSucceeded():
                frame = grab_result.Array  
            else:
                st.warning("Failed to grab frame from Basler camera.")
                break

        frame_placeholder.image(frame, channels="BGR", use_column_width=True)

        time.sleep(0.005)   

    if not basler_camera:
        cap.release()
    else:
        camera.StopGrabbing()
        camera.Close()
        
if selected_camera == "Webcam":
    camera_id = 1
    basler_camera = False
else:
    # If Basler Camera is selected
    camera_id = None
    basler_camera = True

# Display camera feed when the camera is on
if camera_on:
    display_camera_feed(camera_id, camera_on, basler_camera) 