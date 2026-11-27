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
- Budget and currency

Also ask about interests, preferred pace, lodging or flight preferences,
and dietary or accessibility needs when relevant. 

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
REQUIRED_FIELDS = (
    "origin_city",
    "destination_city",
    "start_date",
    "end_date",
    "travelers",
    "budget_total",
)


def chat_agent(state: PlannerState) -> dict:
    messages = state.get("messages", [])

    if not messages or messages[-1]["role"] != "user":
        raise ValueError("chat_agent expects the latest message to be from the user")

    user_text = messages[-1]["content"].strip()
    status = state.get("status")

    # The previous turn asked the user to confirm the extracted preferences.
    if status == "awaiting_preferences_confirmation":
        if user_text.lower() in {"yes", "y"}:
            reply = "Trip details confirmed. I'll start planning."
            return {
                "messages": messages + [
                    {"role": "assistant", "content": reply}
                ],
                "status": "preferences_collected",
            }

        if user_text.lower() in {"no", "n"}:
            reply = "What would you like to change?"
            return {
                "messages": messages + [
                    {"role": "assistant", "content": reply}
                ],
                "status": "collecting_preferences",
            }
        # Otherwise, treat this message as a correction and extract again.

    # Extract from user messages so assistant suggestions cannot become facts.
    transcript = "\n".join(
        message["content"]
        for message in messages
        if message["role"] == "user"
    )

    extracted = extraction_chain.invoke({"transcript": transcript})
    preferences = extracted["parsed"]

    if preferences is None:
        reply = "I had trouble reading those details. Could you clarify?"
        return {
            "messages": messages + [
                {"role": "assistant", "content": reply}
            ],
            "status": "collecting_preferences",
        }

    missing = [
        field for field in REQUIRED_FIELDS
        if preferences.get(field) in (None, "")
    ]

    if not missing:
        reply = (
            f"Please confirm: travel from {preferences['origin_city']} "
            f"to {preferences['destination_city']} from "
            f"{preferences['start_date']} to {preferences['end_date']}, "
            f"for {preferences['travelers']} traveler(s), with a total "
            f"budget of {preferences['budget_total']}. Is that correct?"
        )
        new_status = "awaiting_preferences_confirmation"
    else:
        history = [
            HumanMessage(content=message["content"])
            if message["role"] == "user"
            else AIMessage(content=message["content"])
            for message in messages[:-1]
            if message["role"] in {"user", "assistant"}
        ]
        reply = chain.invoke({
            "history": history,
            "input": user_text,
        })
        new_status = "collecting_preferences"

    return {
        "messages": messages + [
            {"role": "assistant", "content": reply}
        ],
        "user_preferences": preferences,
        "status": new_status,
    }
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
