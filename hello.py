import streamlit as st
import google.generativeai as genai
import wikipediaapi
from utils import configure_gemini, get_wikipedia_info
from PIL import Image
from datetime import datetime
import io

# 🔹 Configure Gemini AI
import streamlit as st
import google.generativeai as genai

import openai
import streamlit as st
import base64

# Load OpenAI API Key
openai.api_key = "your_openai_api_key"  # Or use secrets

def get_landmark_description(image_file):
    # Convert image to base64
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",  # GPT-4 Vision Model
        messages=[
            {"role": "system", "content": "You are a helpful AI that describes landmarks."},
            {"role": "user", "content": [
                {"type": "text", "text": "Describe the landmark in this image."},
                {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_data}"}
            ]}
        ],
        max_tokens=300
    )

    return response["choices"][0]["message"]["content"]

st.title("🏛 AI Landmark Explorer")
uploaded_file = st.file_uploader("Upload a Landmark Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    
    with st.spinner("Analyzing landmark..."):
        description = get_landmark_description(uploaded_file)
    
    st.subheader("📝 Landmark Description:")
    st.write(description)


"""def configure_gemini():
    try:
        api_key = st.secrets#["AIzaSyBz8gamex4PivYRLIPk1AYbVnlIvRflS3I"]  # Ensure this matches the key in secrets.toml
        genai.configure(api_key=api_key)
        return genai.GenerativeModel('gemini-pro-vision')
    except Exception as e:
        st.error(f"Error configuring Gemini API: {str(e)}")
        return None """


# 🔹 Get AI-generated landmark description
def get_landmark_description(model, image):
    try:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes = img_bytes.getvalue()

        response = model.generate_content([
            "Analyze this image and provide:\n"
            "1. Name of the landmark\n"
            "2. Historical significance\n"
            "3. Architectural features\n"
            "4. Best time to visit\n"
            "5. Interesting facts\n"
            "Respond in a structured format.",
            img_bytes
        ])
        return response.text if response else "No response from AI."
    except Exception as e:
        return f"🔴 Error analyzing image: {str(e)}" 
        

# 🔹 Fetch Wikipedia summary
def get_wikipedia_info(landmark_name):
    try:
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page = wiki_wiki.page(landmark_name)

        if page.exists():
            return {
                'summary': page.summary[:1000],  # Limit to 1000 chars
                'url': page.fullurl
            }
        return None  # No Wikipedia page found
    except Exception as e:
        return f"🔴 Error fetching Wikipedia info: {str(e)}"

# 🔹 Process and display image analysis
def process_image(image_file, model):
    # Load and show image
    image = Image.open(image_file)
    st.image(image, caption="📍 Landmark Image", use_container_width=True)

    with st.spinner("🔍 Analyzing landmark..."):
        description = get_landmark_description(model, image)

        # Extract landmark name (assuming it's the first line)
        landmark_name = description.split('\n')[0].replace("Name of the landmark:", "").strip()

        # Get Wikipedia info
        wiki_info = get_wikipedia_info(landmark_name)

        # UI Layout
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("🤖 AI Analysis")
            st.write(description)

            if isinstance(wiki_info, dict):
                st.subheader("📚 More Info")
                st.write(wiki_info['summary'])
                st.markdown(f"[Read more on Wikipedia]({wiki_info['url']})")

        with col2:
            st.subheader("📍 Quick Tips")
            st.info("""
            - 📸 Best photo spots
            - ⏰ Opening hours
            - 🎫 Ticket information
            - 🚶‍♂ Guided tours
            """)

            # Downloadable Report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report = f"""
            Landmark Analysis Report
            Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            
            {description}
            
            Additional Information:
            {wiki_info['summary'] if isinstance(wiki_info, dict) else 'No Wikipedia info available'}
            """
            
            st.download_button(
                label="📥 Download Report",
                data=report,
                file_name=f"landmark_report_{timestamp}.txt",
                mime="text/plain"
            )

# 🔹 Main Streamlit App
def main():
    st.set_page_config(
        page_title="AI Landmark Explorer",
        page_icon="🏛",
        layout="wide"
    )

    st.title("🏛 AI Landmark Explorer")
    st.write("Upload or capture an image to get details about famous landmarks!")

    # Load AI model
    model = configure_gemini()
    if not model:
        st.error("🔴 AI model initialization failed. Check API key.")
        return

    # Tabs for input
    tab1, tab2 = st.tabs(["📸 Camera Capture", "🖼 Upload Image"])

    with tab1:
        st.header("Take a Photo")
        camera_photo = st.camera_input("Capture landmark")
        if camera_photo:
            process_image(camera_photo, model)

    with tab2:
        st.header("Upload an Image")
        uploaded_file = st.file_uploader("Choose an image...", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            process_image(uploaded_file, model)

if __name__ == "__main__":
    main()