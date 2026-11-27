
from agents.flight_agent import recieve_flight_preferences

from state import ApprovalState, PlannerState

ALL_TARGETS = ("flights", "hotels", "activities")

from state import PlannerState, SearchTarget

ALL_TARGETS: tuple[SearchTarget, ...] = (
    "flight", "hotel", "activities"
)

APPROVAL_KEY = {
    "flight": "flights_approved",
    "hotel": "hotels_approved",
    "activities": "activities_approved",
}

TASK_KEY = {
    "flight": "flight_task",
    "hotel": "hotel_task",
    "activities": "activities_task",
}


def routing_agent(state: PlannerState) -> dict:
    approvals = state.get("approvals", {})
    feedback = state.get("user_feedback", "")

    pending = [
        target for target in ALL_TARGETS
        if approvals.get(APPROVAL_KEY[target]) is not True
    ]

    updates = {
        "pending_research": pending,
        "status": "research_routing_complete",
    }

    for target in pending:
        instructions = f"Research {target} options."
        if feedback:
            instructions += f" Consider this user feedback: {feedback}"

        updates[TASK_KEY[target]] = {
            "target": target,
            "instructions": instructions,
            "filters": {},
        }

    return updates

def handoff_to_subagents(trip_request):
    # Placeholder for the logic to hand off the trip_request to subagents
    print("Handoff to subagents with trip request:", trip_request)

    #

    flight_options = recieve_flight_preferences(trip_request)
    print("Flight options received from flight agent:", flight_options)

    # hotel_preferences = {
    #     "destination": trip_request.get("destination"),
    #     "travel_dates": trip_request.get("travel_dates"),
    #     "num_travelers": trip_request.get("num_travelers"),
    #     "budget": trip_request.get("budget"),
    #     "budget_scope": trip_request.get("budget_scope"),
    #     "currency": trip_request.get("currency"),
    #     "hotel_preferences": trip_request.get("hotel_preferences"),
    #     "interests": trip_request.get("interests"),
    # }


     # Placeholder for the logic to hand off hotel preferences to the hotel agent
    # get_hotel_preferences(**hotel_preferences)

    return {"flights": flight_options}



   



