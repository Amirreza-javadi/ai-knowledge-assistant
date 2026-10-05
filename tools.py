import requests
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
from sympy import sqrt, sin, cos, tan, log, pi, E
from langchain.tools import tool
from langchain_tavily import TavilySearch
from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()


search_tool = TavilySearch(max_results=1)


@tool
def calculator(expression: str) -> str:
    """
    Calculate a mathematical expression accurately.

    Use this tool whenever an exact mathematical calculation
    is required.

    Examples:
    - 15 / 100 * 850
    - 850 * (1 - 15 / 100)
    - sqrt(144)
    - 2^10
    - 25 * 4.8
    - (1200 - 350) / 5
    - sin(pi / 2)
    """

    transformations = standard_transformations + (
        implicit_multiplication_application,
        convert_xor,
    )

    allowed_symbols = {
        "sqrt": sqrt,
        "sin": sin,
        "cos": cos,
        "tan": tan,
        "log": log,
        "pi": pi,
        "e": E,
    }

    try:
        expression = expression.strip()

        if not expression:
            return "Error: empty expression."

        result = parse_expr(
            expression,
            local_dict=allowed_symbols,
            transformations=transformations,
            evaluate=True,
        )

        return str(result)

    except Exception as e:
        return f"Error: invalid mathematical expression: {e}"


@tool
def get_weather(city: str) -> str:
    """
    Get the current weather information for a given city.

    Args:
        city: The name of the city.
    """

    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=10
        ).json()

        if "results" not in geo:
            return "City not found."

        latitude = geo["results"][0]["latitude"]
        longitude = geo["results"][0]["longitude"]

        weather = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,"
                    "relative_humidity_2m,"
                    "wind_speed_10m"
                )
            },
            timeout=10
        ).json()

        current = weather["current"]

        return (
            f"Temperature: {current['temperature_2m']}°C\n"
            f"Humidity: {current['relative_humidity_2m']}%\n"
            f"Wind: {current['wind_speed_10m']} km/h"
        )

    except requests.RequestException as e:
        return f"Weather service error: {e}"

    except Exception as e:
        return f"Error getting weather: {e}"


@tool("date-time")
def date_time(location: str) -> str:
    """
    Returns the current date and time for a given city or timezone.

    Examples:
    - London
    - New York
    - Tokyo
    - Tehran
    - Baku
    - Europe/London
    - America/New_York
    - Asia/Tokyo
    """

    # Common city -> IANA timezone mappings
    timezones = {
        "london": "Europe/London",
        "new york": "America/New_York",
        "los angeles": "America/Los_Angeles",
        "chicago": "America/Chicago",
        "toronto": "America/Toronto",
        "vancouver": "America/Vancouver",
        "tehran": "Asia/Tehran",
        "baku": "Asia/Baku",
        "dubai": "Asia/Dubai",
        "riyadh": "Asia/Riyadh",
        "istanbul": "Europe/Istanbul",
        "paris": "Europe/Paris",
        "berlin": "Europe/Berlin",
        "rome": "Europe/Rome",
        "moscow": "Europe/Moscow",
        "tokyo": "Asia/Tokyo",
        "seoul": "Asia/Seoul",
        "beijing": "Asia/Shanghai",
        "shanghai": "Asia/Shanghai",
        "singapore": "Asia/Singapore",
        "sydney": "Australia/Sydney",
        "melbourne": "Australia/Melbourne",
        "delhi": "Asia/Kolkata",
        "mumbai": "Asia/Kolkata",
    }

    location_clean = location.strip().lower()

    # Accept either a city name or an IANA timezone directly
    timezone_name = timezones.get(location_clean, location.strip())

    try:
        tz = ZoneInfo(timezone_name)
    except Exception:
        return (
            f"Timezone or city '{location}' was not recognized. "
            "Please provide a city such as London, Tokyo, Tehran, or "
            "an IANA timezone such as Europe/London."
        )

    now = datetime.now(tz)

    return (
        f"Location: {location}\n"
        f"Date: {now.strftime('%Y-%m-%d')}\n"
        f"Time: {now.strftime('%H:%M:%S')}\n"
        f"Timezone: {now.tzname()}\n"
        f"UTC offset: {now.strftime('%z')}"
    )


def create_document_search_tool(retriever):

    @tool
    def document_search(query: str) -> str:
        """
        Search the knowledge base for information relevant
        to the user's question.
        """

        documents = retriever.invoke(query)

        if not documents:
            return "No relevant information was found in the knowledge base."

        results = []

        for i, doc in enumerate(documents, start=1):

            content = doc.page_content

            source = doc.metadata.get(
                "source",
                "Unknown source"
            )

            results.append(
                f"Document {i} "
                f"(Source: {source}):\n"
                f"{content}"
            )

        return "\n\n".join(results)

    return document_search


def create_url_reader(llm):
    """
    Creates a URL Reader tool that:
    1. Fetches a web page from a URL.
    2. Extracts the readable text.
    3. Sends the extracted text to the LLM.
    4. Returns a concise summary.
    """

    @tool("url_reader")
    def url_reader(url: str) -> str:
        """
        Reads a web page from the given URL and summarizes its content.

        Args:
            url: The URL of the web page to read and summarize.

        Returns:
            A concise summary of the web page.
        """

        try:
            response = requests.get(
                url,
                timeout=15,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove elements that are usually not part of the main content
            for tag in soup([
                "script",
                "style",
                "noscript",
                "nav",
                "footer",
                "header"
            ]):
                tag.decompose()

            text = soup.get_text(
                separator=" ",
                strip=True
            )

            if not text:
                return "Could not extract readable text from this URL."

            # Prevent extremely large pages from overwhelming the LLM
            max_chars = 20000
            text = text[:max_chars]

            prompt = f"""
You are a helpful article summarization assistant.

Read the following web page content and provide a clear, concise
summary of the most important information.

Focus on:
- The main topic
- Key points
- Important facts
- Main conclusions

Do not mention that you are summarizing extracted HTML.
Do not add information that is not present in the article.

Web page content:

{text}
"""

            result = llm.invoke(prompt)

            return result.content

        except requests.RequestException as e:
            return f"Error reading the URL: {e}"

        except Exception as e:
            return f"Error summarizing the URL content: {e}"

    return url_reader
