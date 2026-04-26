import streamlit as st


def footer_home():

    logo_url = "https://i.ibb.co/4r5X1FY/appnacollage.png"

    st.markdown(f""" 
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; items-align:center" >
            <p style="font-weight:bold; color: white; ">Created with ❤️ by </p>
            <img src='{logo_url}' style='height: 25px;' ></img>
        </div>
    
    """, unsafe_allow_html=True)
