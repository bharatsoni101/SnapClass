import streamlit as st
from torch.nn.functional import scaled_mm

from src.database.db import create_subject
import segno
import io


@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):
    app_domain = "snapclass-bharat.streamlit.app"
    join_url = f"{app_domain}/join?join-code={subject_code}"

    st.header("Scan to join")
    qr = segno.make(join_url)

    out = io.BytesIO()

    qr.save(out, kind='png', scale=10, border=1)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('### Copy Link')
        st.code(join_url, language='text')
        st.code(subject_code, language='text')
        st.info("Copy this link to share on whatsapp or Email")
    with col2:
        st.markdown('### Scan to join')
        st.image(out.getvalue(), width="stretch" , caption='QRCODE for class joining')
