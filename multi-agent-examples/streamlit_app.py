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
num_images = st.sidebar.number_input("Number of images per idea", min_value=1, max_value=15, value=5)

# Display the overlay of the mask on the image
if uploaded_image and uploaded_mask:
    image = Image.open(uploaded_image)
    mask = Image.open(uploaded_mask)
    st.image(display_mask_with_image(image, mask), caption="The site", use_column_width=True)

if st.sidebar.button("Submit"):
    # Display loading while the images are being processed
    with st.spinner("Generating design concepts..."):

        # Convert image and mask to PIL image
        uploaded_image = Image.open(uploaded_image)
        uploaded_mask = Image.open(uploaded_mask)
        # Save the mask and image
        print(type(uploaded_image))
        print(uploaded_image.size)
        print(type(uploaded_mask))
        print(uploaded_mask.size)
        
        tasks = [generate_task_with_brief(task1, design_brief), task2, generate_task_with_brief(task3, design_brief), task4]
        design_crew = ArchitectureDesignCrew(tasks, llm)
        result = design_crew.run()
        parsed_list_of_dicts = extract_and_parse_list_of_dicts(result)[0]

        # text = """Some unneeded text before [
        # {"concept": "The Green Nexus", "positive": "A multi-level garden community center with seamless integration of indoor and outdoor spaces, utilizing solar panels and rainwater harvesting", "negative": "A concrete structure devoid of greenery, lacking sustainability features like solar panels or rainwater systems"},
        # {"concept": "The Heritage Hub", "positive": "A modular community center with interconnected pods that can be reconfigured for various uses, featuring a rooftop garden", "negative": "A rigid, unchangeable building with no adaptability or connection to nature"},
        # {"concept": "The Interconnected Hive", "positive": "A community center blending traditional Singaporean architecture with modern design, featuring sustainable materials and spaces for diverse cultural activities", "negative": "A monolithic structure with no cultural integration or use of sustainable materials"},
        # {"concept": "The Tropical Canopy", "positive": "A community center extending into the waterfront with an amphitheater and floating modules, incorporating rainwater collection and hydroponic gardens", "negative": "A landlocked building with no connection to the waterfront or sustainable water usage features"},
        # {"concept": "The Waterfront Pavilion", "positive": "A zero-energy building with passive cooling, green roofs, wind turbines, and photovoltaic panels, focused on environmental education", "negative": "A high-energy consuming building with no sustainable features or focus on environmental education"}
        # ] and some text after"""
        # parsed_list_of_dicts = extract_and_parse_list_of_dicts(text)[0]

        # Make num_images an input field
        output_path = "generated_images/"
        model = "diffusers/stable-diffusion-xl-1.0-inpainting-0.1"

        generate_image_from_prompts(parsed_list_of_dicts, uploaded_image, uploaded_mask, num_images, output_path, model)
        
        # Display the generated images
        for subfolder in os.listdir(output_path):
            subfolder_path = os.path.join(output_path, subfolder)
            
            # Check if the path is indeed a folder
            if os.path.isdir(subfolder_path):
                # Display the folder name as a title
                st.header(subfolder)
                # display the positive prompt
                
                for info in parsed_list_of_dicts:
                    if info["concept"] == subfolder:
                        st.write(f"{info['positive']}")
                
                # Collect all image paths in the subfolder
                image_paths = [os.path.join(subfolder_path, f) for f in os.listdir(subfolder_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
                
                # Initialize a column list to hold the images
                cols = st.columns(len(image_paths))
        
                # Iterate through each image path and the corresponding column to display the image
                for col, img_path in zip(cols, image_paths):
                    image = Image.open(img_path)
                    col.image(image, use_column_width=True)
                
            # Clear the folder after displaying the images, but do not delete the parent folder
            os.rmdir(subfolder_path)
        