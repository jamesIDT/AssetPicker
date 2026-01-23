"""Crypto RSI Screener - Main Streamlit application."""

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Crypto RSI Screener",
    layout="wide"
)

# Main UI
st.title("Crypto RSI Screener")

st.write("Chart and analysis will appear here.")

st.button("Refresh Data", disabled=True)

st.text("Last updated: Not yet refreshed")
