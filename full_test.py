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

# Function to capture and display camera feed
def display_camera_feed(camera_id, camera_on, basler_camera=False):
    # Initialize white balance sliders
    white_balance_red = 128
    white_balance_green = 128
    white_balance_blue = 128

    if not basler_camera:
        cap = cv2.VideoCapture(camera_id)
    else:
        # Connect Basler camera
        available_cameras = pylon.TlFactory.GetInstance().EnumerateDevices()
        if not available_cameras:
            st.warning("No Basler cameras found. Please make sure your Basler camera is connected.")
            return
        else:
            st.sidebar.header("Basler Camera Serial Number")
            for index, camera_info in enumerate(available_cameras):
                st.sidebar.write(f"Serial Number - {camera_info.GetSerialNumber()}")
        selected_camera_index = 0
        camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(available_cameras[selected_camera_index]))
        camera.Open()
        camera.GetNodeMap()
        camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    frame_placeholder = st.empty()
    while camera_on:
        if not basler_camera:
            ret, frame = cap.read()
            if not ret:
                break

        if basler_camera:
            grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grab_result.GrabSucceeded():
                frame = grab_result.Array
            else:
                st.warning("Failed to grab frame from Basler camera.")
                break

        # Apply white balance
        if white_balance:
            frame[:, :, 2] = np.clip(frame[:, :, 2] * white_balance_red / 255, 0, 255).astype(np.uint8)
            frame[:, :, 1] = np.clip(frame[:, :, 1] * white_balance_green / 255, 0, 255).astype(np.uint8)
            frame[:, :, 0] = np.clip(frame[:, :, 0] * white_balance_blue / 255, 0, 255).astype(np.uint8)

        frame_placeholder.image(frame, channels="Mono", use_column_width=True)

        time.sleep(0.005)

    if not basler_camera:
        cap.release()
    else:
        camera.StopGrabbing()
        camera.Close()

# White balance controls
white_balance = st.sidebar.checkbox("White Balance")
if white_balance:
    white_balance_red = st.sidebar.slider("Red", 0, 255, 128)
    white_balance_green = st.sidebar.slider("Green", 0, 255, 128)
    white_balance_blue = st.sidebar.slider("Blue", 0, 255, 128)

if selected_camera == "Webcam":
    camera_id = 0  # Use 0 for the default webcam
    basler_camera = False
else:
    # If Basler Camera is selected
    camera_id = None
    basler_camera = True

# Display camera feed when the camera is on
if camera_on:
    display_camera_feed(camera_id, camera_on, basler_camera)
