from application.agents.chat_agent import collect_trip_preferences
from application.agents.routing_agent import handoff_to_subagents

trip_request = collect_trip_preferences()

handoff_to_subagents(trip_request)

