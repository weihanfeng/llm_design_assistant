import re
import ast
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import matplotlib.pyplot as plt
from diffusers import StableDiffusionInpaintPipeline, StableDiffusionXLInpaintPipeline
import torch
import os

# Parsing
def extract_and_parse_list_of_dicts(text):
    # Adjust the regex pattern to account for optional spaces and newline characters
    # around the curly braces and commas. This pattern is more flexible and can match
    # lists of dictionaries with various spacings and newline characters.
    pattern = r"\[\s*\n?\{.*?\}\s*\n?\]"
    
    # Use non-greedy matching for the content inside the curly braces and allow for multiple
    # dictionaries by including commas and optional spaces/newlines in the pattern.
    # The pattern uses re.DOTALL to match across multiple lines.
    matches = re.findall(pattern, text, re.DOTALL)
    
    parsed_lists = []
    for match in matches:
        try:
            # Try to parse each extracted string using ast.literal_eval
            result = ast.literal_eval(match)
            parsed_lists.append(result)
        except (ValueError, SyntaxError) as e:
            # Handle exceptions raised by incorrect string format or content
            return f"Error parsing extracted text: {e}"
    
    if parsed_lists:
        return parsed_lists
    else:
        return "No list of dictionaries found in the string."

# Image generation functions
    
def convert_image(image_path_or_url):
    # Check if the input is a URL or a local file path
    if image_path_or_url.startswith('http://') or image_path_or_url.startswith('https://'):
        # Handle online images
        response = requests.get(image_path_or_url)
        img_data = response.content
        pil_image = Image.open(BytesIO(img_data))
    else:
        # Handle local images
        pil_image = Image.open(image_path_or_url)

    return pil_image

def generate_image_mask(image, top_left_ratio_x, top_left_ratio_y, bottom_right_ratio_x, bottom_right_ratio_y):
    """
    Generate a mask for the given PIL Image based on specified ratios for the top-left and bottom-right points of the mask.

    Parameters:
    - image: PIL.Image object.
    - top_left_ratio_x: Ratio of the mask's top-left x-coordinate to the image's width.
    - top_left_ratio_y: Ratio of the mask's top-left y-coordinate to the image's height.
    - bottom_right_ratio_x: Ratio of the mask's bottom-right x-coordinate to the image's width.
    - bottom_right_ratio_y: Ratio of the mask's bottom-right y-coordinate to the image's height.

    Returns:
    - A PIL.Image object representing the mask.
    """
    # Calculate mask coordinates
    width, height = image.size
    top_left_x = int(width * top_left_ratio_x)
    top_left_y = int(height * top_left_ratio_y)
    bottom_right_x = int(width * bottom_right_ratio_x)
    bottom_right_y = int(height * bottom_right_ratio_y)

    # Create a new image for the mask with the same dimensions as the original image, filled with black
    mask = Image.new('L', (width, height), 0)

    # Create a draw object and draw the rectangle (white area) on the mask
    draw = ImageDraw.Draw(mask)
    draw.rectangle([top_left_x, top_left_y, bottom_right_x, bottom_right_y], fill=255)

    return mask

def display_mask_with_image(image, mask):
    """
    Display an overlay of the mask (with 50% transparency) over the original image.

    Parameters:
    - image: PIL.Image object of the original image.
    - mask: PIL.Image object of the mask.
    """
    # Convert the original image to RGBA if it's not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')

    # Ensure mask is in mode 'L' for transparency manipulation
    if mask.mode != 'L':
        mask = mask.convert('L')

    # Create an RGBA version of the mask with 50% transparency
    mask_rgba = Image.new('RGBA', mask.size, color=(0, 0, 0, 0))  # Transparent background
    mask_rgba.putalpha(mask.point(lambda p: int(p * 0.5)))  # Apply 50% transparency

    # Composite the mask over the image
    combined = Image.alpha_composite(image, mask_rgba)

    # # save the image in a temp file
    # combined_path = "temp_overlay.png"
    # combined.save(combined_path)
    return combined

def resize_generated_image_to_original(generated_img, original_img):
    """
    Resize the generated image to match the dimensions of the original image.

    Parameters:
    - generated_img: PIL.Image object of the generated image.
    - original_img: PIL.Image object of the original image.

    Returns:
    - A new PIL.Image object of the generated image resized to the original image's dimensions.
    """
    # Get the dimensions of the original image
    original_width, original_height = original_img.size

    # Resize the generated image to these dimensions
    resized_generated_img = generated_img.resize((original_width, original_height))

    return resized_generated_img

def initialize_pipeline(model):
    # Initialize the pipeline
    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        model,
        torch_dtype=torch.float16,)
    pipe.to("cuda")
    return pipe

def generate_image_from_prompts(prompt_list, image, mask, num_output_images, output_path, model):
    pipe = StableDiffusionXLInpaintPipeline.from_pretrained(
        model,
        torch_dtype=torch.float16,)
    pipe.to("cuda")

    # make output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    for idea in prompt_list:
        positive = idea["positive"]
        negative = idea["negative"]
        # make folder for each idea with the name of the concept
        concept = idea["concept"]
        concept_path = output_path + concept + "/"
        os.makedirs(concept_path, exist_ok=True)

        # Generate images
        for i in range(num_output_images):
            generated_image = pipe(
                prompt=positive,
                negative_prompt=negative,
                image=image,
                mask_image=mask,
                guidance_scale=15,
                num_inference_steps=20,  # steps between 15 and 30 work well for us
                strength=0.99,).images[0]
            # Resize the generated image to match the dimensions of the original image
            generated_image = resize_generated_image_to_original(generated_image, image)

            print(f"Image generation successful for concept: '{concept}' ({i+1}/{num_output_images})")
            
            # Save the generated image
            generated_image.save(concept_path + f"generated_image_{i}.png")
        
        # Save the positive and negative prompts as text file in the same folder
        with open(concept_path + "prompts.txt", "w") as file:
            file.write(f"Positive prompt: {positive}\nNegative prompt: {negative}")
        
    print("Image generation complete.")

if __name__ == "__main__":
    # Example usage
    text = """Some unneeded text before [
    {"concept": "The Urban Oasis", "positive": "A multi-level garden community center with seamless integration of indoor and outdoor spaces, utilizing solar panels and rainwater harvesting", "negative": "A concrete structure devoid of greenery, lacking sustainability features like solar panels or rainwater systems"},
    {"concept": "The Transformative Hive", "positive": "A modular community center with interconnected pods that can be reconfigured for various uses, featuring a rooftop garden", "negative": "A rigid, unchangeable building with no adaptability or connection to nature"},
    {"concept": "The Cultural Tapestry", "positive": "A community center blending traditional Singaporean architecture with modern design, featuring sustainable materials and spaces for diverse cultural activities", "negative": "A monolithic structure with no cultural integration or use of sustainable materials"},
    {"concept": "The Waterfront Beacon", "positive": "A community center extending into the waterfront with an amphitheater and floating modules, incorporating rainwater collection and hydroponic gardens", "negative": "A landlocked building with no connection to the waterfront or sustainable water usage features"},
    {"concept": "The Eco Nexus", "positive": "A zero-energy building with passive cooling, green roofs, wind turbines, and photovoltaic panels, focused on environmental education", "negative": "A high-energy consuming building with no sustainable features or focus on environmental education"}
    ] and some text after"""
    parsed_list_of_dicts = extract_and_parse_list_of_dicts(text)[0]
    # print(parsed_list_of_dicts)

    # Example image generation
    num_images = 5
    image_path = "../sample_site.jpg"
    output_path = "generated_images/"
    model = "diffusers/stable-diffusion-xl-1.0-inpainting-0.1"

    image = convert_image(image_path)
    mask = generate_image_mask(image, 0.3, 0.23, 0.87, 0.65)
    # display_mask_with_image(image, mask)

    generate_image_from_prompts(parsed_list_of_dicts, image, mask, num_images, output_path, model)

