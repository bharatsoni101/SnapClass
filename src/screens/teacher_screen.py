#from getpass import fallback_getpass

import streamlit as st

from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.footer import footer_dashboard
from src.components.header_home import header_dashboard
from src.components.subject_card import subject_card
from src.database.db import create_teacher, teacher_login, check_teacher_exists, get_teacher_subjects
from src.ui.base_layout import base_layout_dashboard, style_base_layout

def teacher_screen():
    base_layout_dashboard()
    style_base_layout()

    if 'teacher_data' in st.session_state:
        teacher_screen_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=='login':
        teacher_screen_login()
    elif st.session_state.teacher_login_type=='register':
        teacher_screen_register()

def teacher_screen_dashboard():
    teacher_data = st.session_state.teacher_data
    c1,c2 = st.columns(2, vertical_alignment='center', gap='large')

    with c1:
        header_dashboard()

    with c2:
        st.subheader(f"""Welcome, {teacher_data['name']}!""")
        if st.button("Logout", type="secondary", key="loginbackbtn"):
            st.session_state["login_type"] = None
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()
    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'


    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else 'tertiary'
        if st.button("Take Attendance", type = type1, width="stretch",icon=":material/ar_on_you:"):
            st.session_state.current_teacher_tab = "take_attendance"
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else 'tertiary'
        if st.button('Manage Subjects', type = type2, width='stretch', icon=":material/book_ribbon:"):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else 'tertiary'
        if st.button('Attendance Records', type = type3, width='stretch', icon=":material/cards_stack:"):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    if st.session_state.current_teacher_tab == 'take_attendance':
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == 'manage_subjects':
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == 'attendance_records':
        teacher_tab_attendance_records()


    footer_dashboard()

def teacher_tab_take_attendance():
    st.header('Take AI attendance here')

def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subject', width="stretch")
    with col2:
        if st.button('Create New Subject', width="stretch"):
            create_subject_dialog(teacher_id)

    #list all subjects:
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("👥", "Students", sub['total_students']),
                ("🕒", "Classes", sub['total_classes']),
            ]
        def share_btn():
            if st.button(f"Share Code: {sub['name']}", key=f"share_{sub['subject_code']}", icon=":material/share:"):
                share_subject_dialog(sub['name'], sub['subject_code'])
            st.space()

        subject_card(
            name = sub['name'],
            code = sub['subject_code'],
            section = sub['section'],
            stats= stats,
            footer_callback = share_btn
        )
    else:
        st.info("NO SUBJECT FOUND, CREATE ONE ABOVE!")


def teacher_tab_attendance_records():
    st.header('Attendance records here')




def login_teacher(teacher_username, teacher_password):
    if not teacher_username or not teacher_password:
        return False
    teacher =  teacher_login(teacher_username, teacher_password)

    if teacher:
        st.session_state.teacher_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logined_in = True
        return True
    return False

def teacher_screen_login():

    c1,c2 = st.columns(2, vertical_alignment='center', gap='large')

    with c1:
        header_dashboard()

    with c2:
        if st.button("Go back to home", type="secondary", key="loginbackbtn"):
            st.session_state["login_type"] = None
            st.rerun()

    st.header('Login using password')

    teacher_username = st.text_input("Enter Username", placeholder="Enter Username")
    teacher_password = st.text_input("Enter Password", type="password", placeholder="Enter Password")

    st.divider()

    btn1, btn2 = st.columns(2)

    with btn1:
        if st.button("Login", icon=":material/passkey:", key="teacherloginbtn", width="stretch"):
            if login_teacher(teacher_username, teacher_password):
                st.toast("Login successful! Welcome back.")
                import time
                time.sleep(1)
                st.rerun
                # You can set session state here to indicate that the teacher is logged in
            else:
                st.error("Invalid username or password. Please try again.")

    with btn2:
        if st.button("Register Instead", type="primary", icon=":material/passkey:", key="teacherregisterbtn", width="stretch"):
            st.session_state.teacher_login_type = 'register'
            st.rerun()

    footer_dashboard()

def register_teacher(teacher_username, teacher_password, teacher_confirm, teacher_name):
    if not teacher_username or not teacher_password or not teacher_name:
        return False, "Please fill in all the fields."
    if check_teacher_exists(teacher_username):
        return False, "Username Already taken"
    if teacher_password != teacher_confirm:
        st.error("Passwords do not match. Please try again.")
        return False, "Passwords do not match"
    try:
        create_teacher(teacher_username, teacher_password, teacher_name)
        return True, "Teacher registered successfully! Please"
    except Exception as e:
        return False, f"An error occurred during registration: {str(e)}"



def teacher_screen_register():
    c1,c2 = st.columns(2, vertical_alignment='center', gap='large')

    with c1:
        header_dashboard()

    with c2:
        if st.button("Go back to home", type="secondary", key="loginbackbtn"):
            st.session_state["login_type"] = None
            st.rerun()


    st.header('Register your teacher profile')

    teacher_username = st.text_input("Enter Username", placeholder="Enter Username")
    teacher_name = st.text_input("Enter Name", placeholder="Enter Name")
    teacher_password = st.text_input("Enter Password", type="password", placeholder="Enter Password")
    teacher_confirm = st.text_input("Confirm Password", type="password", placeholder="Enter Password")


    st.divider()

    btn1, btn2 = st.columns(2)

    with btn1:
        if st.button("Register Now", type="primary", icon=":material/passkey:", key="teacherregisterbtn", width="stretch"):
            success, message = register_teacher(teacher_username,teacher_password,teacher_confirm, teacher_name)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = 'login'
                st.rerun()
            else:
                st.error(message)

    with btn2:
        if st.button("Login Instead", icon=":material/passkey:", key="teacherloginbtn", width="stretch"):
            st.session_state.teacher_login_type = 'login'
            st.rerun()

    footer_dashboard()