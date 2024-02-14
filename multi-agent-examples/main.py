from crewai import Crew, Task
from textwrap import dedent
from archi_agents import Architecture_idea_exploration_agent
from langchain.llms import OpenAI

import os
from dotenv import load_dotenv, find_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env.example'))
print("BASEDIR: ", BASEDIR)
print(os.getenv('OPENAI_API_KEY'))

llm = OpenAI(model_name="gpt-3.5-turbo")

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

The brief: {brief}
""")

task2 = dedent(f"""
Given the questions, research the answers to the questions and summarize the findings.          
""")

task3 = dedent(f"""
Given the design brief and the research findings, generate 10 vastly different architecture design concepts which are unique, interesting, innovative and meets the requirements of the brief.
The brief:
{brief}
               """)
              
tasks = [task1, task2, task3]
class ArchitectureDesignCrew:

  def __init__(self, tasks):
    self.tasks = tasks

  def run(self):
    agents = Architecture_idea_exploration_agent(llm=llm)
    tasks = self.tasks
    brief_understanding_agent = agents.architecture_brief_question_agent()
    research_assistant_agent = agents.research_assistant()
    concept_generation_agent = agents.concept_generation_agent()
    agents = [brief_understanding_agent, research_assistant_agent, concept_generation_agent]
    task1 = Task(description=tasks[0], agent=brief_understanding_agent)
    task2 = Task(description=tasks[1], agent=research_assistant_agent)
    task3 = Task(description=tasks[2], agent=concept_generation_agent)
    tasks = [task1, task2, task3]
    
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
