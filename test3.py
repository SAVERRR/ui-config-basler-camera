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

# กำหนดค่าเริ่มต้น
default_exposure_time = 30000
default_gain = 6
default_gamma = 1.0

# กำหนดค่าเริ่มต้นให้กับตัวแปร previous
previous_exposure_time = default_exposure_time
previous_gain = default_gain
previous_gamma = default_gamma


# Function to capture and display camera feed
def display_camera_feed(camera_id, camera_on, basler_camera=False):
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
                model_name = camera.GetDeviceInfo().GetModelName()
                pixel_format = camera.PixelFormat.GetValue()
                st.sidebar.header("Basler Camera Serial Number")
                for index, camera_info in enumerate(available_cameras):
                    st.sidebar.write(f"Serial Number - {model_name}")
                st.sidebar.header("Basler Camera Color Format")
                st.sidebar.write(f"Color Format - {pixel_format}")

            selected_camera_index = 0
            try:
                camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(available_cameras[selected_camera_index]))
                camera.Open()
                camera.GetNodeMap()
                camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
                # Set the upper limit of the camera's frame rate to 30 fps
                camera.AcquisitionFrameRateEnable.SetValue(True)
                camera.AcquisitionFrameRate.SetValue(30.0)
            except pylon.RuntimeException as e:
                print(f"Error opening Basler camera: {e}")
                time.sleep(1)
                return

            # Initialize variables for camera settings
            st.sidebar.header("Config Camera")
            exposure_time = st.sidebar.slider("Exposure Time (us)", 1, 50000, 30000)
            gain = st.sidebar.slider("Gain (dB)", 0, 24, 6)
            gamma = st.sidebar.slider("Gamma", 0.0000, 4.0000, 1.0000)
            set_selector = st.sidebar.selectbox("User Set Control",
                                               ["Default User Set", "High Gain", "Auto Functions", "Color Raw", "User Set 1",
                                                "User Set 2", "User Set 3"])
            set_save = st.sidebar.button("Save")
            set_load = st.sidebar.button("Load")

            def set_save_value():
                if set_selector == "Default User Set":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_Default)
                    camera.UserSetSave.Execute()
                elif set_selector == "High Gain":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_HighGain)
                    camera.UserSetSave.Execute()
                elif set_selector == "Auto Functions":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_AutoFunctions)
                    camera.UserSetSave.Execute()
                elif set_selector == "Color Raw":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_ColorRaw)
                    camera.UserSetSave.Execute()
                elif set_selector == "User Set 1":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_UserSet1)
                    camera.UserSetSave.Execute()
                elif set_selector == "User Set 2":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_UserSet2)
                    camera.UserSetSave.Execute()
                elif set_selector == "User Set 3":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_UserSet3)
                    camera.UserSetSave.Execute()

            def set_load_value():
                if set_selector == "Default User Set":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_Default)
                    camera.UserSetLoad.Execute()
                elif set_selector == "High Gain":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_HighGain)
                    camera.UserSetLoad.Execute()
                elif set_selector == "Auto Functions":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_AutoFunctions)
                    camera.UserSetLoad.Execute()
                elif set_selector == "Color Raw":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_ColorRaw)
                    camera.UserSetLoad.Execute()
                elif set_selector == "User Set 1":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_UserSet1)
                    camera.UserSetLoad.Execute()
                elif set_selector == "User Set 2":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_UserSet2)
                    camera.UserSetLoad.Execute()
                elif set_selector == "User Set 3":
                    camera.UserSetSelector.SetValue(pylon.UserSetSelector_UserSet3)
                    camera.UserSetLoad.Execute()

            #if st.sidebar.button("Save",key="save_button"):
                #set_save_value()

            #if st.sidebar.button("Load",key="load_button"):
                #set_load_value()

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

                    frame_placeholder.image(frame, channels="Mono", use_column_width=True)

                    time.sleep(0.005)
                except Exception as e:
                    print(f"Wait for config: {e}")

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

# Display camera feed when the camera is on
if camera_on:
    display_camera_feed(camera_id, camera_on, basler_camera)
