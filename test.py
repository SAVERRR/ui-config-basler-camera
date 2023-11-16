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


        # Initialize variables for camera settings
        st.sidebar.header("Config Camera")
        pixel_format = st.sidebar.selectbox("Select PixelFormat", ["BGR8", "Mono8"])  # Add more options as needed
        format_button = st.sidebar.button("Format")
        exposure_time = st.sidebar.slider("Exposure Time (us)", 1, 50000, 30000)
        gain = st.sidebar.slider("Gain (dB)", 0, 24, 6)
        gamma = st.sidebar.slider("Gamma",0.0000, 4.0000, 1.0000)
        set_selector = st.sidebar.selectbox("User Set Control",["Default User Set","High Gain","Auto Functions","Color Raw","User Set 1","User Set 2","User Set 3"])
        set_save = st.sidebar.button("Save")
        set_load = st.sidebar.button("Load")
        
        #white_balance_red = st.sidebar.slider("Red")
        #white_balance_green = st.sidebar.slider("Green")
        #white_balance_blue = st.sidebar.slider("Blue")

        # Function to set PixelFormat
        def set_pixel_format():
            selected_format = str(pixel_format)

            if selected_format == "BGR8":
                camera.PixelFormat.SetValue(pylon.PixelType_BGR8)

            
            elif selected_format == "Mono8":
                camera.PixelFormat.SetValue(pylon.PixelType_Mono8)
 
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


            if format_button :
                set_pixel_format()
            if set_save :
                set_save_value()
            if set_load :
                set_load_value()

        frame_placeholder = st.empty()
        while camera_on:  # Keep capturing while the camera is on
            if not basler_camera:
                ret, frame = cap.read()
                if not ret:
                    break              
            
            # Update camera settings for Basler camera
            camera.ExposureTime.SetValue(exposure_time)
            camera.Gain.SetValue(gain)
            camera.Gamma.SetValue(gamma)
            

            grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
            if grab_result.GrabSucceeded():
                frame = grab_result.Array  
            else:
                st.warning("Failed to grab frame from Basler camera.")
                break

            frame_placeholder.image(frame, channels="Mono", use_column_width=True)

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




#camera.ExposureAuto.SetValue(ExposureAuto_Off); #ExposureAuto
#camera.PixelFormat.SetValue(PixelFormat_BGR8)   #PixelFormat
#camera.UserSetSelector.SetValue(UserSetSelector_UserSet1); #Save
#camera.UserSetSelector.SetValue(UserSetSelector_UserSet1); #Load 
#camera.Gamma.SetValue(0.51999); #Gamma
#camera.UserSetSelector.SetValue(UserSetSelector_UserSet1);
