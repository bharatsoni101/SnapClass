import streamlit as st


def footer_home():

    logo_url = "https://i.ibb.co/4r5X1FY/appnacollage.png"

    st.markdown(f""" 
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; items-align:center" >
            <p style="font-weight:bold; color: white; ">Created with ❤️ by </p>
            <p style="font-weight:bold; color: white; ">BHARAT SONI</p>
            <!--<img src='{{ url_for('img', filename='/bharatsoni_logo.png') }}' style='height: 25px;' ></img>-->
        </div>
    
    """, unsafe_allow_html=True)


def footer_dashboard():

    logo_url = "https://i.ibb.co/4r5X1FY/appnacollage.png"

    st.markdown(f""" 
        <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; items-align:center" >
            <p style="font-weight:bold; color: black; ">Created with ❤️ by </p>
            <p style="font-weight:bold; color: black; ">BHARAT SONI</p>
            <!--<img src='{{ url_for('img', filename='/bharatsoni_logo.png') }}' style='height: 25px;' ></img>-->
        </div>
    
    """, unsafe_allow_html=True)