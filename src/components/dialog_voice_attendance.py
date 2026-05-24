from tokenize import detect_encoding

import pandas as pd
import streamlit as st

from src.components.dialog_attendance_results import show_attendance_result
from src.database.db import create_attendance
import streamlit as st
from src.pipeline.voice_pipeline import process_bulk_audio
from src.database.config import supabase
from datetime import datetime

@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):
    st.write('Record audio of students saying I am present, than AI will recognize the student!')

    audio_data = None

    audio_data =  st.audio_input("Record Attendance", key="audio_input")

    if st.button("Analyze Audio", type="primary", width="stretch"):
        with st.spinner("Processing audio data..."):
            enrolled_res = supabase.table('subject_students').select('*, students(*)').eq('subject_id', selected_subject_id).execute()
            enrolled_students = enrolled_res.data

            if not enrolled_students:
                st.warning("No students enrolled in this subject.")
                return
            candidate_dict = {
                s['students']['student_id']: s['students']['voice_embedding']
                for s in enrolled_students if s['students'].get('voice_embedding')
            }

            if not candidate_dict:
                st.error('No enrolled students have voice profile registerd.')

            detected_scores = process_bulk_audio(audio_data, candidate_dict)

            results, attendance_to_log = [], []

            current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for node in enrolled_students:
                student = node['students']
                score = detected_scores.get(student['student_id'], 0.0)
                is_present = bool( score>0 )

                results.append({
                    "Name": student['name'],
                    "ID": student['student_id'],
                    "Source": score if is_present else "-",
                    "status": " ✅ Present" if is_present else " ❌ Absent"
                })

                attendance_to_log.append({
                    "student_id": student['student_id'],
                    "subject_id": selected_subject_id,
                    "timestamp": current_timestamp,
                    "is_present": bool(is_present)
                })
            st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)

    if st.session_state.get("voice_attendance_results"):
        st.divider()
        df_results, logs = st.session_state.voice_attendance_results
        show_attendance_result(df_results, logs)






