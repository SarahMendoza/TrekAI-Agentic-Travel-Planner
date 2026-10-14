from sqlite3 import Time

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graphs import Graph, StateGraph, START, END
from typing_extensions import TypedDict


class TravelAgent(TypedDict):
    name: str
    location: str
    guest_count: int
    dates: Time

def create_travel_agent_prompt() -> PromptTemplate:
    template = """You are a travel agent. You will be given information about a client and their travel preferences. Your task is to create a personalized travel itinerary for them.

    Client Information:
    Name: {name}
    Location: {location}
    Guest Count: {guest_count}
    Dates: {dates}

    Please provide a detailed travel itinerary that includes recommended destinations, activities, accommodations, and any other relevant information. Make sure to tailor the itinerary to the client's preferences and needs.

    Itinerary:
    """
    
    return PromptTemplate(
        input_variables=["name", "location", "guest_count", "dates"],
        template=template,
        output_parser=StrOutputParser()
    )





def planner_agent(travel_agent: TravelAgent) -> str:
    prompt = create_travel_agent_prompt()
    itinerary = prompt.format(**travel_agent)
    return itinerary

def flight_agent(travel_agent: TravelAgent) -> str:
    prompt = create_travel_agent_prompt()
    flight_details = prompt.format(**travel_agent)
    return flight_details

def lodging_agent(travel_agent: TravelAgent) -> str:
    prompt = create_travel_agent_prompt()
    lodging_details = prompt.format(**travel_agent)
    return lodging_details

builder = StateGraph(TravelAgent)
builder.add_node("planner_agent", planner_agent)
builder.add_node("flight_agent", flight_agent)
builder.add_node("lodging_agent", lodging_agent)
builder.add_edge(START, "planner_agent")
builder.add_edge("planner_agent", "flight_agent")
builder.add_edge("planner_agent", "lodging_agent")
builder.add_edge("planner_agent", END)

graph = builder.compile()