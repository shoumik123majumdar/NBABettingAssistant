import requests
from nba_api.stats.endpoints import playergamelog, teamgamelog
from nba_api.stats.static import teams, players
import statistics
import pandas as pd

def get_game_logs(player_id, stat, season, mov_avg=5):
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    game_log_data = game_log.get_data_frames()[0]
    stat_avg = statistics.mean(game_log_data[stat])
    stat_mov_avg = statistics.mean(game_log_data[stat][:mov_avg])
    
    return game_log_data

def team_data(team_id,stat,season,mov_avg = 5):
    game_log = teamgamelog.TeamGameLog(team_id=team_id, season=season)
    game_log_data = game_log.get_data_frames()[0]
    stat_avg = statistics.mean(game_log_data[stat])
    stat_mov_avg = statistics.mean(game_log_data[stat][:mov_avg])
    print(stat_avg)
    print(stat_mov_avg)
    return game_log_data


def get_team_id(nickname,teams):
    for team in teams:
        if team['nickname'] == nickname:
            return team['id']
    return None

def get_opp(player_game_log):
    opponent_list = []
    for i in player_game_log['MATCHUP']:
        parts = i.split()
        opponent_list.append(parts[-1])
    teams_dict = teams.get_teams()
    id_dict = {}
    for i in opponent_list:
        for team in teams_dict:
            if i == team['abbreviation']:
                id_dict[i] = team['id']
    print(id_dict)
    return opponent_list, id_dict
    
    
    

def training_data_compile(stat,player_id,season,mov_avg = 5):
    player_game_log = get_game_logs(player_id, stat, season, mov_avg=5)
    player_game_log = player_game_log.iloc[::-1]
    team_game_log = team_data(team_id,stat,season,mov_avg = 5)
    team_game_log = team_game_log.iloc[::-1]
    print(player_game_log.head())
    print(team_game_log.head())
    data = pd.DataFrame()
    data[f'avg_{stat}' ] = player_game_log[stat].expanding().mean()
    data[f'moving_avg_{stat}'] = player_game_log[stat].rolling(window=mov_avg, min_periods=1).mean() 
    opponent_list, id_dict = get_opp(player_game_log)
    data['OPP'] = opponent_list
    data["GAME_DATE"] = player_game_log['GAME_DATE']
    print(data)


def main():
    satan = 'New York Knicks'
    teams_dict = teams.get_teams()
    opponent_team = [x for x in teams_dict if x['full_name'] == satan][0]
    team_id = opponent_team['id']

    goat = 'Jayson Tatum'
    player_dict = players.get_players()
    target_player = [x for x in player_dict if x['full_name'] == goat][0]
    player_id = target_player['id']
    training_data_compile('PTS',player_id, team_id, '2023')
main()

'''
# Example usage:
player_id = 123456  # Replace with actual player ID
team_id = 987654  # Replace with actual team ID

player_avg_stats = get_player_avg_stats(player_id)
last_5_games_avg_stats = get_player_last_5_games_avg_stats(player_id)
opposing_team_stats = get_opposing_team_stats(team_id)
opposing_team_offensive_rating, opposing_team_defensive_rating = get_opposing_team_ratings(team_id)
'''
