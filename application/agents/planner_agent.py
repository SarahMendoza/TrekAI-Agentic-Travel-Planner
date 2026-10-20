from application.state import PlannerState


def planner_agent(state: PlannerState):
    print("...planner_agent...")
    return {"itinerary_markdown": "# Stub itinerary", "status": "reviewing"}