import streamlit as st

from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.home_screen import home_screen

def main():
    if 'login_type' not in st.session_state:
        st.session_state['login_type'] = None

    match st.session_state['login_type']:
        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
        case None:
            home_screen()


main()




# def main():
#     st.header("This is title!")
#
#     name = st.text_input('Enter name:')
#
#     col1, col2 = st.columns(2, gap='large')
#
#     with col1 :
#         if st.button('Hi', type='primary', key='btn1', width='stretch'):
#             st.write(f'Hello, {name}!')
#
#     with col2 :
#         if st.button('Bye', type='primary', key='btn2', width='stretch'):
#             st.write(f'Hello, {name}!')
#
#     st.markdown("""
#         <style>
#             button {
#                 background-color: #orange !important;
#             }
#         </style>
#     """, unsafe_allow_html=True)

