import streamlit as st
import threading, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import database as db  # Your database module

st.set_page_config(page_title="Automation", page_icon="🔥", layout="wide")

# ---------------- CSS & STYLING ----------------
st.markdown("""
<style>

/* ======== GLOBAL iOS BACKGROUND ======== */
.stApp {
    background: linear-gradient(145deg, #e3edf7, #ffffff);
    background-attachment: fixed;
}

/* Soft noise overlay */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background: url("https://www.transparenttextures.com/patterns/white-diamond.png");
    opacity: 0.15;
    z-index: 0;
}


/* ======== iOS GLASS CARD ======== */
.stCard {
    backdrop-filter: blur(20px);
    background: rgba(255,255,255,0.55) !important;
    border-radius: 22px !important;
    padding: 22px !important;
    border: 1px solid rgba(255,255,255,0.45) !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    transition: 0.25s ease-in-out;
}
.stCard:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 35px rgba(0,0,0,0.12);
}


/* ======== iOS TITLE ======== */
.title {
    font-family: "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 3.1rem;
    font-weight: 800;
    letter-spacing: -1px;
    margin-bottom: 10px;
    text-align: center;
    background: linear-gradient(120deg, #007aff, #5856d6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}


/* ======== APPLE LOGO STYLE ======== */
.logo {
    width: 140px;
    height: 140px;
    border-radius: 30px;
    display: block;
    margin: auto;
    padding: 10px;
    background: rgba(255,255,255,0.55);
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
    backdrop-filter: blur(25px);
}


/* ======== INPUTS (iOS Rounded Inputs) ======== */
input, textarea {
    background: rgba(255,255,255,0.75) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(0,0,0,0.15) !important;
    padding: 12px !important;
    font-size: 15px;
    color: #333 !important;
    font-family: "SF Pro Text";
    transition: 0.2s;
}
input:focus, textarea:focus {
    border-color: #007aff !important;
    box-shadow: 0 0 0 3px rgba(0,122,255,0.25);
}


/* ======== iOS BUTTONS ======== */
.stButton>button {
    background: linear-gradient(135deg,#007aff,#5856d6) !important;
    color: white !important;
    border: none !important;
    padding: 12px 30px !important;
    font-size: 16px !important;
    border-radius: 14px !important;
    font-family: "SF Pro Text", sans-serif;
    font-weight: 600 !important;
    transition: 0.2s;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
}
.stButton>button:hover {
    filter: brightness(1.05);
    box-shadow: 0px 10px 25px rgba(0,0,0,0.18);
    transform: translateY(-1px);
}


/* ======== LIVE LOGS CONSOLE ======== */
.console-box {
    background: rgba(255,255,255,0.65);
    backdrop-filter: blur(18px);
    border-radius: 20px;
    padding: 20px;
    height: 330px;
    overflow-y: auto;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.05), 
                0 10px 30px rgba(0,0,0,0.10);
    font-family: "SF Mono", monospace;
    color: #444;
    font-size: 14px;
    border: 1px solid rgba(0,0,0,0.15);
}


/* ======== iOS TAB FIX ======== */
.css-1y4p8pa, .css-13sdm1h {
    background: rgba(255,255,255,0.60) !important;
    backdrop-filter: blur(18px);
    border-radius: 14px;
    border: 1px solid rgba(0,0,0,0.1);
}

/* Remove default Streamlit borders */
.block-container {
    padding-top: 1rem;
}

</style>

<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">

<!-- Apple Style Rounded Logo -->
<img class="logo" src="https://i.ibb.co/m5G9GdXx/logo.png">

""", unsafe_allow_html=True)
