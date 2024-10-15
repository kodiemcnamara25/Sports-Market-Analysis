import openmeteo_requests
import pandas as pd
from geopy.geocoders import Nominatim

import requests
import pandas as pd

def get_weather_data(city, state, date, hour):

    geolocator = Nominatim(user_agent='myapplication')
    location = geolocator.geocode(f"{city}, {state}") if state!="" else geolocator.geocode(f"{city}") 
    lat = location.latitude
    lon = location.longitude

    openmeteo = openmeteo_requests.Client()

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date, #"2019-06-08",
        "end_date": date, #"2019-06-08",
        "hourly": ["temperature_2m", "rain", "snowfall", "cloud_cover", "wind_speed_10m"],
        "temperature_unit": "fahrenheit",
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch"
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_rain = hourly.Variables(1).ValuesAsNumpy()
    hourly_snowfall = hourly.Variables(2).ValuesAsNumpy()
    hourly_cloud_cover = hourly.Variables(3).ValuesAsNumpy()
    hourly_wind_speed_10m = hourly.Variables(4).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(hourly.Interval(), unit="s"),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["rain"] = hourly_rain
    hourly_data["snowfall"] = hourly_snowfall
    hourly_data["cloud_cover"] = hourly_cloud_cover
    hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

    hourly_dataframe = pd.DataFrame(data = hourly_data)

    hourly_dataframe['date'] = pd.to_datetime(hourly_dataframe['date'])
    hourly_dataframe = hourly_dataframe[(hourly_dataframe['date'].dt.hour == hour)]

    return(hourly_dataframe)


def get_nfl_scoreboard_data(begin_date, end_date):

    url = f"http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates={begin_date}-{end_date}"
    response = requests.get(url=url)

    all_games = response.json()['events']

    game_dfs = []
    for i in range(len(all_games)):
        
        game = all_games[i]

        if game['shortName'].upper() in ['NFC VS AFC', 'AFC VS NFC'] or game['season']['slug']=="preseason":
            continue

        ID = game['id']
        date = game['date']
        year = game['season']['year']
        game_type = game['season']['slug']
        competition_type = game['competitions'][0]['type']['abbreviation']
        week = game['week']['number']
        neutral_site = game['competitions'][0]['neutralSite']
        conference_competition = game['competitions'][0]['conferenceCompetition']
        venue_city = game['competitions'][0]['venue']['address']['city']
        venue_state = "" if "state" not in game['competitions'][0]['venue']['address'].keys() else game['competitions'][0]['venue']['address']['state']
        venue_indoors = game['competitions'][0]['venue']['indoor']

        home_index = [game['competitions'][0]['competitors'][0]['homeAway'], game['competitions'][0]['competitors'][1]['homeAway']].index("home")
        away_index = [game['competitions'][0]['competitors'][0]['homeAway'], game['competitions'][0]['competitors'][1]['homeAway']].index("away")

        home_team_location = game['competitions'][0]['competitors'][home_index]['team']['location']
        home_team_name = "" if 'name' not in game['competitions'][0]['competitors'][home_index]['team'].keys()\
            else game['competitions'][0]['competitors'][home_index]['team']['name']
        home_team_abb = game['competitions'][0]['competitors'][home_index]['team']['abbreviation']
        
        home_team_score = game['competitions'][0]['competitors'][home_index]['score']
        home_team_score_Q1 = game['competitions'][0]['competitors'][home_index]['linescores'][0]['value']
        home_team_score_Q2 = game['competitions'][0]['competitors'][home_index]['linescores'][1]['value']
        home_team_score_Q3 = game['competitions'][0]['competitors'][home_index]['linescores'][2]['value']
        home_team_score_Q4 = game['competitions'][0]['competitors'][home_index]['linescores'][3]['value']

        away_team_location = game['competitions'][0]['competitors'][away_index]['team']['location']
        away_team_name =  "" if 'name' not in game['competitions'][0]['competitors'][away_index]['team'].keys()\
            else game['competitions'][0]['competitors'][away_index]['team']['name']
        away_team_abb = game['competitions'][0]['competitors'][away_index]['team']['abbreviation']
        
        away_team_score = game['competitions'][0]['competitors'][away_index]['score']
        away_team_score_Q1 = game['competitions'][0]['competitors'][away_index]['linescores'][0]['value']
        away_team_score_Q2 = game['competitions'][0]['competitors'][away_index]['linescores'][1]['value']
        away_team_score_Q3 = game['competitions'][0]['competitors'][away_index]['linescores'][2]['value']
        away_team_score_Q4 = game['competitions'][0]['competitors'][away_index]['linescores'][3]['value']

        primetime_game = any([x['market']['type']=="National" for x in game['competitions'][0]['geoBroadcasts']])
        description = "" if "headlines" not in game['competitions'][0].keys() else game['competitions'][0]['headlines'][0]['description']

        nfl_scoreboard = pd.DataFrame({
            "ID": ID,
            "date": date,
            "year": year,
            "game_type": game_type,
            "competition_type": competition_type,
            "week": week,
            "neutral_site": neutral_site,
            "conference_competition": conference_competition,
            "venue_city": venue_city,
            "venue_state": venue_state,
            "venue_indoors": venue_indoors,
            "home_team_location": home_team_location,
            "home_team_name": home_team_name,
            "home_team_abb": home_team_abb,
            "home_team_score": home_team_score,
            "home_team_score_Q1": home_team_score_Q1,
            "home_team_score_Q2": home_team_score_Q2,
            "home_team_score_Q3": home_team_score_Q3,
            "home_team_score_Q4": home_team_score_Q4,
            "away_team_location": away_team_location,
            "away_team_name": away_team_name,
            "away_team_abb": away_team_abb,
            "away_team_score": away_team_score,
            "away_team_score_Q1": away_team_score_Q1,
            "away_team_score_Q2": away_team_score_Q2,
            "away_team_score_Q3": away_team_score_Q3,
            "away_team_score_Q4": away_team_score_Q4,
            "primetime_game": primetime_game,
            "description": description
        }, index=[i])

        game_dfs.append(nfl_scoreboard)
    
    if(len(game_dfs)):
        return(pd.concat(game_dfs))

game_id = 401326322
def get_nfl_boxscore_data(game_id):

    url = f"https://cdn.espn.com/core/nfl/boxscore?xhr=1&gameId={game_id}"
    response = requests.get(url=url)

    team_home_away = response.json()['gamepackageJSON']['boxscore']['teams'][0]['homeAway']
    team1_boxscore = pd.DataFrame([(f"{team_home_away} {x['label']}", x['displayValue']) for x in response.json()['gamepackageJSON']['boxscore']['teams'][0]['statistics']]).set_index(0).T

    team_home_away = response.json()['gamepackageJSON']['boxscore']['teams'][1]['homeAway']
    team2_boxscore = pd.DataFrame([(f"{team_home_away} {x['label']}", x['displayValue']) for x in response.json()['gamepackageJSON']['boxscore']['teams'][1]['statistics']]).set_index(0).T

    nfl_boxscore = pd.concat([team1_boxscore, team2_boxscore], axis = 1)
    nfl_boxscore.columns.name = None
    return(nfl_boxscore)

def _parse_espn_bet(odds_dict):
    away_team_spread = odds_dict['awayTeamOdds']['close']['pointSpread']['american'] if\
        "pointSpread" not in odds_dict['awayTeamOdds']['current'].keys()\
        else odds_dict['awayTeamOdds']['current']['pointSpread']['american']

    away_team_spread_open = away_team_spread if\
        "open" not in odds_dict['awayTeamOdds'].keys() or 'pointSpread' not in odds_dict['awayTeamOdds']['open']\
        else odds_dict['awayTeamOdds']['open']['pointSpread']['american']

    home_team_spread = odds_dict['homeTeamOdds']['close']['pointSpread']['american'] if\
        "pointSpread" not in odds_dict['homeTeamOdds']['current'].keys()\
        else odds_dict['homeTeamOdds']['current']['pointSpread']['american']

    home_team_spread_open = home_team_spread if\
        "open" not in odds_dict['homeTeamOdds'].keys() or 'pointSpread' not in odds_dict['homeTeamOdds']['open']\
        else odds_dict['homeTeamOdds']['open']['pointSpread']['american']

    over_under = odds_dict['close']['total']['american'] if \
        'total' not in odds_dict['current'].keys() \
        else odds_dict['current']['total']['american']

    over_under_open = over_under if\
        "open" not in odds_dict.keys() or "total" not in odds_dict['open'].keys()\
        else odds_dict['open']['total']['american']

    nfl_odds = pd.DataFrame({
        "away_team_underdog": odds_dict['awayTeamOdds']['underdog'],
        "away_team_spread": away_team_spread,
        "away_team_spread_open": away_team_spread_open,
        "home_team_underdog": odds_dict['homeTeamOdds']['underdog'],
        "home_team_spread": home_team_spread,
        "home_team_spread_open": home_team_spread_open,
        "over_under": over_under,
        "over_under_open": over_under_open,
        }, index=[0])
    
    return(nfl_odds)


def _parse_bet365(odds_dict):

    away_team_spread = odds_dict['bettingOdds']['teamOdds']['preMatchSpreadHandicapAway']['value']
    away_team_spread_open = away_team_spread

    home_team_spread = odds_dict['bettingOdds']['teamOdds']['preMatchSpreadHandicapHome']['value']
    home_team_spread_open = home_team_spread

    over_under = odds_dict['bettingOdds']['teamOdds']['preMatchTotalHandicap']
    over_under_open = over_under

    nfl_odds = pd.DataFrame({
        "away_team_underdog": float(away_team_spread) < 0,
        "away_team_spread": away_team_spread,
        "away_team_spread_open": away_team_spread_open,
        "home_team_underdog": float(home_team_spread) < 0,
        "home_team_spread": home_team_spread,
        "home_team_spread_open": home_team_spread_open,
        "over_under": over_under,
        "over_under_open": over_under_open,
        }, index=[0])
    
    return(nfl_odds)


def _parse_draftkings(odds_dict):

    away_team_spread = odds_dict['awayTeamOdds']['current']['pointSpread']['american']
    away_team_spread_open = away_team_spread

    home_team_spread = odds_dict['homeTeamOdds']['current']['pointSpread']['american']
    home_team_spread_open = home_team_spread

    over_under = odds_dict['overUnder']
    over_under_open = over_under

    nfl_odds = pd.DataFrame({
        "away_team_underdog": odds_dict['awayTeamOdds']['underdog'],
        "away_team_spread": away_team_spread,
        "away_team_spread_open": away_team_spread_open,
        "home_team_underdog": odds_dict['homeTeamOdds']['underdog'],
        "home_team_spread": home_team_spread,
        "home_team_spread_open": home_team_spread_open,
        "over_under": over_under,
        "over_under_open": over_under_open,
        }, index=[0])
    
    return(nfl_odds)


def get_nfl_odds_data(game_id):
    url = f"https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/events/{game_id}/competitions/{game_id}/odds"
    response = requests.get(url=url)

    provider_names = [x['provider']['name'].upper() for x in response.json()['items']]

    espn_provider = [("ESPN BET" in x) for x in provider_names]
    draftkings_provider = [("DRAFTKINGS" in x) for x in provider_names]
    bet365_provider = [("BET 365" in x) for x in provider_names]

    if any(espn_provider):
        nfl_odds = _parse_espn_bet(response.json()['items'][espn_provider.index(True)])
    elif any(draftkings_provider):
        nfl_odds = _parse_draftkings(response.json()['items'][draftkings_provider.index(True)]) 
    elif any(bet365_provider):
        nfl_odds = _parse_bet365(response.json()['items'][bet365_provider.index(True)])       
    else:
        print("No Odds found")
        return(
            pd.DataFrame({
        "away_team_underdog": pd.NA,
        "away_team_spread": pd.NA,
        "away_team_spread_open": pd.NA,
        "home_team_underdog": pd.NA,
        "home_team_spread": pd.NA,
        "home_team_spread_open": pd.NA,
        "over_under": pd.NA,
        "over_under_open": pd.NA,
        }, index=[0])
        )
    
    return(nfl_odds)

