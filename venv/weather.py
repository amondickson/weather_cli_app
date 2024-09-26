import requests
from datetime import datetime, timedelta, timezone
import time
import colorama
from colorama import Fore, Style
from tabulate import tabulate
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize colorama
colorama.init(autoreset=True)

# Get the API key from the environment variables
API_KEY = os.getenv('API_KEY')
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

# Check if the API key exists
if API_KEY is None:
    print(f"{Fore.RED}Error: API key is missing. Please check your .env file.")
    exit()

# Global variable to track if the header has been displayed
header_displayed = False

def display_header():
    """Displays the header, only once."""
    global header_displayed
    if not header_displayed:
        print(Style.BRIGHT + Fore.CYAN + "=" * 50)
        print(Style.BRIGHT + Fore.YELLOW + " Welcome to the Weather App!")
        print(Style.BRIGHT + Fore.CYAN + "=" * 50)
        print(Style.BRIGHT + Fore.GREEN + "Get current weather data or a 5-day forecast")
        print(Style.BRIGHT + Fore.CYAN + "=" * 50 + "\n")
        header_displayed = True

def get_weather(city, units='metric'):
    """Fetches the current weather data for a given city."""
    url = f'{BASE_URL}?q={city}&appid={API_KEY}&units={units}'

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()

        if data.get("cod") != 200:
            print(f"{Fore.RED}Error: {data.get('message').capitalize()}")
            return

        # Extract weather data
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        weather_desc = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        timezone_offset = data['timezone']

        # Local time of the user
        local_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Convert UTC to local city time
        utc_time = datetime.now(timezone.utc)
        city_time = utc_time + timedelta(seconds=timezone_offset)
        formatted_city_time = city_time.strftime('%Y-%m-%d %H:%M:%S')

        # Sunrise and Sunset
        sunrise = time.strftime('%H:%M:%S', time.gmtime(data['sys']['sunrise'] + timezone_offset))
        sunset = time.strftime('%H:%M:%S', time.gmtime(data['sys']['sunset'] + timezone_offset))

        # Weather Table
        table_data = [
            [f"{Fore.YELLOW}Temperature", f"{Fore.CYAN}{temp}° ({'Celsius' if units == 'metric' else 'Fahrenheit'})"],
            [f"{Fore.YELLOW}Feels Like", f"{Fore.CYAN}{feels_like}°"],
            [f"{Fore.YELLOW}Weather", f"{Fore.CYAN}{weather_desc.capitalize()}"],
            [f"{Fore.YELLOW}Humidity", f"{Fore.CYAN}{humidity}%"],
            [f"{Fore.YELLOW}Wind Speed", f"{Fore.CYAN}{wind_speed} m/s"],
            [f"{Fore.YELLOW}Sunrise", f"{Fore.CYAN}{sunrise}"],
            [f"{Fore.YELLOW}Sunset", f"{Fore.CYAN}{sunset}"]
        ]

        # Display data
        print(f"\n{Fore.GREEN}Weather in {Fore.CYAN}{city.capitalize()}:")
        print(f"{Fore.YELLOW}Your local time: {local_time}")
        print(f"{Fore.YELLOW}Current time in {city.capitalize()}: {formatted_city_time}")
        print(tabulate(table_data, headers=[f"Metric", f"Value"], tablefmt="fancy_grid"))

        return table_data, formatted_city_time

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            print(f"{Fore.RED}Error: City not found. Please enter a valid city name.")
        else:
            print(f"{Fore.RED}HTTP error occurred: {http_err}")
    except requests.exceptions.Timeout:
        print(f"{Fore.RED}Error: The request timed out. Please try again later.")
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}Error: Network connection error. Please check your internet connection.")
    except Exception as err:
        print(f"{Fore.RED}An error occurred: {err}")

def get_forecast(city, units='metric'):
    """Fetches a 5-day weather forecast for a given city."""
    forecast_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={units}'

    try:
        response = requests.get(forecast_url, timeout=5)
        response.raise_for_status()

        data = response.json()

        if data.get("cod") != '200':
            print(f"{Fore.RED}Error: {data.get('message').capitalize()}")
            return

        print(f"\n{Fore.GREEN}5-Day Weather Forecast for {Fore.CYAN}{city.capitalize()}:")
        forecast_table = []
        for forecast in data['list'][:5]:
            date_time = forecast['dt_txt']
            temp = forecast['main']['temp']
            weather_desc = forecast['weather'][0]['description']
            forecast_table.append([date_time, f"{temp}°", weather_desc.capitalize()])

        print(tabulate(forecast_table, headers=[f"Date & Time", f"Temperature", f"Weather"], tablefmt="fancy_grid"))

    except requests.exceptions.HTTPError as http_err:
        print(f"{Fore.RED}HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"{Fore.RED}An error occurred: {err}")

def get_units():
    """Ask the user to choose between metric or imperial units."""
    while True:
        unit_choice = input("Choose units (1 for Metric (Celsius), 2 for Imperial (Fahrenheit)): ")
        if unit_choice == '1':
            return 'metric'
        elif unit_choice == '2':
            return 'imperial'
        else:
            print(f"{Fore.RED}Invalid choice, please enter 1 or 2.")

def get_weather_option():
    """Ask the user if they want to see current weather or forecast."""
    while True:
        choice = input("Would you like to see the (1) Current Weather or (2) 5-Day Forecast? Enter 1 or 2: ")
        if choice == '1':
            return 'current'
        elif choice == '2':
            return 'forecast'
        else:
            print(f"{Fore.RED}Invalid choice, please enter 1 or 2.")

def save_to_file(city, table_data, formatted_city_time):
    """Saves the weather data to a file."""
    with open(f"{city}_weather.txt", "w") as file:
        file.write(f"Weather in {city.capitalize()} as of {formatted_city_time}\n")
        file.write(tabulate(table_data, headers=["Metric", "Value"], tablefmt="plain"))
    print(f"{Fore.GREEN}Weather data saved to {city}_weather.txt")

if __name__ == '__main__':
    while True:
        # Display the header only once
        display_header()

        city = input('Enter city name or country name(or type "exit" to quit): ').strip()
        if city.lower() == 'exit':
            break

        # Get unit preference (metric/imperial)
        units = get_units()

        # Get the weather option (current or forecast)
        weather_option = get_weather_option()

        if weather_option == 'current':
            table_data, formatted_city_time = get_weather(city, units)
        elif weather_option == 'forecast':
            get_forecast(city, units)

        # Ask if the user wants to save the data to a file
        save_option = input("Would you like to save this weather info to a file? (y/n): ").strip().lower()
        if save_option == 'y' and weather_option == 'current':
            save_to_file(city, table_data, formatted_city_time)

        print("\n" + Fore.CYAN + "=" * 40 + "\n")
