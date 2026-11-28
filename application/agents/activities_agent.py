import json
import re
import os 
from langchain.agents import AgentState, create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from openai import api_key
import serpapi
from dotenv import load_dotenv
from state import ActivityOption, PlannerState

load_dotenv()  # Load environment variables from .env file
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

class ActivitiesAgentState(AgentState):
    activities: list[ActivityOption]

chat = ChatOpenAI(model="gpt-4o", temperature=0.7)

@tool
def search_activities(destination: str, runtime: ToolRuntime) -> Command:
    """Search for priced attractions in a destination city."""
    client = serpapi.Client(api_key=api_key)
    results = client.search({
        "engine": "google",
        "q": f"Top sights in {destination}",
    })

    activity_options: list[ActivityOption] = []

    for sight in results.get("top_sights", {}).get("sights", []):
        price_text = str(sight.get("price", "")).strip()
        match = re.fullmatch(r"\$([0-9,]+(?:\.[0-9]{1,2})?)", price_text)

        if match:
            cost = float(match.group(1).replace(",", ""))
        elif price_text.lower() == "free":
            cost = 0.0
        else:
            continue  # No usable price; do not treat missing prices as free.

        activity_options.append({
            "name": sight.get("title", ""),
            "category": "attraction",
            "estimated_cost": cost,
            "day": "",  # The planner assigns the day later.
            "summary": sight.get("description", ""),
        })

    return Command(update={
        "activities": activity_options,
        "messages": [
            ToolMessage(
                content=json.dumps(activity_options),
                tool_call_id=runtime.tool_call_id,
            )
        ],
    })

search_prompt = (
    "You are an agent that searches for activities in a destination city. "
    "You will be given a destination and should return a list of activities with their estimated costs."
)

search_activities_agent = create_agent(
    model=chat,
    tools=[search_activities],
    system_prompt=search_prompt,
    state_schema=ActivitiesAgentState,
)


def activities_agent(state: PlannerState) -> dict:
    destination = state["user_preferences"]["destination_city"]
    task = state.get("activities_task")
    instructions = task["instructions"] if task else "Research activities."

    agent_input: ActivitiesAgentState = {
        "activities": [],
        "messages": [
            HumanMessage(
                content=f"{instructions}\nSearch activities in {destination}."
            )
        ],
    }

    result = search_activities_agent.invoke(agent_input)
    return {"activities": result["activities"]}