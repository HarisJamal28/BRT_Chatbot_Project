import os
import json
from openai_services import call_openai
from chromadb_BRT import retriever, load_brt_data
from brt_mongo import save_chat, fetch_chat
import time 
from difflib import get_close_matches

PROMPT = """
You are a friendly and helpful Bus Route Assistant with two main roles:
1. **Providing Bus Route Information**: You can assist with details about bus routes, including:
   - Route numbers and names.
   - Stops along a route.
   - First and last bus timings.
   - Bus intervals.

2. **Casual Conversation**: You can engage in friendly conversation and respond naturally to common greetings and casual questions like:
   - "Hello, how are you?"
   - "What’s up?"
   - "Goodbye!"

**Instructions**:
- **For Casual Conversations**: When the user greets you or asks casual questions, always start by replying with a friendly tone, e.g., "Hello! How can I help you today?" or "I'm doing great, thanks for asking!"
  
- **For Bus Route Inquiries**: When the user asks a specific question about bus routes, provide concise information with route numbers, stops, first and last bus timings, and intervals.

- **For Ambiguities**: If the query is vague, politely ask the user for more details. For example, if they only mention a stop, ask them for the route number or a clearer description of their question.

- **Friendly Tone**: Always maintain a friendly and helpful tone, ensuring the user feels welcomed and comfortable.

**Conversation Flow**:
1. Start by asking: "What is the nearest Bus stop to you?"
2. Save the nearest stop as the "first stop".
3. Then ask: "Where do you need to go?"
4. Save the destination as the "second stop".
5. Provide the best route information based on the "first stop" and "second stop".
6. If the user asks for alternatives, provide alternative routes.

Make sure you pardon yourself from conversations that are not related to bus routes
"""

if not os.path.exists("./chromaDB"):
    print("ChromaDB not found. Loading bus route data.")
    load_brt_data()
else:
    print("ChromaDB already exists. Skipping data loading.")

def load_brt_data():
    try:
        with open("./brt_buses_data.json", "r") as file:
            data = json.load(file)
        print("Data loaded successfully.")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def process_query(query, routes_data):
    stop_names = []
    query_lower = query.lower()
    
    for route in routes_data:
        for stop in route['stops']:
            if stop.lower() in query_lower:
                stop_names.append(stop)
    
    if not stop_names:
        all_stops = {stop.lower(): stop for route in routes_data for stop in route['stops']}
        closest_matches = get_close_matches(query_lower, all_stops.keys(), n=1, cutoff=0.6)
        if closest_matches:
            stop_names.append(all_stops[closest_matches[0]])
    
    return stop_names

def recommend_route(start, end, routes_data):
    direct_routes = [route for route in routes_data if start in route['stops'] and end in route['stops']]
    
    if direct_routes:
        return direct_routes
    
    connected_routes = []
    for route in routes_data:
        if start in route['stops']:
            for connecting_route in routes_data:
                if route != connecting_route and end in connecting_route['stops']:
                    common_stops = set(route['stops']).intersection(connecting_route['stops'])
                    if common_stops:
                        connected_routes.append((route, connecting_route, common_stops))
    
    return connected_routes

def format_route(route, start, end):
    stops = route['stops']
    start_index = stops.index(start)
    end_index = stops.index(end)
    return f"Route {route['routeNumber']} - {route['routeName']}<br>Number of Stops: {end_index - start_index + 1}"

def format_connected_routes(route1, route2, common_stop):
    return (f"Board {route1['routeNumber']} - {route1['routeName']} and get off at {common_stop}.<br>"
            f"Then board {route2['routeNumber']} - {route2['routeName']} to reach your destination.<br>")

def brt_bot(question, user_id):
    history = fetch_chat(user_id)
    clean_history = []
    if len(history) > 0:
        for item in history:
            clean_history.append({
                "role": item["role"],
                "content": item["content"]
            })

    casual_keywords = ["hello", "hi", "how are you", "what’s up", "goodbye"]
    if any(keyword in question.lower() for keyword in casual_keywords):
        return "Hello! Any idea where u want to take a Bus to today?"

    off_topic_keywords = ["weather", "sports", "news", "jokes", "games"]
    if any(keyword in question.lower() for keyword in off_topic_keywords):
        return ("I’d love to chat about those, but I’m here to help you with bus routes!<br>"
                "Please let me know if you have any questions about our routes or bus timings.")

    all_routes_data = load_brt_data()

    if all_routes_data is None:
        return "Sorry, we encountered an issue loading the bus route data. Please try again later."

    if "What is the nearest Bus stop to you?" not in [msg['content'] for msg in clean_history if msg['role'] == 'assistant']:
        save_chat(user_id, "assistant", "What is the nearest Bus stop to you?")
        return "What is the nearest Bus stop to you?"

    if "Where do you need to go?" not in [msg['content'] for msg in clean_history if msg['role'] == 'assistant']:
        nearest_stop = process_query(question, all_routes_data)
        if nearest_stop:
            save_chat(user_id, "user", f"Start: {nearest_stop[0]}")
            save_chat(user_id, "assistant", "Where do you need to go?")
            return "Where do you need to go?"

    alt_keywords = ["alternative", "another", "different", "other"]
    if any(keyword in question.lower() for keyword in alt_keywords):
        start = next((msg['content'].replace("Start: ", "") for msg in clean_history if msg['content'].startswith("Start: ")), None)
        end = next((msg['content'].replace("End: ", "") for msg in clean_history if msg['content'].startswith("End: ")), None)
        if start and end:
            best_routes = recommend_route(start, end, all_routes_data)
            if best_routes:
                response = "Here are some alternative routes you can take:<br>"
                for route in best_routes:
                    if isinstance(route, tuple): 
                        for common_stop in route[2]:
                            response += format_connected_routes(route[0], route[1], common_stop)
                    else:
                        response += format_route(route, start, end) + "<br><br>"
                return response
            else:
                return f"Sorry, I couldn't find any alternative routes from {start} to {end}. Could you please provide more details?"

    start = next((msg['content'].replace("Start: ", "") for msg in clean_history if msg['content'].startswith("Start: ")), None)
    if start:
        destination_stop = process_query(question, all_routes_data)
        if destination_stop:
            end = destination_stop[0]
            save_chat(user_id, "user", f"End: {end}")
            best_routes = recommend_route(start, end, all_routes_data)
            if best_routes:
                suggested_routes = set()
                response = f"The best routes from {start} to {end} are:<br>"
                for route in best_routes:
                    if isinstance(route, tuple): 
                        for common_stop in route[2]:
                            response += format_connected_routes(route[0], route[1], common_stop)
                            suggested_routes.add((route[0]['routeNumber'], route[1]['routeNumber']))
                    else:
                        response += format_route(route, start, end) + "<br><br>"
                        suggested_routes.add(route['routeNumber'])
                
                save_chat(user_id, "assistant", response)
                save_chat(user_id, "suggested_routes", json.dumps(list(suggested_routes)))
                return response
            else:
                return f"Sorry, I couldn't find a direct route from {start} to {end}. Could you please provide more details?"
        else:
            return "Sorry, I couldn't find any stops matching your query. Could you please provide more details?"

    return "Sorry, I couldn't understand your request. Please try again."

if __name__ == "__main__":
    while True:
        question = input("Inquire about a Bus Route (or type 'exit' to quit): ")
        if question.lower() == "exit":
            break
        response = brt_bot(question, "myaccount")
        print("\nAssistant:", response, "\n")