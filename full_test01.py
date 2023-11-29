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
def display_camera_feed(camera_id, camera_on, basler_camera=False, loaded_values=None):
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
            exposure_time = st.sidebar.slider("Exposure Time (us)", 1, 200000, 30000)
            gain = st.sidebar.slider("Gain (dB)", 0, 24, 6)
            gamma = st.sidebar.slider("Gamma", 0.0000, 4.0000, 1.0000,)
            set_selector = st.sidebar.selectbox("User Set Control",
                                               ["Default User Set", "High Gain", "Auto Functions", "Color Raw", "User Set 1",
                                                "User Set 2", "User Set 3"])
            #set_save = st.sidebar.button("Save")
            #set_load = st.sidebar.button("Load")

            print(exposure_time)
            print(gain)
            print(gamma)

            def set_save_value():
                try:
                    # Save the current user-set configuration to a file (JSON)
                    with open("user_settings.json", "w") as file:
                        json.dump({
                            "exposure_time": exposure_time,
                            "gain": gain,
                            "gamma": gamma,
                            "user_set": set_selector,  # เพิ่มการบันทึก User Set
                        }, file)
                    st.sidebar.success("Settings saved successfully!")
                except Exception as e:
                    st.sidebar.error(f"Error saving settings: {e}")

            def set_load_value():
                try:
                    # Load the user-set configuration from the file (JSON)
                    with open("user_settings.json", "r") as file:
                        loaded_settings = json.load(file)
            
                    # ให้ตัวแปรกลางเก็บค่าที่โหลดมา
                    exposure_time = loaded_settings["exposure_time"]
                    gain = loaded_settings["gain"]
                    gamma = loaded_settings["gamma"]

                    st.experimental_set_query_params(exposure_slider=exposure_time, gain_slider=gain, gamma_slider=gamma, set_selector=loaded_settings["user_set"])
                    st.sidebar.success("Settings loaded successfully!")
                    
                    return exposure_time, gain, gamma, loaded_settings["user_set"]
                except Exception as e:
                    st.sidebar.error(f"Error loading settings: {e}")
                    return None
                
        
            if st.sidebar.button("Save",key="save_button"):
                set_save_value()

            if st.sidebar.button("Load",key="load_button"):
                loaded_values = set_load_value()

            frame_placeholder = st.empty()
            while camera_on:  # Keep capturing while the camera is on
                try:
                    if not basler_camera:
                        ret, frame = cap.read()
                        if not ret:
                            break

                    # บันทึกค่าเดิมก่อนที่จะทำการ SetValue
                    previous_exposure_time = camera.ExposureTime.GetValue()
                    previous_gain = camera.Gain.GetValue()
                    previous_gamma = camera.Gamma.GetValue()
                    # Update camera settings for Basler camera
                    try:
                        camera.ExposureTime.SetValue(exposure_time)
                        camera.Gain.SetValue(gain)
                        camera.Gamma.SetValue(gamma)
                    except pylon.RuntimeException as config_error:
                        print(f"Error while configuring camera: {config_error}")
                        camera.ExposureTime.SetValue(previous_exposure_time)
                        camera.Gain.SetValue(previous_gain)
                        camera.Gamma.SetValue(previous_gamma)
                    grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                    if grab_result.GrabSucceeded():
                        frame = grab_result.Array
                    else:
                        print("Failed to grab frame from Basler camera.")
                        break

                    frame_placeholder.image(frame, channels="BGR" if color_format.startswith("BGR") else "Mono", use_column_width=True)

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
    camera_id = 1
    basler_camera = False
else:
    # If Basler Camera is selected
    camera_id = None
    basler_camera = True

loaded_values = None

# Display camera feed when the camera is on
if camera_on:
    display_camera_feed(camera_id, camera_on, basler_camera,loaded_values)
