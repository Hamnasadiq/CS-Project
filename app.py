from dotenv import load_dotenv
import os
from langchain_core.tools import tool
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from io import BytesIO
from PIL import Image
from math import radians, sin, cos, sqrt, atan2
import streamlit as st
import shutil
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

#load environment variables from .env file
load_dotenv()

#accessing environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


@tool
def calculator(expression: str) -> float:
    """A calculator tool for evaluating complex arithmetic expression.
    This function evaluates a given arithmetic expression that can include
    addition, subtraction, division, and parantheses for grouping operations.

    Args:
    expression (str): The arithmetic expression to evaluate.

    Returns:
    str: A message containing the result of the calculation.

    Examples:
           calculator("2 + 5 * 5 - 10 * 50") -> "The result is -485"
           calculator("(2 + 5) * (5 - 10 * 50)") -> "The result is -2475"
       
 """
    print(f"Calculator tool called with expression: {expression}")
    try:
        # Use eval to evaluate the expression securely
        result = eval(expression, {"__builtins__": None}, {})
        return f"The result is {result}"
    except ZeroDivisionError:
        return "Error: Division by zero is not allowed."
    except Exception as e:
        return f"Error: Unable to perform the calculation. Details: {str(e)}"

@tool
def get_stock_price(symbol: str) -> str:
    """
    Fetches the current stock price of a company based on its stock symbol using the Alpha Vantage API.
    
    Args:
        symbol (str): The stock symbol of the company (e.g., 'AAPL' for Apple, 'GOOGL' for Google).
    
    Returns:
        str: A message containing the current stock price of the company.
    
    Raises:
        HTTPError: If the HTTP request to the stock API fails (e.g., 404 or 500 status).
    """
    API_KEY = "SQSMPCSA8M3LRN6F"
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        price = data["Global Quote"]["05. price"]
        return f"The current price of {symbol} is ${price}"
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as e:
        return f"Error fetching stock price: {e}"

@tool
def get_latest_news(topic: str) -> str:
    """
    Fetches the latest news for a given topic.
    
    Args:
        topic (str): The topic to search for news articles.
    
    Returns:
        str: A formatted string containing the tool name, the latest news titles, and their respective links.
    
    Example:
        >>> get_latest_news("Technology")
    """
    api_key = "654e605a0a674e6b8752c8de91652a44"  # Replace with your actual API key
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200 and data.get("articles"):
            articles = data["articles"]
            result = f"Tool used: get_latest_news tool is used \nHere are the latest news articles related to {topic}:\n"
            
            for article in articles[:5]:  # Limiting to 5 articles
                title = article["title"]
                url = article["url"]
                result += f"- {title}: ({url})\n"
            
            return result
        else:
            return f"Error: Could not fetch news on {topic}. Response: {data.get('message', 'Unknown error')}"
    except Exception as e:
        return f"Error fetching news: {e}"
    
@tool
def get_movie_details(movie_name: str) -> str:
    """
    Fetches movie details using the OMDb API.

    Args:
        movie_name (str): The name of the movie to search for.

    Returns:
        str: A message containing the movie details like title, year, genre, director, actors, and IMDb rating.

    Example:
        >>> get_movie_details("Inception")
    """
    API_KEY = "97f317ee"  # Replace with your actual OMDb API key
    url = f"http://www.omdbapi.com/?t={movie_name}&apikey={API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if data["Response"] == "True":
            title = data.get("Title", "N/A")
            year = data.get("Year", "N/A")
            genre = data.get("Genre", "N/A")
            director = data.get("Director", "N/A")
            actors = data.get("Actors", "N/A")
            plot = data.get("Plot", "N/A")
            imdb_rating = data.get("imdbRating", "N/A")

            return (f"🎬 **Movie Details:**\n"
                    f"- **Title:** {title}\n"
                    f"- **Year:** {year}\n"
                    f"- **Genre:** {genre}\n"
                    f"- **Director:** {director}\n"
                    f"- **Actors:** {actors}\n"
                    f"- **IMDb Rating:** {imdb_rating}\n"
                    f"- **Plot:** {plot}")
        else:
            return f"❌ Error: Movie '{movie_name}' not found!"

    except requests.exceptions.RequestException as e:
        return f"❌ Error: Failed to fetch movie details. Details: {e}"


@tool
def get_recipe_details(recipe_name: str) -> str:
    """
    Fetches recipe details using the Spoonacular API.

    Args:
        recipe_name (str): The name of the recipe to search for.

    Returns:
        str: A message containing recipe details like title, ingredients, and instructions.

    Example:
        >>> get_recipe_details("Pasta")
    """
    API_KEY = "47ede17dacf34cc8bf822fa8a13d971f"  # Replace with your actual API key
    url = f"https://api.spoonacular.com/recipes/complexSearch?query={recipe_name}&number=1&apiKey={API_KEY}"

    try:
        response = requests.get(url)
        data = response.json()

        if "results" in data and data["results"]:
            recipe_id = data["results"][0]["id"]
            recipe_title = data["results"][0]["title"]

            # Fetch detailed recipe info
            details_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}"
            details_response = requests.get(details_url)
            details_data = details_response.json()

            ingredients = [ingredient["original"] for ingredient in details_data.get("extendedIngredients", [])]
            instructions = details_data.get("instructions", "No instructions available.")

            return (f"🍽 **Recipe Details:**\n"
                    f"- **Title:** {recipe_title}\n"
                    f"- **Ingredients:**\n  " + "\n  ".join(ingredients) + "\n"
                    f"- **Instructions:** {instructions}")
        else:
            return f"❌ Error: Recipe '{recipe_name}' not found!"

    except requests.exceptions.RequestException as e:
        return f"❌ Error: Failed to fetch recipe details. Details: {e}"


API_KEY = "7195231e-6c04-4680-b68a-9049118d692e"  # Replace with your OpenCage API key

@tool
def get_distance(location1: str, location2: str) -> str:
    """
    Calculates the distance between two locations using the OpenCage Geocoder API.

    Args:
        location1 (str): The first location (e.g., "New York").
        location2 (str): The second location (e.g., "Los Angeles").

    Returns:
        str: A message containing the calculated distance in kilometers between the two locations.

    Raises:
        Exception: If either location is invalid or the API requests fail.
    """

    def get_coordinates(location):
        url = f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={API_KEY}"
        response = requests.get(url).json()
        if response["results"]:
            lat = response["results"][0]["geometry"]["lat"]
            lon = response["results"][0]["geometry"]["lng"]
            return lat, lon
        else:
            raise ValueError(f"Invalid location: {location}")

    try:
        lat1, lon1 = get_coordinates(location1)
        lat2, lon2 = get_coordinates(location2)

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula to calculate the distance
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        R = 6371  # Radius of Earth in kilometers
        distance = R * c

        return f"The distance between {location1} and {location2} is approximately {distance:.2f} km."
    except Exception as e:
        return str(e)
PEXELS_API_KEY = "zePpbhcXNFk7AKvFBuu7jMQy4S8vhkRBhQeGU28ul0zsoN5xsx9cYIcL"  # Replace with your actual API key
PEXELS_API_URL = "https://api.pexels.com/v1/search"
@tool
def get_ip_address(ip: str) -> str:
    """Fetches details about a given IP address."""
    url = f"http://ip-api.com/json/{ip}"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "fail":
        return "Invalid IP Address or API limit exceeded."
    
    return f"""
    IP Address: {data['query']}
    Country: {data['country']}
    Region: {data['regionName']}
    City: {data['city']}
    ISP: {data['isp']}
    Latitude: {data['lat']}
    Longitude: {data['lon']}
    """
@tool
def get_disk_usage():
    """Retrieves disk usage.

    This function provides the disk usage statistics such as total, used, and free disk space.

    Args:
        None

    Returns:
        str: A formatted string containing disk usage statistics with the total, used, and free disk space.
    """
    path = "/"
    total, used, free = shutil.disk_usage(path)
    gb = 1024 * 1024 * 1024

    return (f"Total Disk Space: {total / gb:.2f} GB\n"
            f"Used Disk Space: {used / gb:.2f} GB\n"
            f"Free Disk Space: {free / gb:.2f} GB")
@tool
def get_time_in_timezone(timezone_name: str) -> str:
    """Returns the current time for a given timezone.

    This function fetches the current time for a specific timezone based on the provided IANA timezone name.

    Args:
        timezone_name (str): The IANA timezone name (e.g., 'America/New_York')

    Returns:
        str: Current time in the specified timezone (get_time_in_timezone tool is used )
    """
    try:
        current_time = datetime.now(ZoneInfo(timezone_name))
        return current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
    except Exception as e:
        return f"Error: Invalid timezone: {str(e)}"



country_cities = {
    "Pakistan": ["Karachi", "Lahore", "Islamabad", "Quetta", "Peshawar"],
    "USA": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
    "India": ["Mumbai", "Delhi", "Bangalore", "Kolkata", "Chennai"],
    # Add more countries and their major cities here
}

@tool
def get_weather(location_name: str, is_city: bool = False) -> str:
    """Fetches the current weather for a given location (country or city). If a country is queried, includes weather for major cities.

    Args:
        location_name (str): The name of the location (country or city) for which to fetch the weather.
        is_city (bool, optional): Boolean indicating if the location is a city. Default is False.

    Returns:
        str: A description of the current weather, temperature, and other details.
    """
    try:
        global last_country
        api_key = "e0f48608aef2cf6c4dd18acfaf37f3b8"  # Replace with your OpenWeatherMap API key

        # Fetch country weather
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location_name}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            weather = data["weather"][0]["description"].capitalize()
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            result = (
                f"The current weather in {location_name} is {weather} with a temperature "
                f"of {temp}°C and feels like {feels_like}°C.\n get_weather tool is used "
            )

            # Fetch major cities' weather if the location is a country
            if not is_city and location_name in country_cities:
                last_country = location_name
                result += "\nMajor cities' weather:\n"
                for city in country_cities[location_name]:
                    city_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
                    city_response = requests.get(city_url)
                    city_data = city_response.json()

                    if city_response.status_code == 200:
                        city_weather = city_data["weather"][0]["description"].capitalize()
                        city_temp = city_data["main"]["temp"]
                        city_feels_like = city_data["main"]["feels_like"]
                        result += (
                            f"- {city}: {city_weather}, {city_temp}°C (feels like {city_feels_like}°C)\n"
                        )
                    else:
                        result += f"- {city}: Weather data unavailable.\n"

            # Append tool usage info
            result += "\nTool used: get_weather"
            return result
        else:
            return f"Error: Could not retrieve weather data. Reason: {data.get('message', 'Unknown error')}."
    except Exception as e:
        return f"Error: Unable to fetch weather. Details: {str(e)}"

@tool
def llm_fallback(query: str):
    """Handles queries when no specific tool is available.

    Args:
        query (str): The input query for which no tool exists.

    Returns:
        str: A generated response from the LLM.
    """

    # Generate response using LLM
    response = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        api_key="AIzaSyDlGuiJOqQePVsQEu5gWiftb74RDGvcq"
    )
    
    reply = response


    return f"Tool used: llm_fallback\nllm_fallback tool is used to handle query: {query}\nResponse: {reply}"




@tool(parse_docstring=True)
def search_image(query: str):
    """Searches for images based on the query keyword.

    Args:
        query (str): The search query to find images.

    Returns:
        str: Displays images related to the search query.
    """
    api_key = "YcKCA72Ez-w6bn0jC03opmr4UtdeXlRccoHpOs4WygU"
    url = f"https://api.unsplash.com/search/photos?query={query}&client_id={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if data['results']:
        # Extract the image URLs from the response
        image_urls = [image['urls']['small'] for image in data['results'][:5]]
        
        # Display images in the Streamlit app
        for img_url in image_urls:
            st.image(img_url, caption=f"Image related to {query}", use_container_width=True)
        
        return f"Tool used: search_image\n search_image tool is used to  Displayed images related to {query}."
    else:
        return f"Error: Could not find images for {query}.\nTool used: search_image"



# Define tools (only tool names for sidebar)
tool_names = [
    "Calculator",
    "Stock Price",
    "Latest News",
    "Movie Details",
    "Recipe Details",
    "IP Address",
    "Check Distance",
    "Weather",
    "Get Time in Timezone",
    "Search Image",
    "LLM Fallback"
]

# Actual tool functions (Replace these with actual implementations)
tools = [
    calculator,
    get_stock_price,
    get_latest_news,
    get_movie_details,
    get_recipe_details,
    get_ip_address,
    get_distance,
    get_weather,
    get_time_in_timezone,
    search_image,
    llm_fallback
]

# Initialize AI model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", api_key=GOOGLE_API_KEY)

# Initialize agent
agent = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION)

# Set page config
st.set_page_config(page_title="AI Chatbot", page_icon="🤖", layout="wide")

# Custom CSS for improved styling
st.markdown(
    """
    <style>
        body {
            background-color: #1E1E1E;
            color: white;
        }
        .stApp {
            background-color: #1E1E1E;
        }
        .sidebar .sidebar-content {
            background-color: #111;
            color: white;
            padding: 20px;
        }
        .sidebar .sidebar-content h2 {
            color: #FFA500;
        }
        .sidebar .sidebar-content ul {
            list-style-type: none;
            padding: 0;
        }
        .sidebar .sidebar-content ul li {
            padding: 8px;
            border-radius: 5px;
            margin-bottom: 5px;
            background: #222;
            text-align: left;
        }
        .sidebar .sidebar-content ul li:hover {
            background: #333;
            cursor: pointer;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            width: 100%;
            font-weight: bold;
        }
        .stTextInput>div>div>input {
            background-color: #333;
            color: white;
            border-radius: 10px;
            padding: 8px;
        }
        .main-content {
            text-align: center;
            padding-top: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar with only tool names
with st.sidebar:
    st.markdown("🔧 **Available Tools**", unsafe_allow_html=True)
    st.markdown("<ul>", unsafe_allow_html=True)
    for tool in tool_names:
        st.markdown(f"<li>{tool}</li>", unsafe_allow_html=True)
    st.markdown("</ul>", unsafe_allow_html=True)

# Main Chatbot UI
st.markdown("<div class='main-content'><h1>🤖 AI Chatbot</h1></div>", unsafe_allow_html=True)
st.write("This chatbot can help you with various tasks. Ask anything and it will assist you.")

# User input
user_input = st.text_input("Ask anything")

if st.button("Submit"):
    response = agent.invoke(user_input)
    st.write(response["output"])