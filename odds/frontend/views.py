from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import redirect
import os, shutil
import time
from django.http import JsonResponse
from django.conf import settings
import re
import requests
from datetime import date

# Create your views here.
def index(request):
    # Replace 'YOUR_API_KEY' with your actual sportsdata.io API key
    api_key = "c771eda3c44b47de9f2d6848bfb29824"
    # Get today's date in 'YYYY-MM-DD' format
    today_date = date.today().strftime('%Y-%m-%d')
    games_data = get_games_by_date(api_key, today_date)

    # Define an empty list to store the specific data for each game
    Final_data = []
    abbreviations_team = {
        "ARI": "Arizona Diamondbacks",
        "ATL": "Atlanta Braves",
        "BAL": "Baltimore Orioles",
        "BOS": "Boston Red Sox",
        "CHC": "Chicago Cubs",
        "CHW": "Chicago White Sox",
        "CIN": "Cincinnati Reds",
        "CLE": "Cleveland Indians",
        "COL": "Colorado Rockies",
        "DET": "Detroit Tigers",
        "FLA": "Florida Marlins",
        "HOU": "Houston Astros",
        "KAN": "Kansas City Royals",
        "LAA": "Los Angeles Angels of Anaheim",
        "LAD": "Los Angeles Dodgers",
        "MIL": "Milwaukee Brewers",
        "MIA": "Miami Marlins",
        "MIN": "Minnesota Twins",
        "NYM": "New York Mets",
        "NYY": "New York Yankees",
        "OAK": "Oakland Athletics",
        "PHI": "Philadelphia Phillies",
        "PIT": "Pittsburgh Pirates",
        "SD": "San Diego Padres",
        "SF": "San Francisco Giants",
        "SEA": "Seattle Mariners",
        "STL": "St. Louis Cardinals",
        "TB": "Tampa Bay Rays",
        "TEX": "Texas Rangers",
        "TOR": "Toronto Blue Jays",
        "WSH": "Washington Nationals"
    }
    if games_data:
        for game in games_data:
            game_id = game["GameID"]
            home_team = abbreviations_team.get(game["HomeTeam"])
            away_team = abbreviations_team.get(game["AwayTeam"])
            status = game["Status"]
            datetime = game["DateTime"]
            home_moneyline = game.get("HomeTeamMoneyLine", "N/A")
            away_moneyline = game.get("AwayTeamMoneyLine", "N/A")

            # Create a dictionary with the specific data for the current game
            todays_data = {
                "Game_ID": game_id,
                "Status": status,
                "Date_and_Time": datetime,
                "Home_Team": home_team,
                "Away_Team": away_team,
                "Home_Team_Money_Line": home_moneyline,
                "Away_Team_Money_Line": away_moneyline
            }

            # Append the dictionary to the specific_game_data_list
            Final_data.append(todays_data)
    context_dict = {"Final_data": Final_data}
    return render(request, 'odds/home.html', context_dict)

def get_games_by_date(api_key, date_str):
    base_url = "https://api.sportsdata.io/v3/mlb/scores/json/GamesByDate/"
    url = base_url + date_str
    headers = {"User-Agent": "YourApp", "Ocp-Apim-Subscription-Key": api_key}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        games_data = response.json()
        
        # Get odds data
        odds_url = f"https://api.sportsdata.io/v3/mlb/odds/json/GameOddsByDate/{date_str}?key={api_key}"
        odds_response = requests.get(odds_url)
        if odds_response.status_code == 200:
            odds_data = odds_response.json()
            
            # Add Home and Away moneyline to each game in games_data
            for game in games_data:
                game_id = game["GameID"]  # Corrected the key to "GameID"
                matching_odds = next((o for o in odds_data if o["GameId"] == game_id and o["PregameOdds"] and o["PregameOdds"][0]["SportsbookUrl"].startswith("https://sportsbook.draftkings.com/")), None)
                if matching_odds:
                    game["HomeTeamMoneyLine"] = matching_odds["PregameOdds"][0]["HomeMoneyLine"]
                    game["AwayTeamMoneyLine"] = matching_odds["PregameOdds"][0]["AwayMoneyLine"]
                else:
                    game["HomeTeamMoneyLine"] = None
                    game["AwayTeamMoneyLine"] = None

            return games_data
        else:
            print(f"Failed to fetch odds data. Status code: {odds_response.status_code}")
            return None
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        return None