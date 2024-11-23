import streamlit as st
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# Set page layout to wide
st.set_page_config(layout="wide")

# Title
st.title("Interactive Image Selection and Mask Generator")

# Initialize session state variable for the last rectangle
if 'last_rect' not in st.session_state:
    st.session_state['last_rect'] = None

# Sidebar
st.sidebar.header("Upload an Image")
uploaded_file = st.sidebar.file_uploader(
    "Choose an image file", type=["jpg", "jpeg", "png"]
)

MAX_WIDTH = 1000  # Maximum display width for the canvas

if uploaded_file is not None:
    # Load the image
    image = Image.open(uploaded_file)
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
    st.subheader("Interactive Selection")

    # Create columns for the clear button and drawing tool selection
    col1, col2 = st.columns([1, 5])

    with col1:
        # Add a clear button to allow user to clear the canvas
        if st.button('Clear Selection'):
            # Clear the last rectangle
            st.session_state['last_rect'] = None
            # Force canvas to update
            st.rerun()

    with col2:
        # Drawing options as radio buttons
        drawing_mode = st.radio(
            "Selection mode:",
            ("Draw", "Move/Resize"),
            horizontal=True
        )

    if drawing_mode == "Move/Resize":
        drawing_mode_value = 'transform'
    elif drawing_mode == "Draw":
        drawing_mode_value = 'rect'

    # Prepare initial_drawing data if last rectangle exists
    initial_drawing = None
    if st.session_state['last_rect'] is not None:
        initial_drawing = {
            "version": "4.4.0",
            "objects": [st.session_state['last_rect']]
        }

    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",       # Semi-transparent red fill
        stroke_width=2,
        stroke_color="rgba(0, 255, 0, 1)",       # Green stroke
        background_image=resized_image,          # Use resized PIL image
        update_streamlit=True,
        height=new_height,                       # Set height to match resized image
        width=new_width,                         # Set width to match resized image
        drawing_mode=drawing_mode_value,         # Use the selected drawing mode
        key="canvas",
        initial_drawing=initial_drawing,         # Load existing rectangle if any
        display_toolbar=False,                   # Hide the toolbar
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
                if st.session_state['last_rect'] != rect:
                    # Update the session state with the last rectangle
                    st.session_state['last_rect'] = rect

                    # Force the app to rerun to update the canvas
                    st.rerun()
        else:
            # If no objects exist, clear the last rectangle
            if st.session_state['last_rect'] is not None:
                st.session_state['last_rect'] = None
                st.rerun()

    # If we have a last rectangle, generate the mask
    if st.session_state['last_rect'] is not None:
        rect = st.session_state['last_rect']
        # Create a blank mask for the original image size
        mask = np.zeros((orig_height, orig_width), dtype=np.uint8)

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
        mask[top:bottom, left:right] = 255

        # Display the mask
        st.subheader("Generated Mask")
        mask_pil = Image.fromarray(mask)
        st.image(mask_pil, caption="Mask", use_column_width=True)
else:
    st.session_state['last_rect'] = None
