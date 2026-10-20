# TrekAI-Agentic-Travel-Planner

File Structure:

```text
TrekAI-Agentic-Travel-Planner/
├── README.md
├── langgraph.json
├── requirements.txt
└── application/
	├── api_tools.md
	├── main.py
	├── state.py
	├── agents/
	│   ├── activities_agent.py
	│   ├── chat_agent.py
	│   ├── flight_agent.py
	│   ├── hotel_agent.py
	│   ├── hotel_agent2.py
	│   ├── planner_agent.py
	│   └── routing_agent.py
	└── tools/
		└── tools.py
```



Application Functional Outline:

**chat_agent** -- receives information from user about their desired vacation (dates, destination, activies type, flight and hotel preferences)

**routing_agent** -- receives structured user preferences from the chat_agent, and reviews it. Creates instructions for the sub-agents (flight_agent, hotel_agent, and activities_agent) with the desired outcomes of their corresponding web searches. Sends search instructions and requirements to sub-agents.

**flight_agent** -- receives user context and flight requirements. Search the internet or specific flight API's using the information as a filter. The flight agent finds relevant flights and formats them into the graph's context.

**hotel_agent** -- similar workflow to flight_agent. This is the dedicated sub-agent for researching hotels and lodging at the user's destination city.

**activities_agent** -- similar workflow to flight_agent. This is the dedicated sub-agent for researching activites, museums, food, and/or events at the user's destination city.

**planner_agent** -- receives possible trip flights, hotels, and activities options from each of the three sub-agents. Should only receive possible options that are both within the user's budget, at the destination city, and at least sensibly related to their preferences. This agent uses structured chain of thought reasoning to construct an itinerary from the information provided. It then formats the itinerary as a final output, and sends this output to the chat_agent.

**chat_agent** -- receives a completed itinerary and presents it to the user. If the user approves, then the task is completed and ends. If the user wants to change specific details then chat_agent receives and structures this feedback. The flights, hotels, and individual activities may each be approved or rejected independently to help the routing agent avoid re-routing completed tasks.