import streamlit as st

from src.components.header_home import header_home
from src.ui.base_layout import base_layout_home, style_base_layout

def home_screen():
    st.header("Home Screen")

    header_home()
    base_layout_home()
    style_base_layout()

    col1, col2 = st.columns(2, gap='large')
    with col1:
        if st.button('Login as Teacher', type='primary', key='teacher_btn', width='stretch'):
            st.session_state['login_type'] = 'teacher'
            st.rerun()
    with col2:
        if st.button('Login as Student', type='primary', key='student_btn', width='stretch'):
            st.session_state['login_type'] = 'student'
            st.rerun()