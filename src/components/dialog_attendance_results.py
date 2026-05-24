import time
from PIL import Image

import streamlit as st
from sklearn.utils import column_or_1d

from src.database.db import create_attendance
from src.database.config import supabase

def show_attendance_result(df, logs):
    st.write('Please review the attendance before submitting!')
    st.dataframe(df, hide_index=True, width="stretch")

    col1 , col2 = st.columns(2)

    with col1:
        if st.button('Discard', type='tertiary', width="stretch"):
            st.session_state.voice_attendance_results = None
            st.session_state.attendance_images = []
            st.rerun()
    with col2:
        if st.button('Confirm & Save', type='primary', width="stretch"):
            try:
                create_attendance(logs)
                st.toast("Attendace saved successfully!")
                st.session_state.attendance_images = []
                st.session_state.voice_attendance_results = None
                st.rerun()
            except Exception as e:
                st.error(f"Failed to save attendance: {str(e)}")
                st.rerun()


@st.dialog("Attendance Reports")
def attendance_result_dialog(df, logs):
    show_attendance_result(df, logs)







