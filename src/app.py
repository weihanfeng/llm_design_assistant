import streamlit as st
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas
import os
from dotenv import load_dotenv

from textwrap import dedent
from langchain_community.chat_models import ChatOpenAI
from utils import (
    extract_and_parse_list_of_dicts,
    generate_image_from_prompts,
    display_mask_with_image,
)
from archi_tasks import task1, task2, task3, task4, generate_task_with_brief
from archi_crew import ArchitectureDesignCrew

# Env set up
BASEDIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASEDIR, ".env"))

llm = ChatOpenAI(model_name="gpt-4-0125-preview")
repo_id = os.getenv("MODEL")

# Set page layout to wide
st.set_page_config(layout="wide")

# Initialize session state variable for the last rectangle
if "last_rect" not in st.session_state:
    st.session_state["last_rect"] = None

# Streamlit UI
st.title("Design Concept Generator")

# User Inputs
uploaded_image = st.sidebar.file_uploader(
    "Upload the site image:", type=["jpg", "jpeg", "png"]
)
design_brief = st.sidebar.text_area("Enter the architecture brief:")
num_concepts = st.sidebar.number_input(
    "Number of concepts to generate", min_value=1, max_value=15, value=5
)
num_images = st.sidebar.number_input(
    "Number of images per concept", min_value=1, max_value=15, value=5
)

MAX_WIDTH = 1000  # Maximum display width for the canvas

if uploaded_image is not None:
    # Load the image
    image = Image.open(uploaded_image)
    image_array = np.array(image)

    # Get original dimensions
    orig_width, orig_height = image.size

    # If the image is wider than MAX_WIDTH, resize it
    if orig_width > MAX_WIDTH:
        scaling_factor = MAX_WIDTH / orig_width
        new_width = int(orig_width * scaling_factor)
        new_height = int(orig_height * scaling_factor)
        resized_image = image.resize((new_width, new_height))
    else:
        scaling_factor = 1.0
        new_width = orig_width
        new_height = orig_height
        resized_image = image

    # Display the image with interaction
    st.subheader("Select site") 

    # Create columns for the clear button and drawing tool selection
    col1, col2 = st.columns([1, 5])

    with col1:
        # Add a clear button to allow user to clear the canvas
        if st.button("Clear Selection"):
            # Clear the last rectangle
            st.session_state["last_rect"] = None
            # Force canvas to update
            st.rerun()

    with col2:
        # Drawing options as radio buttons
        drawing_mode = st.radio(
            "Selection mode:", ("Draw", "Move/Resize"), horizontal=True
        )

    if drawing_mode == "Move/Resize":
        drawing_mode_value = "transform"
    elif drawing_mode == "Draw":
        drawing_mode_value = "rect"

    # Prepare initial_drawing data if last rectangle exists
    initial_drawing = None
    if st.session_state["last_rect"] is not None:
        initial_drawing = {
            "version": "4.4.0",
            "objects": [st.session_state["last_rect"]],
        }

    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",  # Semi-transparent red fill
        stroke_width=2,
        stroke_color="rgba(0, 255, 0, 1)",  # Green stroke
        background_image=resized_image,  # Use resized PIL image
        update_streamlit=True,
        height=new_height,  # Set height to match resized image
        width=new_width,  # Set width to match resized image
        drawing_mode=drawing_mode_value,  # Use the selected drawing mode
        key="canvas",
        initial_drawing=initial_drawing,  # Load existing rectangle if any
        display_toolbar=False,  # Hide the toolbar
    )

    if canvas_result.json_data is not None:
        # Get objects from canvas
        objects = canvas_result.json_data["objects"]

        if objects:
            # Keep only the last rectangle drawn
            rect_objects = [obj for obj in objects if obj["type"] == "rect"]

            if rect_objects:
                # Take the last rectangle drawn
                rect = rect_objects[-1]

                # Check if a new rectangle was drawn or edited
                if st.session_state["last_rect"] != rect:
                    # Update the session state with the last rectangle
                    st.session_state["last_rect"] = rect

                    # Force the app to rerun to update the canvas
                    st.rerun()
        else:
            # If no objects exist, clear the last rectangle
            if st.session_state["last_rect"] is not None:
                st.session_state["last_rect"] = None
                st.rerun()
    else:
        st.session_state["last_rect"] = None

    # If we have a last rectangle, generate the mask
    if st.session_state["last_rect"] is not None:
        rect = st.session_state["last_rect"]
        # Create a blank mask for the original image size
        mask_array = np.zeros((orig_height, orig_width), dtype=np.uint8)

        # Adjust for scaleX and scaleY
        left = rect["left"] / scaling_factor
        top = rect["top"] / scaling_factor
        width = rect["width"] * rect["scaleX"] / scaling_factor
        height = rect["height"] * rect["scaleY"] / scaling_factor

        # Convert to integer pixel coordinates
        left = int(left)
        top = int(top)
        width = int(width)
        height = int(height)

        # Ensure coordinates are within image boundaries
        left = max(0, left)
        top = max(0, top)
        right = min(orig_width, left + width)
        bottom = min(orig_height, top + height)

        # Fill the mask with white in the selected region
        mask_array[top:bottom, left:right] = 255

        # Convert mask_array to PIL Image
        mask = Image.fromarray(mask_array)

        # Display the image and mask together
        # st.subheader("Selected Mask")
        # st.image(
        #     display_mask_with_image(image, mask), caption="The site", use_column_width=True
        # )

else:
    st.session_state["last_rect"] = None

# Check if both the image and mask are ready
if (
    st.sidebar.button("Submit")
    and uploaded_image is not None
    and st.session_state["last_rect"] is not None
):
    with st.spinner("Generating design concepts..."):
        # Image is already a PIL Image
        # Mask is already a PIL Image

        print(type(image))
        print(image.size)
        print(type(mask))
        print(mask.size)

        tasks = [
            generate_task_with_brief(task1, design_brief),
            task2,
            generate_task_with_brief(task3, design_brief),
            task4,
        ]
        design_crew = ArchitectureDesignCrew(tasks, llm)
        result = design_crew.run(num_concepts=num_concepts)
        parsed_list_of_dicts = extract_and_parse_list_of_dicts(result)[0]

        # Make num_images an input field
        output_path = "generated_images/"
        # model = "diffusers/stable-diffusion-xl-1.0-inpainting-0.1"
        # get HF_HOME from environment variable and append to model
        generate_image_from_prompts(
            parsed_list_of_dicts, image, mask, num_images, output_path, repo_id
        )

        for subfolder in os.listdir(output_path):
            subfolder_path = os.path.join(output_path, subfolder)

            if os.path.isdir(subfolder_path):
                st.header(subfolder)

                for info in parsed_list_of_dicts:
                    if info["concept"] == subfolder:
                        st.write(f"{info['positive']}")

                image_paths = [
                    os.path.join(subfolder_path, f)
                    for f in os.listdir(subfolder_path)
                    if f.endswith((".png", ".jpg", ".jpeg"))
                ]

                cols = st.columns(len(image_paths))

                for col, img_path in zip(cols, image_paths):
                    generated_image = Image.open(img_path)
                    col.image(generated_image, use_column_width=True)

    # Clean up the generated images
    for subfolder in os.listdir(output_path):
        subfolder_path = os.path.join(output_path, subfolder)
        if os.path.isdir(subfolder_path):
            for f in os.listdir(subfolder_path):
                os.remove(os.path.join(subfolder_path, f))
            os.rmdir(subfolder_path)
