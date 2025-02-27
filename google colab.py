

# Install necessary libraries (run this cell first in Colab)
!pip install gradio transformers wikipedia-api Pillow

import gradio as gr
from transformers import pipeline
import wikipediaapi
from PIL import Image
import io

# 🔹 Configure Hugging Face Transformer Model (e.g., GPT-2 or similar)
def configure_hugging_face_model():
    try:
        # Load a text generation pipeline from Hugging Face
        model = pipeline("text-generation", model="distilgpt2")  # Lightweight GPT-2
        return model
    except Exception as e:
        return f"Error loading Hugging Face model: {str(e)}"

# 🔹 Fetch landmark description using the Hugging Face model
def get_landmark_description(image_description, model):
    try:
        # Generate text using the Hugging Face model
        generated_text = model(
            f"Analyze the following landmark description and provide:\n"
            "1. Name of the landmark\n"
            "2. Historical significance\n"
            "3. Architectural features\n"
            "4. Best time to visit\n"
            "5. Interesting facts\n\n"
            f"Description:\n{image_description}\n",
            max_length=150,
            num_return_sequences=1
        )[0]['generated_text']
        return generated_text
    except Exception as e:
        return f"🔴 Error generating landmark description: {str(e)}"

# 🔹 Fetch Wikipedia summary
def get_wikipedia_info(landmark_name):
    try:
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page = wiki_wiki.page(landmark_name)

        if page.exists():
            return {
                'summary': page.summary[:1000],  # Limit to 1000 characters
                'url': page.fullurl
            }
        return None  # No Wikipedia page found
    except Exception as e:
        return f"🔴 Error fetching Wikipedia info: {str(e)}"

# 🔹 Process and analyze the image
def process_image(image, model):
    # Convert PIL image to a placeholder description (you can use a vision model for actual analysis)
    image_description = "This is a placeholder description for the landmark image."

    # Get landmark description using Hugging Face model
    description = get_landmark_description(image_description, model)

    # Extract landmark name (assuming it's the first line of the description)
    landmark_name = description.split('\n')[0].replace("Name of the landmark:", "").strip()

    # Get Wikipedia info
    wiki_info = get_wikipedia_info(landmark_name)

    # Build the output
    result = f"🤖 **AI Analysis:**\n{description}\n\n"

    if isinstance(wiki_info, dict):
        result += f"📚 **Wikipedia Summary:**\n{wiki_info['summary']}\n\n"
        result += f"[Read more on Wikipedia]({wiki_info['url']})"
    else:
        result += "No additional information found on Wikipedia."

    return result

# 🔹 Gradio Interface for Colab
def launch_gradio_in_colab():
    # Configure the Hugging Face model
    model = configure_hugging_face_model()
    if isinstance(model, str):  # If there's an error
        print(model)
        return

    # Define Gradio interface
    with gr.Blocks() as demo:
        gr.Markdown("## 🏛 AI Landmark Explorer with Wikipedia Integration")
        gr.Markdown(
            "Upload an image of a landmark, and the AI will provide details about the landmark, including historical and architectural information."
        )

        with gr.Row():
            with gr.Column():
                image_input = gr.Image(label="Upload Image", type="pil")  # Use PIL image type
            with gr.Column():
                output_text = gr.Textbox(label="Landmark Analysis", lines=10)

        analyze_button = gr.Button("Analyze Landmark")

        # Bind button click to process_image function
        analyze_button.click(
            fn=lambda img: process_image(img, model),
            inputs=[image_input],
            outputs=[output_text]
        )

    demo.launch(share=True)

# 🔹 Launch Gradio in Colab
launch_gradio_in_colab()

# Install necessary libraries (run this cell first in Colab)
!pip install gradio transformers wikipedia-api Pillow timm

import gradio as gr
from transformers import pipeline, ViTImageProcessor, ViTForImageClassification
from transformers import AutoTokenizer, AutoModelForCausalLM
import wikipediaapi
from PIL import Image
import torch

# 🔹 Load Hugging Face Image Recognition Model
def load_image_model():
    processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
    model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")
    return processor, model

# 🔹 Load Hugging Face Text Generation Model
def load_text_generation_model():
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    return tokenizer, model

# 🔹 Get Landmark Description Using Image Model
def analyze_image(image, processor, model):
    try:
        inputs = processor(images=image, return_tensors="pt")
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
        label = model.config.id2label[predicted_class_idx]
        return label  # Return the predicted label (landmark name or object type)
    except Exception as e:
        return f"Error in image analysis: {str(e)}"

# 🔹 Generate Landmark Description Using GPT-2
def generate_description(landmark_name, tokenizer, text_model):
    try:
        prompt = (
            f"Provide a detailed description for the following landmark:\n"
            f"{landmark_name}\n\n"
            "Include the following:\n"
            "1. Historical significance\n"
            "2. Architectural features\n"
            "3. Best time to visit\n"
            "4. Interesting facts\n\n"
        )
        inputs = tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = text_model.generate(inputs, max_length=300, num_return_sequences=1, no_repeat_ngram_size=2)
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text
    except Exception as e:
        return f"Error in text generation: {str(e)}"

# 🔹 Fetch Wikipedia Summary
def get_wikipedia_info(landmark_name):
    try:
        wiki_wiki = wikipediaapi.Wikipedia('en')
        page = wiki_wiki.page(landmark_name)

        if page.exists():
            return {
                'summary': page.summary[:1000],  # Limit to 1000 characters
                'url': page.fullurl
            }
        return None  # No Wikipedia page found
    except Exception as e:
        return f"🔴 Error fetching Wikipedia info: {str(e)}"

# 🔹 Process the Image and Generate Output
def process_image(image, processor, image_model, tokenizer, text_model):
    # Step 1: Use the image model to analyze the image
    landmark_name = analyze_image(image, processor, image_model)

    # Step 2: Use the text generation model to generate detailed landmark description
    detailed_description = generate_description(landmark_name, tokenizer, text_model)

    # Step 3: Fetch Wikipedia information
    wiki_info = get_wikipedia_info(landmark_name)

    # Step 4: Combine the results into output
    result = f"**Predicted Landmark:** {landmark_name}\n\n"
    result += f"**AI-Generated Description:**\n{detailed_description}\n\n"

    if isinstance(wiki_info, dict):
        result += f"**Wikipedia Summary:**\n{wiki_info['summary']}\n\n"
        result += f"[Read more on Wikipedia]({wiki_info['url']})"
    else:
        result += "No additional information found on Wikipedia."

    return result

# 🔹 Gradio Interface
def launch_gradio():
    # Load models
    processor, image_model = load_image_model()
    tokenizer, text_model = load_text_generation_model()

    # Define Gradio interface
    with gr.Blocks() as demo:
        gr.Markdown("## 🏛 AI Landmark Explorer with Hugging Face and Wikipedia Integration")
        gr.Markdown(
            "Upload an image of a landmark, and the AI will predict the landmark name, generate detailed descriptions, and fetch additional information from Wikipedia."
        )

        with gr.Row():
            with gr.Column():
                image_input = gr.Image(label="Upload Image", type="pil")  # Use PIL image type
            with gr.Column():
                output_text = gr.Textbox(label="Landmark Analysis", lines=15)

        analyze_button = gr.Button("Analyze Landmark")

        # Bind button click to process_image function
        analyze_button.click(
            fn=lambda img: process_image(img, processor, image_model, tokenizer, text_model),
            inputs=[image_input],
            outputs=[output_text]
        )

    demo.launch(share=True)

# 🔹 Launch Gradio App in Colab
launch_gradio()
