import streamlit as st
import google.generativeai as genai
import wikipediaapi

def configure_gemini():
    """Initialize and configure Gemini API."""
    try:
        api_key = st.secrets["AIzaSyAxFUkU6Rp_GmiEPgHnKjLV1hPVKfh0k3A"]  # Ensure this matches secrets.toml
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-1.5')
    except KeyError:
        st.error("❌ API Key not found! Please check `secrets.toml` file.")
        return None
    #except Exception as e:
        #st.error(f"⚠️ Error configuring Gemini API: {str(e)}")
       # return None

def get_wikipedia_info(landmark_name):
    """Fetch summary and URL of a landmark from Wikipedia."""
    try:
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page = wiki_wiki.page(landmark_name)

        if page.exists():
            return {
                'summary': page.summary[:1000],  # Limit summary to 1000 characters
                'url': page.fullurl
            }
        else:
            return None  # Landmark not found on Wikipedia

    except Exception as e:
        return f"⚠️ Error fetching Wikipedia information: {str(e)}"
