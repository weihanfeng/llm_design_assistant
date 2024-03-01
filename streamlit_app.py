import streamlit as st
from PIL import Image
import io
from streamlit_drawable_canvas import st_canvas
import pandas as pd

IMAGE_WIDTH = 16 * 50
IMAGE_HEIGHT = 10 * 50

def crop_image(image, height, width):
    """Crop image to specified height and width without changing aspect ratio."""
    # Get current aspect ratio
    aspect_ratio = image.size[0] / image.size[1]
    # Calculate new height and width based on aspect ratio
    new_height = int(width / aspect_ratio)
    new_width = int(height * aspect_ratio)
    # Crop image to fit new dimensions
    if new_height > height:
        # Crop height
        image = image.crop(((image.size[0] - new_width) / 2, 0, (image.size[0] + new_width) / 2, image.size[1]))
    else:
        # Crop width
        image = image.crop((0, (image.size[1] - new_height) / 2, image.size[0], (image.size[1] + new_height) / 2))
    return image.resize((width, height))

# Streamlit UI
st.title("Architecture Design and Visualization Tool")

# User Inputs
uploaded_image = st.file_uploader("Upload the site image:", type=["jpg", "jpeg"])
# uploaded_mask = st.file_uploader("Upload the mask image:", type=["jpg", "jpeg"])
architecture_brief = st.text_area("Enter the architecture brief:")

# crop image
if uploaded_image:
    image = Image.open(uploaded_image)
    image = crop_image(image, IMAGE_HEIGHT, IMAGE_WIDTH)
    # st.image(image)

# Specify canvas parameters in application
drawing_mode = st.sidebar.selectbox(
    "Drawing tool:", ("point", "freedraw", "line", "rect", "circle", "transform")
)

stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
if drawing_mode == 'point':
    point_display_radius = st.sidebar.slider("Point display radius: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color hex: ")
bg_color = st.sidebar.color_picker("Background color hex: ", "#eee")
# bg_image = st.sidebar.file_uploader("Background image:", type=["png", "jpg"])

realtime_update = st.sidebar.checkbox("Update in realtime", True)



# Create a canvas component
if uploaded_image:
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        background_image=Image.open(uploaded_image) if uploaded_image else None,
        update_streamlit=realtime_update,
        height=IMAGE_HEIGHT,
        width=IMAGE_WIDTH,
        drawing_mode=drawing_mode,
        point_display_radius=point_display_radius if drawing_mode == 'point' else 0,
        key="canvas",
    )

    # convert canvas result to pil image mask, with only two values, while keeping the original image size
    if canvas_result.image_data is not None:
        # Convert image data to a PIL image
        mask = Image.fromarray(canvas_result.image_data.astype("uint8"), "RGBA")
        # Convert mask to grayscale
        mask = mask.convert("L")
        # Convert mask to binary
        mask = mask.point(lambda x: 0 if x == 0 else 255)
        # Resize mask to original image size
        mask = mask.resize((image.size[0], image.size[1]))

    # A button to save the mask