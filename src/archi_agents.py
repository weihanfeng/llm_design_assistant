from crewai import Agent
from tools.search_tools import SearchTools


class Architecture_idea_exploration_agent:

    def __init__(self, llm):
        self.llm = llm

    def architecture_brief_question_agent(self, num_questions=5):
        return Agent(
            role="Architecture design brief questioner",
            goal="Asks questions regarding the architecture design brief in order to find out more about the brief. The question can range from the site, the people, the culture, the surrounding environment, climate and so on. The goal is to understand the requirements of the architecture design brief through a series of questions.",
            backstory=f"""An expert in understanding the requirements of the architecture design brief through a series of questions. You should only ask a maximum of {num_questions} questions.""",
            verbose=True,
            llm=self.llm,
            allow_delegation=False,
        )

    def research_assistant(self):
        return Agent(
            role="Expert architecture researcher",
            goal="Researches and provides answers to a set of questions using the Search the internet tool. After you have done your research, you will provide a detailed summary on the findings.",
            backstory="""You must always use the tool, Search the internet, to search the internet to find the answers to the questions. You must research all the questions you received.""",
            tools=[
                SearchTools.search_internet,
            ],
            verbose=True,
            llm=self.llm,
            allow_delegation=False,
        )

    def concept_generation_agent(self, num_concepts=5):
        return Agent(
            role="Architecture concept generation agent",
            goal=f"""Given a architecture design brief and some research, generate {num_concepts} vastly different architecture design concepts which are unique, interesting, innovative and meets the requirements of the brief.""",
            backstory="""You must always use the research findings to generate the concepts. You must never use any tool.""",
            verbose=True,
            llm=self.llm,
            allow_delegation=False,
        )

    def text_to_image_prompt_agent(self):
        return Agent(
            role="Text to image prompt agent",
            goal="""Given the design concepts, generate a positive prompt and a negative prompt for each concept, the prompts will be the inputs to a text to image model to generate images of the concepts.""",
            backstory="""The prompts should be brief and focused on describing the actual form of the design, to help with visualization. Give your output as a list of json objects in the format {"concept": "name of concept", "positive": "positive prompt", "negative": "negative prompt"}.""",
            verbose=True,
            llm=self.llm,
            allow_delegation=False,
        )
