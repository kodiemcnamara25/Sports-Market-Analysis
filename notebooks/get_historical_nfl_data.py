import pandas as pd
from datetime import datetime
import time

from notebooks.nfl_data_acquisition_functions import *

begin_date = "20210901"
end_date = "20220301"
filename = "NFL Data 2021"

range_dates = pd.date_range(start=begin_date,end=end_date)
range_dates_text = [datetime.strftime(x, '%Y%m%d') for x in range_dates]

game_dfs = []
for dt in range_dates_text:
    
    nfl_scoreboard_data = get_nfl_scoreboard_data(begin_date = dt, end_date = dt)
    if nfl_scoreboard_data is None:
        continue

    nfl_boxscore_data = pd.concat([get_nfl_boxscore_data(x) for x in nfl_scoreboard_data['ID']])
    nfl_boxscore_data.index = nfl_scoreboard_data.index

    nfl_odds_data = pd.concat([get_nfl_odds_data(x) for x in nfl_scoreboard_data['ID']])
    nfl_odds_data.index = nfl_scoreboard_data.index
        
    weather_request_success = False

    while not weather_request_success:
        # Less than 10'000 API calls per day, 5'000 per hour and 600 per minute.
        try:
            weather_data = pd.concat(
                [get_weather_data(city, state, date, hour)\
                for city, state, date, hour\
                in zip(nfl_scoreboard_data['venue_city'], \
                        nfl_scoreboard_data['venue_state'], \
                        [x.split("T")[0] for x in nfl_scoreboard_data['date']], \
                        [int(x.split("T")[1].split(":")[0]) for x in nfl_scoreboard_data['date']])]
            )
            weather_request_success = True
        except:
            print("Sleeping for 30s")
            time.sleep(30)

    weather_data.index = nfl_scoreboard_data.index
    
    game_df = pd.concat([nfl_scoreboard_data, nfl_boxscore_data, nfl_odds_data, weather_data], axis = 1)

    game_dfs.append(game_df)

nfl_historical_data = pd.concat(game_dfs)

nfl_historical_data.to_csv(path_or_buf = f"./data/interim/{filename}.csv", index = False)