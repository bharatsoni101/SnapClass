#from getpass import fallback_getpass
from datetime import datetime

import pandas as pd
import streamlit as st
import numpy as np
from rich.jupyter import display
from torch.fx.experimental.unification.unification_tools import groupby

from src.components.dialog_add_photo import add_photos_dialog
from src.components.dialog_attendance_results import attendance_result_dialog
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_voice_attendance import voice_attendance_dialog
from src.components.footer import footer_dashboard
from src.components.header_home import header_dashboard
from src.components.subject_card import subject_card
from src.database.db import create_teacher, teacher_login, check_teacher_exists, get_teacher_subjects, \
    get_attendance_for_teacher
from src.pipeline.face_pipeline import predict_attendance
from src.screens.student_screen import student_dashboard
from src.ui.base_layout import base_layout_dashboard, style_base_layout
from src.database.config import supabase

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
    teacher_id = st.session_state.teacher_data['teacher_id']

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.write('You have not created any subjects yet. Please create one to begin!')
        return

    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3,1], vertical_alignment="bottom")
    with col1:
        selected_subject = st.selectbox("Select Subject", options=list(subject_options.keys()))

    with col2:
        if st.button("Add Photos", type="primary",icon=":material/photo_prints:" , width="stretch"):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject]

    st.divider

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button('Clear all photos', type='tertiary', width='stretch', icon=":material/delete:", disabled=not has_photos, key='clear_photos_btn'):
            st.session_state.attendance_images = []
            st.rerun()
    with c2:

        if st.button('Run face Analysis', type='secondary', width='stretch', icon=":material/thumb_up:", disabled=not has_photos, key='run_analysis_btn'):
            all_detected_ids = {}

            for idx, img in enumerate(st.session_state.attendance_images):
                img_np = np.array(img.convert('RGB'))

                detected, _, _ = predict_attendance(img_np)

                if detected:
                    for sid in detected.keys():
                        student_id = int(sid)

                        all_detected_ids.setdefault(student_id, []).append(f"photo {idx+1}")

            enrolled_res = supabase.table('subject_students').select('*, students(*)').eq('subject_id', selected_subject_id).execute()
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning('No student are enrolled in this course')
            else:
                results, attendance_to_log = [], []
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for node in enrolled_students:
                    student = node['students']
                    sources = all_detected_ids.get(int(student_id), [])
                    is_present = len(sources) > 0

                    results.append({
                        "Name": student['name'],
                        "ID": student['student_id'],
                        "Source": ", ".join(sources) if is_present else "-",
                        "status": " ✅ Present" if is_present else " ❌ Absent"
                    })

                    attendance_to_log.append({
                        "student_id": student['student_id'],
                        "subject_id": selected_subject_id,
                        "timestamp": current_timestamp,
                        "is_present": bool(is_present)
                    })

                attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance', type='secondary', width='stretch', icon=":material/mic:", key='voice_attendance_btn'):
            #st.write("Use Voice Attendance")
            voice_attendance_dialog(selected_subject_id)


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
    st.header('Attendance Records')

    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        return

    data = []

    for r in records:
        ts = r.get('timestamp')

        data.append({
            "ts_group": ts.split(".")[0] if ts else None,
            "Time": datetime.fromisoformat(ts).strftime("%Y-%m-%d %I:%M %p") if ts else "N'A",
            "Subject": r['subjects']['name'],
            "Subject Code":r['subjects']['subject_code'],
            "is_present": bool(r.get('is_present', False))
        })


    df = pd.DataFrame(data)



    summary = (
        df.groupby(['ts_group', 'Time', 'Subject', 'Subject Code'])
        .agg(
            Present_Count = ('is_present', 'sum'),
            Total_Count =('is_present', 'count')
        ).reset_index()

    )

    summary['Attendance Stats'] = (
            "✅ " + summary['Present_Count'].astype(str) + " /"
            + summary['Total_Count'].astype(str) + ' Students'
    )

    display_df = ( summary.sort_values(by='ts_group' ,ascending=False)
    [['Time', 'Subject', 'Subject Code', 'Attendance Stats']]
    )

    st.dataframe(display_df, width='stretch', hide_index=True)



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
                st.toast(f"Login successful! {teacher_username} Welcome back.")
                import time
                time.sleep(1)
                st.rerun()
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