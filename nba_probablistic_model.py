import requests
from nba_api.stats.endpoints import playergamelog, teamgamelog, teamestimatedmetrics
from nba_api.stats.static import teams, players
import statistics

def get_player_avg_stats(player_id, stat, season, mov_avg=5):
    game_log = playergamelog.PlayerGameLog(player_id=player_id, season=season)
    game_log_data = game_log.get_data_frames()[0]
    print(game_log)
    stat_avg = statistics.mean(game_log_data[stat])
    stat_mov_avg = statistics.mean(game_log_data[stat][:mov_avg])
    print(stat_avg)
    print(stat_mov_avg)
    return stat_avg, stat_mov_avg

def team_data(team_id,stat,season,mov_avg = 5):
    game_log = teamgamelog.TeamGameLog(team_id=team_id, season=season)
    game_log_data = game_log.get_data_frames()[0]
    print(game_log_data.columns)
    stat_avg = statistics.mean(game_log_data[stat])
    stat_mov_avg = statistics.mean(game_log_data[stat][:mov_avg])
    print(stat_avg)
    print(stat_mov_avg)
    return stat_avg, stat_mov_avg

def team_metrics(team_id, stat, season):
    team_metrics = teamestimatedmetrics.TeamEstimatedMetrics(season=season)
# Make the API request
    team_metrics.get_request()
# Access the retrieved data
    team_estimated_metrics_data = team_metrics.team_estimated_metrics.get_data_frame()
# Print the first few rows of the data
    print(team_estimated_metrics_data)

def main():
    satan = 'New York Knicks'
    teams_dict = teams.get_teams()
    opponent_team = [x for x in teams_dict if x['full_name'] == satan][0]
    team_id = opponent_team['id']

    goat = 'Jayson Tatum'
    player_dict = players.get_players()
    target_player = [x for x in player_dict if x['full_name'] == goat][0]
    player_id = target_player['id']
    print(target_player)
    player_avg_stats = get_player_avg_stats(player_id,'PTS','2023')

    team_data(team_id, 'PTS', '2023')
    team_metrics(team_id, 'E_OFF_RATING', '2023')
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
