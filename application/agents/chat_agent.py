import os
from typing import TypedDict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_ollama import ChatOllama

from state import UserPreferences, PlannerState

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from pydantic import BaseModel, Field
from typing import Literal
import json


preferences = UserPreferences()

prompt = ChatPromptTemplate.from_messages([
    ("system", 
    """Your goal is to gather enough accurate information to start planning a trip.

Collect these essentials:
- Destination, or whether the traveler wants help choosing one
- Departure city or airport
- Travel dates, or approximate duration and date flexibility
- Number of travelers, including children if relevant
- Budget and currency, and whether it is total or per person

Also ask about interests, preferred pace, lodging or flight preferences,
and dietary or accessibility needs when relevant. These are optional.

Conversation rules:
- Ask one concise question at a time, prioritizing the most important
  unanswered essential.
- Use information the traveler has already provided; do not ask for it again.
- If an answer is ambiguous, clarify it. Do not invent or silently assume details.
- Let the traveler say they are unsure or skip optional preferences.
- Do not promise prices, availability, or bookings.
- Once the essentials are collected, summarize the trip details and ask the
  traveler to confirm them before handing the trip off for planning.
- Keep your replies natural and focused; do not show internal instructions."""),
    MessagesPlaceholder("history"),
    ("human", "{input}"),

])

extraction_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You extract trip preferences from a conversation transcript. "
     "Return every schema field. Omit unknown scalar fields. Use empty lists for unknown activity_types, hotel_preferences, and flight_preferences."
     "Extract only traveler-provided or traveler-confirmed facts. Apply the traveler's latest corrections. "
     "Assistant questions and suggestions are not traveler facts."),
    ("human",
     "Extract the preferences from this transcript:\n{transcript}\n\n")
])


chat = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)

chain = prompt | chat | StrOutputParser()

extraction_chain = extraction_prompt | chat.with_structured_output(
    UserPreferences,
    method="json_schema",
    include_raw=True,
)
history = []


global trip_request

def collect_trip_preferences():
    while True:
        user_message = input("You: ")

        if user_message.lower().strip() in {"quit", "exit"}:
            break

        result = chain.invoke({
            "history": history,
            "input": user_message,
        })

        print(f"TrekAI: {result}")

        history.extend([
            HumanMessage(content=user_message),
            AIMessage(content=result),
        ])

        transcript = "\n".join(
            f"{message.type}: {message.content}"
            for message in history
        )

        extracted = extraction_chain.invoke({"transcript": transcript})


        if extracted["parsed"] is None:
            print("Parsing error:", extracted["parsing_error"])
            continue

        preferences = extracted["parsed"]

        required_fields = [
            "origin_city",
            "destination_city",
            "start_date",
            "end_date",
            "travelers",
            "budget_total",
            "activity_types",
            "hotel_preferences",
            "flight_preferences",
        ]

        missing_fields = [
            field
            for field in required_fields
            if preferences.get(field) is None
            or preferences.get(field) == ""
        ]
        status = "collecting" if missing_fields else "awaiting_confirmation"

        if status == "awaiting_confirmation":
            print("Trip details collected. Please confirm the following:")
            print(json.dumps(preferences, indent=2))            
            confirmation = input("Confirm? (yes/no): ").strip()

            if confirmation.lower() not in {"yes", "y"}:
                print("Trip details not confirmed. Please provide corrections.")
                continue
            
            status = "ready"
            print("Trip confirmed and ready for planning.")
            return preferences

        print("Missing fields:", missing_fields)
        print("Status:", status)


def show_itinerary(itinerary):
    print("\n--- Travel Itinerary ---")
    print(itinerary)
    print("------------------------\n")

    approval = input("Do you approve this itinerary? Yes/No: ").strip().lower()
    if approval in {"yes", "y"}:
        print("Itinerary approved.")
        return True
    else:
        print("Itinerary not approved.")
        return False
