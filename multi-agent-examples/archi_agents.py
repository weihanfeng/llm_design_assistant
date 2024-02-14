from crewai import Agent
from tools.search_tools import SearchTools

class Architecture_idea_exploration_agent():
  
  def __init__(self, llm):
    self.llm = llm


  def architecture_brief_question_agent(self):
    return Agent(
        role='Architecture design brief questioner',
        goal='Asks questions regarding the architecture design brief in order to find out more about the brief. The question can range from the site, the people, the culture, the surrounding environment, climate and so on. The goal is to understand the requirements of the architecture design brief through a series of questions.',
        backstory=
        'An expert in understanding the requirements of the architecture design brief through a series of questions',
        verbose=True,
        llm=self.llm,
        allow_delegation=False,)

  def research_assistant(self):
    return Agent(
        role='Expert architecture researcher',
        goal='Researches and provides answers to a set of questions. After you have done your research, you will provide a detailed report on the findings and delegate the task to the Architecture concept generation agent',
        backstory="""An expert in researching and providing answers to a set of questions""",
        tools=[
            SearchTools.search_internet,
        ],
        verbose=True,
        llm=self.llm,
        allow_delegation=False,)

  def concept_generation_agent(self):
    return Agent(
        role='Architecture concept generation agent',
        goal="""Given a architecture design brief and some research, generate 10 vastly different architecture design concepts which are unique, interesting, innovative and meets the requirements of the brief.""",
        backstory="""Specialist in generating architecture design concepts based on a given brief and research""",
        verbose=True,
        llm=self.llm,
        allow_delegation=False,)
