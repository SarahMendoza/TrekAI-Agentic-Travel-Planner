# AGENT BASE CODE -- Test agent and tool use using a calculator example agent

import os
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI


# set up your tools list and API keys
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    mult = a * b
    print("\n\nUsing multiply tool.", a, " * ", b, " = ", mult, "\n\n")
    return mult

@tool
def square(a) -> int:
    """Calculates the square of a number."""
    a = int(a)
    square = a * a
    print("\n\nUsing square tool.", a, " * ", a, " = ", square, "\n\n")
    return square

tools = [ multiply, square]



system_prompt = """
You are a mathematical assistant. Use your tools to answer questions.
If you do not have a tool to answer the question, say so.

Return only the answer. Example:
Human: What is 1 + 1?
AI: 2
"""


# Choose an LLM
os.environ["OPENAI_API_KEY"] = "add api key here"
llm = ChatOpenAI(temperature=0, model="gpt-5.4")


# construct the JSON agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    #debug=True
    )



result = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the value of 4 squared?"}]}
)
print(result["messages"][-1].content)