

from agents.hotel_agent import hotel_agent

from state import ApprovalState, PlannerState


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




   



