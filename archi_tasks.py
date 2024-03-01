from textwrap import dedent

# Placeholder for the brief, which can be defined later
brief = None

def generate_task_with_brief(brief_content):
    global brief
    brief = brief_content
    task = dedent(f"""
    Given the design brief and the research findings, generate 5 vastly different architecture design concepts which are unique, interesting, innovative and meets the requirements of the brief.
    The design concepts should make use of research findings.
    The design concepts should be focus on describing the actual form of the design, to help with visualization.

    The brief:
    {brief}
    """)
    return task

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

task4 = dedent(f"""
Given the design concepts, generate a positive prompt and a negative prompt for each concept, the prompts will be the inputs to a text to image model to generate images of the concepts.
The prompts should be brief and focused on describing the actual form of the design, to help with visualization.
Give your output as a list of json objects in the format: 
{{"concept": "name of concept", "positive": "positive prompt", "negative": "negative prompt"}}."""
)