import re
from typing import NotRequired

from langchain.tools import tool
from langchain_ollama import ChatOllama
from state import FlightOption, PlannerState, ReturnFlightOption
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import serpapi


import json
import os
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from langchain.agents import AgentState, create_agent
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Command
from pydantic import BaseModel, Field

from state import UserPreferences, PlannerState
load_dotenv()  

flight_api_key = os.getenv("SERPAPI_API_KEY")

class FlightState(AgentState):
    user_preferences: UserPreferences
    flights: list[FlightOption]
    return_flights: list[ReturnFlightOption]
    selected_outbound_index: NotRequired[int]

class FlightParams(BaseModel):
    destination: str
    departure_city: str
    start_date: str
    end_date: str
    num_travelers: int = Field(ge=1)


chat = ChatOpenAI(temperature=0, model="gpt-5.4-mini")

from datetime import datetime

def format_date(value: str | None) -> str:
    if not value:
        raise ValueError("A date is required for round-trip searches.")
    
    cleaned = re.sub(
        r"\b(\d{1,2})(?:st|nd|rd|th)\b",
        r"\1",
        value.strip(),
        flags=re.IGNORECASE,
    )


    for date_format in ("%Y-%m-%d", "%B %d, %Y"):
        try:
            return datetime.strptime(cleaned, date_format).strftime(
                "%Y-%m-%d"
            )
        except ValueError:
            continue

    raise ValueError(f"Unsupported date format: {value!r}")


class AirportCodes(BaseModel):
    destination: str
    departure_city: str


preference_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Convert origin_city and destination_city to their respective IATA airport codes. "),
    ("human", "{user_preferences}"),
])

preference_chain = preference_prompt | chat.with_structured_output(
    AirportCodes,
    method="json_schema",
)

def convert_preferences_to_flight_params(
    user_preferences: UserPreferences,
) -> FlightParams:
    start_date = format_date(user_preferences.get("start_date"))
    end_date = format_date(user_preferences.get("end_date"))

    if end_date < start_date:
        raise ValueError("Return date cannot precede departure date.")

    airports = preference_chain.invoke({
        "user_preferences": json.dumps({
            "origin_city": user_preferences["origin_city"],
            "destination_city": user_preferences["destination_city"],
        })
    })
    print("Start date:", start_date)
    print("End date:", end_date)

    return FlightParams(
        departure_city=airports["origin_city"],
        destination=airports["destination_city"],
        start_date=start_date,
        end_date=end_date,
        num_travelers=user_preferences["travelers"],
    )
@tool
def search_flights(
    departure_city: str,
    destination: str,
    start_date: str,
    num_travelers: int,
    runtime: ToolRuntime,
    end_date: str
) -> Command:
    """Search available flights using IATA airport codes and ISO dates."""
    start_date = format_date(start_date)
    end_date = format_date(end_date)

    if end_date < start_date:
        raise ValueError("Return date cannot precede departure date.")

    arrival_city = destination
    client = serpapi.Client(api_key=flight_api_key)
    results = client.search({
    "engine": "google_flights",
    "departure_id": departure_city,
    "arrival_id": arrival_city,
    "currency": "USD",
    "type": "1",
    "outbound_date": start_date,
    "return_date": end_date,
    "adults": num_travelers,
    })

    # for result in results.get("best_flights", []):
    #     print("departure_tokeN:", result.get("departure_token"))

    if results.get("error"):
        raise ValueError(results["error"])

    raw_options = (
        results.get("best_flights", [])
        + results.get("other_flights", [])
    )

    flight_options: list[FlightOption] = []

    for option in raw_options:
        segments = option.get("flights", [])
        price = option.get("price")

        if not segments or price is None:
            continue

        first_segment = segments[0]
        last_segment = segments[-1]

        airlines = list(dict.fromkeys(
            segment["airline"] for segment in segments
        ))

        flight: FlightOption = {
            "airline": ", ".join(airlines),
            "price": float(price),
            "departure_airport": first_segment["departure_airport"]["id"],
            "arrival_airport": last_segment["arrival_airport"]["id"],
            "stops": len(option.get("layovers", [])),
            "summary": (
                f"Departs {first_segment['departure_airport']['time']}; "
                f"arrives {last_segment['arrival_airport']['time']}."
            ),
            "booking_hint": results.get("search_metadata", {}).get(
                "google_flights_url", ""
            ),
        }
        if option.get("departure_token"):
            flight["departure_token"] = option["departure_token"]

        flight_options.append(flight)

    return Command(
        update={
            "flights": flight_options,
            "return_flights": [],
            "selected_outbound_index": 0,
            "messages": [
                ToolMessage(
                    content=json.dumps(flight_options),
                    tool_call_id=runtime.tool_call_id,
                )
            ],
        }
    )

@tool
def search_return_flights(
    departure_city: str,
    destination: str,
    start_date: str,
    num_travelers: int,
    end_date: str,
    outbound_index: int,
    runtime: ToolRuntime
) -> Command:
    """Find return choices for an outbound option stored in state."""
    outbound = runtime.state["flights"][outbound_index]
    departure_token = outbound.get("departure_token")
    if not departure_token:
        raise ValueError("Selected outbound flight has no departure token.")

    client = serpapi.Client(api_key=flight_api_key)
    results = client.search({
        "engine": "google_flights",
        "departure_id": departure_city,
        "arrival_id": destination,
        "currency": "USD",
        "type": "1",
        "outbound_date": start_date,
        "return_date": end_date,
        "adults": num_travelers,
        "departure_token": departure_token,
        })
    if results.get("error"):
            raise ValueError(results["error"])
    
    raw_options = (
            results.get("best_flights", [])
            + results.get("other_flights", [])
    )
    
    return_flight_options: list[ReturnFlightOption] = []
    
    for option in raw_options:
            segments = option.get("flights", [])
            price = option.get("price")
    
            if not segments or price is None:
                continue
    
            first_segment = segments[0]
            last_segment = segments[-1]
    
            airlines = list(dict.fromkeys(
                segment["airline"] for segment in segments
            ))
    
            flight: ReturnFlightOption = {
                "airline": ", ".join(airlines),
                "price": float(price),
                "departure_airport": first_segment["departure_airport"]["id"],
                "arrival_airport": last_segment["arrival_airport"]["id"],
                "stops": len(option.get("layovers", [])),
                "summary": (
                    f"Departs {first_segment['departure_airport']['time']}; "
                    f"arrives {last_segment['arrival_airport']['time']}."
                ),
                "booking_hint": results.get("search_metadata", {}).get(
                    "google_flights_url", ""
                ),

            }
            return_flight_options.append(flight)
    return Command(
            update={
                "return_flights": return_flight_options,
                "selected_outbound_index": 0,
                "messages": [
                    ToolMessage(
                        content=json.dumps(return_flight_options),
                        tool_call_id=runtime.tool_call_id,
                    )
                ],
            }
        )



tools = [search_flights, search_return_flights]
search_prompt = """
You search for flights using the search flights tool. You must use the tools to find flight options.

When flight search parameters are provided:
1. Call search_flights before answering.
2. Pass the supplied airport codes, dates, and traveler count unchanged.
3. Wait for the tool result before comparing flights.
4. If the tool returns no options, report that.

Do not invent flights, prices, or availability.
Do not book anything.
"""

search_flight_agent = create_agent(
    model=chat,
    tools=tools,
    system_prompt=search_prompt,
    state_schema=FlightState,
)

def flight_agent(state: PlannerState) -> dict:
    preferences = state["user_preferences"]
    params = convert_preferences_to_flight_params(preferences)

    task = state.get("flight_task", {})
    instructions = task.get("instructions", "Research flight options.")

    result = search_flight_agent.invoke({
        "user_preferences": preferences,
        "flights": [],
        "return_flights": [],
        "messages": [{
            "role": "user",
            "content": (
                f"{instructions}\n"
                f"Search using these parameters: {params.model_dump_json()}\n"
                f"Flight preferences: {preferences.get('flight_preferences', [])}"
            ),
        }],
    })

    return {"flights": result.get("flights", [])}


    

