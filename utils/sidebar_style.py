# utils/sidebar_style.py
import streamlit as st
import os
import base64

def apply_sidebar_style():
    st.markdown("""
    <style>
    /* Sidebar completo */
    [data-testid="stSidebar"] {
        background-color: #cce6ff !important;
        color: #000 !important;
        padding-top: 10px !important;
    }

    [data-testid="stSidebarContent"] {
        padding-top: 10px !important;
        color: #000 !important;
    }

    [data-testid="stSidebarContent"] h2,
    [data-testid="stSidebarContent"] h3,
    [data-testid="stSidebarContent"] h4 {
        margin-top: 0 !important;
        padding-top: 0 !important;
        color: #000 !important;
    }

    [data-testid="stSidebar"] .stSelectbox {
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }

    /* Hack multi-page menu */
    .css-18e3th9, .css-1d391kg {
        background-color: #cce6ff !important;
        color: #000 !important;
    }

    .css-18e3th9 a, .css-1d391kg a {
        color: #000 !important;
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

    # Logo arriba
    logo_path = "assets/logo.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_bytes = f.read()
            logo_b64 = base64.b64encode(logo_bytes).decode()
        st.sidebar.markdown(
            f'<div style="text-align:center; margin-bottom:15px;">'
            f'<img src="data:image/png;base64,{logo_b64}" style="width:70%;"/>'
            f'</div>',
            unsafe_allow_html=True
        )
