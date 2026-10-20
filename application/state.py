from typing import Literal, NotRequired, TypedDict

SearchTarget = Literal["flight", "hotel", "activities"]
WorkflowStatus = Literal[
	"preferences_collected",
	"research_routing_complete",
	"itinerary_ready",
	"awaiting_user_approval",
	"needs_revision",
	"complete",
]

ALL_TARGETS = ["flights", "hotels", "activities"]


class Message(TypedDict):
	role: Literal["system", "user", "assistant"]
	content: str


class UserPreferences(TypedDict, total=False):
	origin_city: str
	destination_city: str
	start_date: str
	end_date: str
	budget_total: float
	travelers: int
	activity_types: list[str]
	hotel_preferences: list[str]
	flight_preferences: list[str]


class SearchTask(TypedDict):
	target: SearchTarget
	instructions: str
	filters: dict[str, object]


# consider adding unique ID's for each option, s.t. it's easier to prune state options once the user has approved
class FlightOption(TypedDict):
	airline: str
	price: float
	departure_airport: str
	arrival_airport: str
	stops: int
	summary: str
	booking_hint: str
	departure_token: NotRequired[str] 


class HotelOption(TypedDict):
	name: str
	price_total: float
	neighborhood: str
	amenities: list[str]
	summary: str


class ActivityOption(TypedDict):
	name: str
	category: str
	estimated_cost: float
	day: str
	summary: str


class ApprovalState(TypedDict, total=False):
	flights_approved: bool
	hotels_approved: bool
	activities_approved: bool


class PlannerState(TypedDict, total=False):
	messages: list[Message]
	user_preferences: UserPreferences
	approvals: ApprovalState
	user_feedback: str
	flight_task: SearchTask
	hotel_task: SearchTask
	activities_task: SearchTask
	pending_research: list[SearchTarget]
	flights: list[FlightOption]
	return_flights: list[FlightOption]
	hotels: list[HotelOption]
	activities: list[ActivityOption]
	itinerary_markdown: str
	final_response: str
	status: WorkflowStatus
