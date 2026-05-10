import streamlit as st

def subject_card(name, code, section, stats, footer_callback=None):

    st.markdown(f"""
        <div id="main1" style="border: 1px solid #ccc; border-radius: 8px; padding: 16px; margin-bottom: 16px; background-color: #f9f9f9;">
            <h3 style="margin: 0 0 8px 0;">{name}</h3>
            <p style="margin: 0 0 8px 0; color: #555;">Code: {code} | Section: {section}</p>
            <div style="display: flex; gap: 16px; margin-top:   16px;">
    """, unsafe_allow_html=True)
    if stats:
        for icon, label, value in stats:
            st.markdown(f"""
                <div id="stats2" style="display: flex; align-items: center; gap: 4px;">
                    <span style="font-size: 20px;">{icon}</span>
                    <span style="color: #555;">{label}: {value}</span>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

    if footer_callback:
        footer_callback()

