import time
from idlelib.rpc import response_queue

import numpy as np
import streamlit as st

from src.components.footer import footer_dashboard
from src.components.header_home import header_dashboard
from src.database.db import get_all_students, create_student
from src.pipeline.voice_pipeline import get_voice_embedding
from src.ui.base_layout import base_layout_dashboard, style_base_layout
from PIL import Image
import numpy as np
from src.pipeline.face_pipeline import predict_attendance, get_face_embeddings, train_classifier
import time

def student_dashboard() :
    st.header("Student Dashboard here")
    student_data = st.session_state.student_data

    st.header(f"Welcome, {student_data['name']}!")

    st.subheader("Your Attendance Records")
    attendance_records = student_data.get("attendance_records", [])
    if attendance_records:
        for record in attendance_records:
            st.write(f"Date: {record['date']}, Status: {record['status']}")
    else:
        st.write("No attendance records found.")

def student_screen():
    base_layout_dashboard()
    style_base_layout()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    c1,c2 = st.columns(2, vertical_alignment='center', gap='large')

    with c1:
        header_dashboard()

    with c2:
        if st.button("Go back to home", type="secondary", key="loginbackbtn"):
            st.session_state["login_type"] = None
            st.rerun()

    #st.header('Login using password')

    st.header('Login using faceID')

    show_registration = False

    photo_source = st.camera_input("Position your face in the camera and click the button to login", key="student_camera_input")
    if photo_source:
        img = np.array(Image.open(photo_source))

        with st.spinner('AI is scanning...'):
            detected, all_ids, num_faces = predict_attendance(img)

            if num_faces == 0:
                st.warning('Face not detected. Please try again.')
            elif num_faces>1 :
                st.warning('Multiple faces found.')
            else:
                if detected:
                    #student_id = list(detected().keys())[0]
                    student_id = next(iter(detected))
                    all_students = get_all_students()
                    student = next((s for s in all_students if s['student_id'] == student_id), None)

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f'Welcome, {student["name"]}!')
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info('Face not recognized! you might be new Student!')
                    show_registration = True
    if show_registration:
        with st.container(border=True):
            st.header('Register now profile')
            new_name = st.text_input('Enter your name', placeholder='E.g. John Doe')

            st.subheader('Optional : voice enrollment')
            st.info("Enroll your voice only attendance")

            audio_data = None

            try:
                audio_data = st.audio_input("Record a short phrase like I am present, My name is Akash. ")
            except Exception as e:
                st.error ('Audio data failed!')

            if st.button('Create Account', type='primary'):
                if new_name:
                    with st.spinner('Creating profile...'):
                        img = np.array(Image.open(photo_source))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()  # Convert numpy array to list for JSON serialization

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())
                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                st.toast(f'Profile created! Hi, {new_name}!')
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Could not capture your facial feature for registration. Please try again.')
                else:
                    st.error('Please enter your name to create an account.')




    footer_dashboard()

