import streamlit as st
import cv2
import numpy as np
from pypylon import pylon
import time
import json

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
def display_camera_feed(camera_id, camera_on, basler_camera=False, loaded_values=None, set_selector=None):
    try:
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
                    st.sidebar.header("Basler Camera Model")
                    st.sidebar.write(f"Model - {camera_info.GetModelName()}")

            selected_camera_index = 0
            try:
                camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(available_cameras[selected_camera_index]))
                camera.Open()
                camera.GetNodeMap()
                camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
                # Set the upper limit of the camera's frame rate to 30 fps
                camera.AcquisitionFrameRateEnable.SetValue(True)
                camera.AcquisitionFrameRate.SetValue(30.0)
                color_format = camera.PixelFormat.GetValue()
                st.sidebar.header("Basler Camera Color Format")
                st.sidebar.write(f"Type - {color_format}")
            except pylon.RuntimeException as e:
                print(f"Error opening Basler camera: {e}")
                time.sleep(0.005)
                return

            # Initialize variables for camera settings
            st.sidebar.header("Config Camera")
            exposure_slider = st.sidebar.slider("Exposure Time (us)", 1, 200000, 30000)
            gain_slider = st.sidebar.slider("Gain (dB)", 0, 24, 6)
            gamma_slider = st.sidebar.slider("Gamma", 0.0000, 4.0000, 1.0000)
            set_selector = st.sidebar.selectbox("User Set Control",
                                                ["Default User Set", "High Gain", "Auto Functions", "Color Raw",
                                                 "User Set 1", "User Set 2", "User Set 3"], key="set_selector")

            def set_save_value(serial_number, set_selector):
                try:
                    filename = f"user_settings_{serial_number}_{set_selector.lower().replace(' ', '_')}.json"
                    with open(filename, "w") as file:
                        json.dump({
                            "exposure_time": exposure_slider,
                            "gain": gain_slider,
                            "gamma": gamma_slider,
                            "user_set": set_selector,
                        }, file)
                    st.sidebar.success(f"Settings saved successfully to {filename}!")
                except Exception as e:
                    st.sidebar.error(f"Error saving settings: {e}")

            def set_load_value(serial_number, set_selector, loaded_values):
                try:
                    filename = f"user_settings_{serial_number}_{set_selector.lower().replace(' ', '_')}.json"
                    with open(filename, "r") as file:
                        loaded_settings = json.load(file)

                    # Update the variables with the loaded settings
                    exposure_slider = loaded_settings["exposure_time"]
                    gain_slider = loaded_settings["gain"]
                    gamma_slider = loaded_settings["gamma"]
                    set_selector = loaded_settings["user_set"]

                    if loaded_values is not None:
                        loaded_values["exposure_slider"] = exposure_slider
                        loaded_values["gain_slider"] = gain_slider
                        loaded_values["gamma_slider"] = gamma_slider
                        loaded_values["set_selector"] = set_selector

                    st.sidebar.success(f"Settings loaded successfully from {filename}!")

                    return exposure_slider, gain_slider, gamma_slider, set_selector
                except Exception as e:
                    st.sidebar.error(f"Error loading settings: {e}")
                    return None

            # Use the placeholder for the buttons
            save_button = st.sidebar.button("Save", key="save_button")
            load_button = st.sidebar.button("Load", key="load_button")

            if save_button:
                set_save_value(available_cameras[selected_camera_index].GetSerialNumber(), set_selector)

            if load_button:
                exposure_slider, gain_slider, gamma_slider, set_selector = set_load_value(available_cameras[selected_camera_index].GetSerialNumber(), set_selector, loaded_values)
        
            if loaded_values is not None and load_button:
                exposure_slider, gain_slider, gamma_slider, set_selector = set_load_value(available_cameras[selected_camera_index].GetSerialNumber(), set_selector, loaded_values)
            
            frame_placeholder = st.empty()
            while camera_on:  # Keep capturing while the camera is on
                try:
                    if not basler_camera:
                        ret, frame = cap.read()
                        st.image(frame, channels="BGR")
                        if not ret:
                            break

                    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                    if grab_result.GrabSucceeded():
                        frame = grab_result.Array
                    else:
                        print("Failed to grab frame from Basler camera.")
                        break

                    # Apply loaded values to the camera settings
                    camera.ExposureTime.SetValue(exposure_slider)
                    camera.Gain.SetValue(gain_slider)
                    camera.Gamma.SetValue(gamma_slider)

                    frame_placeholder.image(frame, channels="BGR" if color_format.startswith("BGR") else "Mono",
                                             use_column_width=True)

                    time.sleep(0.005)
                except Exception as e:
                    print(f"Wait for config: {e}")
                    break

            camera.StopGrabbing()
            camera.Close()

        if not basler_camera:
            cap.release()
        else:
            camera.StopGrabbing()
            camera.Close()

    except Exception as e:
        print(f"Unexpected error: {e}")

if selected_camera == "Webcam":
    camera_id = 0
    basler_camera = False
else:
    # If Basler Camera is selected
    camera_id = None
    basler_camera = True

loaded_values = None

# Display camera feed when the camera is on
if camera_on:
    if loaded_values is None:
        loaded_values = {}
    display_camera_feed(camera_id, camera_on, basler_camera, loaded_values)
    
