# filepath: /c:/Users/Shaik Pharvej/Gemini Landmark/st.experimental_singleton.py
import streamlit as st
import google.generativeai as genai
import openai

@st.cache_resource
def configure_gemini():
    try:
        api_key = st.secrets.get("gemini_api_key")
        if not api_key:
            raise ValueError("API key for Gemini is not set in Streamlit secrets.")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5')
    except Exception as e:
        st.error(f"Error configuring Gemini API: {str(e)}")
        return None
