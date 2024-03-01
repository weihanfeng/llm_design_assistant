from crewai import Crew, Task
from textwrap import dedent
from archi_agents import Architecture_idea_exploration_agent
from langchain_community.chat_models import ChatOpenAI
from utils import extract_and_parse_list_of_dicts, generate_image_from_prompts, convert_image, generate_image_mask

class ArchitectureDesignCrew:

  def __init__(self, tasks, llm):
    self.tasks = tasks
    self.llm = llm

  def run(self):
    agents = Architecture_idea_exploration_agent(llm=self.llm)
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