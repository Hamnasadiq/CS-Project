from dotenv import load_dotenv
import os
from langchain_core.tools import tool
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import initialize_agent,AgentType
import streamlit as st
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

tools=[calculator,get_stock_price,get_latest_news]

llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp",api_key=GOOGLE_API_KEY)



agent=initialize_agent(tools,llm,agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION)

st.title("AI Chatbot")
st.write("This is a chatbot that can perform calculations, fetch stock prices, and provide the latest news on a given topic")
user_input = st.text_input("Enter your prompt")


if st.button("Submit"):
    response=agent.invoke(user_input)
    st.write(response["output"])