from crewai import Crew, Task
from textwrap import dedent
from archi_agents import Architecture_idea_exploration_agent
from langchain_community.chat_models import ChatOpenAI
from utils import extract_and_parse_list_of_dicts

import os
from dotenv import load_dotenv, find_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(BASEDIR, '.env.example'))

llm = ChatOpenAI(model_name="gpt-4-0125-preview")
# llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125")

brief = dedent("""
The client is a local government that is looking to build a new community center in Kallang, Singapore. 
The community center will be a multi-purpose building that will be used for a variety of activities such as sports, meetings, and events.
The community center should foster a sense of community for the residents of Kallang and should be a place where people can come together and socialize.
The community center should be designed to be sustainable and environmentally friendly.
The community center should be designed to be accessible to all residents, including those with disabilities.
The community center should be designed to be flexible and adaptable to different uses.
""")

task1 = dedent(f"""
Given the design brief below, try to understand the task and generate questions to research. 
The questions should be focused on understanding the actual content of the brief, the site, the people, the culture, the surrounding environment, climate and so on.
The answer to the questions should be readily searchable on the internet.
               
The brief: {brief}
""")

task2 = dedent(f"""
Given the questions, research the answers to the questions and summarize the findings.
You must always use the tool to search the internet to find the answers to the questions.

After you have obtained the findings, output the summary incorporating all the research findings. Your final answer is the summary.         
""")

task3 = dedent(f"""
Given the design brief and the research findings, generate 5 vastly different architecture design concepts which are unique, interesting, innovative and meets the requirements of the brief.
The design concepts should make use of research findings.
The design concepts should be focus on describing the actual form of the design, to help with visualization.

The brief:
{brief}
               """)

task4 = dedent(f"""
Given the design concepts, generate a positive prompt and a negative prompt for each concept, the prompts will be the inputs to a text to image model to generate images of the concepts.
The prompts should be brief and focused on describing the actual form of the design, to help with visualization.
Give your output as a list of json objects in the format: 
{{"concept": "name of concept", "positive": "positive prompt", "negative": "negative prompt"}}."""
)
               
tasks = [task1, task2, task3, task4]
class ArchitectureDesignCrew:

  def __init__(self, tasks):
    self.tasks = tasks

  def run(self):
    agents = Architecture_idea_exploration_agent(llm=llm)
    tasks = self.tasks
    brief_understanding_agent = agents.architecture_brief_question_agent()
    research_assistant_agent = agents.research_assistant()
    concept_generation_agent = agents.concept_generation_agent()
    text_to_image_prompt_agent = agents.text_to_image_prompt_agent()
    agents = [brief_understanding_agent, research_assistant_agent, concept_generation_agent, text_to_image_prompt_agent]
    task1 = Task(description=tasks[0], agent=brief_understanding_agent)
    task2 = Task(description=tasks[1], agent=research_assistant_agent)
    task3 = Task(description=tasks[2], agent=concept_generation_agent)
    task4 = Task(description=tasks[3], agent=concept_generation_agent)
    tasks = [task1, task2, task3, task4]
    
    crew = Crew(
      agents=agents,
      tasks=tasks,
      verbose=True
    )

    result = crew.kickoff()
    return result

if __name__ == "__main__":
  design_crew = ArchitectureDesignCrew(tasks)
  result = design_crew.run()
  print(result)
  
  ideas = extract_and_parse_list_of_dicts(result)
  print(ideas)