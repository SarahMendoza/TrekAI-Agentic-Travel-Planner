
from agents.flight_agent import recieve_flight_preferences
from agents.hotel_agent import hotel_agent



def handoff_to_subagents(trip_request):
    # Placeholder for the logic to hand off the trip_request to subagents
    print("Handoff to subagents with trip request:", trip_request)

    flight_options = recieve_flight_preferences(trip_request)
    print("\n\nFlight options received from flight agent:", flight_options)

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
    #get_hotel_preferences(**hotel_preferences)


    hotel_options = hotel_agent(trip_request)
    print("\n\nHotel options received from flight agent:", hotel_options)

    return {"flights": flight_options, "hotels": hotel_options}
    #return { "hotels": hotel_options}
    # return { "flights": flight_options}



   



