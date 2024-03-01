from textwrap import dedent
from langchain_community.chat_models import ChatOpenAI
from utils import extract_and_parse_list_of_dicts, generate_image_from_prompts, convert_image, generate_image_mask
from  archi_tasks import task1, task2, task3, task4, generate_task_with_brief
from archi_crew import ArchitectureDesignCrew

import os
from dotenv import load_dotenv, find_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASEDIR, '.env.example'))

llm = ChatOpenAI(model_name="gpt-4-0125-preview")
# llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125")

design_brief = dedent("""
The client is a local government that is looking to build a new community center in Kallang, Singapore. 
The community center will be a multi-purpose building that will be used for a variety of activities such as sports, meetings, and events.
The community center should foster a sense of community for the residents of Kallang and should be a place where people can come together and socialize.
The community center should be designed to be sustainable and environmentally friendly.
The community center should be designed to be flexible and adaptable to different uses.
""")

tasks = [generate_task_with_brief(task1, design_brief), task2, generate_task_with_brief(task3, design_brief), task4]


if __name__ == "__main__":
  design_crew = ArchitectureDesignCrew(tasks, llm)
  result = design_crew.run()
  # print(result)
  
  parsed_list_of_dicts = extract_and_parse_list_of_dicts(result)[0]

  # Example image generation
  num_images = 5
  image_path = "../sample_site.jpg"
  output_path = "generated_images/"
  model = "diffusers/stable-diffusion-xl-1.0-inpainting-0.1"

  image = convert_image(image_path)
  mask = generate_image_mask(image, 0.3, 0.23, 0.87, 0.65)
  # display_mask_with_image(image, mask)

  generate_image_from_prompts(parsed_list_of_dicts, image, mask, num_images, output_path, model)