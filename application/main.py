import sys
from typing import Literal

from langgraph.graph import END, START, StateGraph

# from agents.activities_agent import activities_agent
# from agents.chat_agent import chat_agent
# from agents.flight_agent import flight_agent
# from agents.hotel_agent import hotel_agent
# from agents.planner_agent import planner_agent
# from application.agents.routing_agent import routing_agent
# from application.state import ALL_TARGETS, PlannerState

# preserved code from Zion's main.py
from agents.chat_agent import collect_trip_preferences
from agents.routing_agent import handoff_to_subagents
# from application.agents.routing_agent import handoff_to_subagents

trip_request = collect_trip_preferences()


handoff_to_subagents(trip_request)



# def after_chat_condition(state: PlannerState) -> Literal["routing_agent", END]:
#     if state.get("status") == "complete":
#         return END
#     return "routing_agent"


# def which_subagents_condition(state: PlannerState) -> list[str]:
#     node_for = {"flights": "flight_agent", "hotels": "hotel_agent", "activities": "activities_agent"}
#     pending = [t for t in ALL_TARGETS if t not in state.get("approved", [])]
#     return [node_for[t] for t in pending] or ["planner_agent"]


# builder = StateGraph(PlannerState)
# builder.add_node("chat_agent", chat_agent)
# builder.add_node("routing_agent", routing_agent)
# builder.add_node("flight_agent", flight_agent)
# builder.add_node("hotel_agent", hotel_agent)
# builder.add_node("activities_agent", activities_agent)
# builder.add_node("planner_agent", planner_agent)

# builder.add_edge(START, "chat_agent")
# builder.add_conditional_edges("chat_agent", after_chat_condition)
# builder.add_conditional_edges(
#     "routing_agent",
#     which_subagents_condition,
#     ["flight_agent", "hotel_agent", "activities_agent", "planner_agent"],
# )
# builder.add_edge("flight_agent", "planner_agent")
# builder.add_edge("hotel_agent", "planner_agent")
# builder.add_edge("activities_agent", "planner_agent")
# builder.add_edge("planner_agent", "chat_agent")

# graph = builder.compile()


# if __name__ == "__main__":
#     if "--draw" in sys.argv:
#         with open("trekai_graph.png", "wb") as f:
#             f.write(graph.get_graph().draw_mermaid_png())
#         print("Saved trekai_graph.png")
#     else:
#         print(graph.invoke({}))


