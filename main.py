import matplotlib
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

'''
Key:
pts - points
reb - rebounds
ast - assists
bool - Over/Under

'''

CURRENT_SEASON = "2022-23"


def get_player_id(player_name):
    response = players.find_players_by_full_name(player_name)
    return response[0]['id']


# Helper Method
def bet_won_bool(stat, prop_val, bool):
    if (stat > prop_val and bool == True):
        return True
    elif (stat > prop_val and bool == False):
        return False
    elif (stat < prop_val and bool == True):
        return False
    elif (stat < prop_val and bool == False):
        return True


# Helper Method
def num_stat_hit(player_name, num_games,prop_val, stat_name_list, bool,):
    num_stat_hit = 0
    player_id = get_player_id(player_name)
    response = playergamelog.PlayerGameLog(player_id=player_id, season=CURRENT_SEASON)
    for i in range(num_games):
        complete_stat_total = 0
        for stat_name in stat_name_list:
            complete_stat_total += response.get_normalized_dict()['PlayerGameLog'][i][stat_name.upper()]
        if (bet_won_bool(complete_stat_total, prop_val, bool)):
            num_stat_hit += 1
    return num_stat_hit


def get_games_played(player_name):
    player_id = get_player_id(player_name)
    response = playergamelog.PlayerGameLog(player_id=player_id, season=CURRENT_SEASON)
    return len(response.get_normalized_dict()['PlayerGameLog'])


# Helper Method
def format_bet_string(player_name, prop_val, stat_list, bool):
    if (bool == True):
        ovORund = "OVER"
    else:
        ovORund = "UNDER"
    stat_string = stat_list[0] + ","
    for i in range(1, len(stat_list)):
        stat_string += stat_list[i] + ","
    return f"{player_name} will drop {ovORund} {prop_val} {stat_string}"


def prop_hit_analysis(player_name, prop_val, stat_list, bool, num_games=0, printable=False):
    if (num_games == 0):
        num_games_played = get_games_played(player_name)
    else:
        num_games_played = num_games
    num_hits = num_stat_hit(player_name, num_games_played, prop_val, stat_list, bool)
    percentage_hits = round(num_hits / num_games_played * 100, 2)
    bet_string = format_bet_string(player_name, prop_val, stat_list, bool)
    if (printable):
        print(f"The bet that {bet_string} hit {num_hits} out of the last {num_games_played} games "
              f"or {percentage_hits}% of the time")
    return num_hits


prop_hit_analysis("Russell Westbrook",50, ["pts","reb","ast"], False,printable=True)

'''
IDEAS
# Russell Westbrook, 16, pts



#Later
def graph_analysis():
    return 0
'''
