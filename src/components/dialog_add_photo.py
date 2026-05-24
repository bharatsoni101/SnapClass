import time
from PIL import Image

import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase

@st.dialog("Capture or upload photos")
def add_photos_dialog():

    st.write('Add classroom photos to scan for attendance!')

    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'camera'

    t1,t2 = st.columns(2)

    with t1:
        type_carema = "primary" if st.session_state.photo_tab == 'camera' else 'tertiary'
        if st.button('Camera', type=type_carema, width="stretch", icon=":material/photo_camera:"):
            st.session_state.photo_tab = 'camera'

    with t2:
        type_upload = "primary" if st.session_state.photo_tab == 'upload' else 'tertiary'
        if st.button('Upload ', type=type_upload, width="stretch", icon=":material/file_upload:"):
            st.session_state.photo_tab = 'upload'

    if st.session_state.photo_tab == 'camera':
        cam_photo = st.camera_input('Take Snapshot', key='camera_input')
        if cam_photo:
            st.session_state.attendance_images.append(Image.open(cam_photo))
            st.toast('Photo added from camera!')
            st.rerun()

    if st.session_state.photo_tab == 'upload':
        upload_files = st.file_uploader('Choose image file' , type=['jpg', 'jpeg', 'png'], accept_multiple_files=True, key='upload_input')
        if upload_files:
            for f in upload_files:
                st.session_state.attendance_images.append(Image.open(f))
            st.toast('Photo uploaded successfully!')
            st.rerun()
    st.divider()

    if st.button('Done', type='primary', width='stretch'):
        st.rerun()






