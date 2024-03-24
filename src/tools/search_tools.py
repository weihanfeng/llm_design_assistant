import json
import os

import requests
from langchain.tools import tool
from tavily import TavilyClient

class SearchTools():

  @tool("Search the internet")
  def search_internet(query):
    """Useful to search the internet
    about a a given topic and return relevant results"""
    top_result_to_return = 3
    tavily = TavilyClient(api_key=os.environ['TAVILY_API_KEY'])
    response = tavily.search(query=query, search_depth="advanced", max_results=top_result_to_return)
    context = [obj["content"] for obj in response["results"]] 
    context = '\n'.join(context)

    return context

if __name__ == "__main__":
  print(SearchTools.search_internet("What is the capital of USA?"))