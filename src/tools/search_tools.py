import json
import os

import requests
from langchain.tools import tool
from tavily import TavilyClient

# class SearchTools():

#   @tool("Search the internet")
#   def search_internet(query):
#     """Useful to search the internet
#     about a a given topic and return relevant results"""
#     top_result_to_return = 2
#     url = "https://google.serper.dev/search"
#     payload = json.dumps({"q": query})
#     headers = {
#         'X-API-KEY': os.environ['SERPER_API_KEY'],
#         'content-type': 'application/json'
#     }
#     response = requests.request("POST", url, headers=headers, data=payload)
#     # check if there is an organic key
#     if 'organic' not in response.json():
#       return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
#     else:
#       results = response.json()['organic']
#       string = []
#       for result in results[:top_result_to_return]:
#         try:
#           string.append('\n'.join([
#               # f"Title: {result['title']}", f"Link: {result['link']}",
#               f"Snippet: {result['snippet']}", "\n-----------------"
#           ]))
#         except KeyError:
#           next

#       return '\n'.join(string)

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
  print(SearchTools.search_internet("population of Kallang Bahru, Singapore"))