"""To run:
streamlit run --server.enableCORS=false --server.enableXsrfProtection=false --server.enableWebsocketCompression=false streamlit_app.py
"""

import streamlit as st
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import os
from dotenv import load_dotenv, find_dotenv

from textwrap import dedent
from langchain_community.chat_models import ChatOpenAI
from utils import extract_and_parse_list_of_dicts, generate_image_from_prompts, convert_image, generate_image_mask, display_mask_with_image
from  archi_tasks import task1, task2, task3, task4, generate_task_with_brief
from archi_crew import ArchitectureDesignCrew

# Env set up
BASEDIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASEDIR, '.env.example'))

llm = ChatOpenAI(model_name="gpt-4-0125-preview")

# Streamlit UI
st.title("Design concept generator")

# User Inputs
uploaded_image = st.sidebar.file_uploader("Upload the site image:", type=["jpg", "jpeg"])
uploaded_mask = st.sidebar.file_uploader("Upload the mask image:", type=["jpg", "jpeg"])
design_brief = st.sidebar.text_area("Enter the architecture brief:")
num_concepts = st.sidebar.number_input("Number of concepts to generate", min_value=1, max_value=15, value=5)
num_images = st.sidebar.number_input("Number of images per concept", min_value=1, max_value=15, value=5)

# image display
if uploaded_image and uploaded_mask:
    image = Image.open(uploaded_image)
    mask = Image.open(uploaded_mask)
    st.image(display_mask_with_image(image, mask), caption="The site", use_column_width=True)

if st.sidebar.button("Submit"):
    with st.spinner("Generating design concepts..."):

        uploaded_image = Image.open(uploaded_image)
        uploaded_mask = Image.open(uploaded_mask)
        
        print(type(uploaded_image))
        print(uploaded_image.size)
        print(type(uploaded_mask))
        print(uploaded_mask.size)
        
        tasks = [generate_task_with_brief(task1, design_brief), task2, generate_task_with_brief(task3, design_brief), task4]
        design_crew = ArchitectureDesignCrew(tasks, llm)
        result = design_crew.run(num_concepts=num_concepts)
        parsed_list_of_dicts = extract_and_parse_list_of_dicts(result)[0]

        # Make num_images an input field
        output_path = "generated_images/"
        # model = "diffusers/stable-diffusion-xl-1.0-inpainting-0.1"
        # get HF_HOME from environment variable and append to model
        model = os.getenv("HF_HOME") + "/diffusers/stable-diffusion-xl-1.0-inpainting-0.1"

        generate_image_from_prompts(parsed_list_of_dicts, uploaded_image, uploaded_mask, num_images, output_path, model)
        
        for subfolder in os.listdir(output_path):
            subfolder_path = os.path.join(output_path, subfolder)
            
            if os.path.isdir(subfolder_path):
                st.header(subfolder)
                
                for info in parsed_list_of_dicts:
                    if info["concept"] == subfolder:
                        st.write(f"{info['positive']}")
                
                image_paths = [os.path.join(subfolder_path, f) for f in os.listdir(subfolder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
                
                cols = st.columns(len(image_paths))
        
                for col, img_path in zip(cols, image_paths):
                    image = Image.open(img_path)
                    col.image(image, use_column_width=True)
    
    # Clean up the generated images
    for subfolder in os.listdir(output_path):
        subfolder_path = os.path.join(output_path, subfolder)
        if os.path.isdir(subfolder_path):
            for f in os.listdir(subfolder_path):
                os.remove(os.path.join(subfolder_path, f))
            os.rmdir(subfolder_path)
    