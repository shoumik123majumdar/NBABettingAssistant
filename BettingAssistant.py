import matplotlib
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players

'''
Key:
pts - points
reb - rebounds
ast - assists

Parameter Formatting/Examples:
player_name = Russell Westbrook
prop_val = 30
stat_list = ["pts","ast"]
bool - Over/Under --> False
num_games = 82
season = "2022-23"
matchup = Suns --> PHX
'''

class BettingAssistant():
    def __init__(self, player_name, prop_val, stat_list, bool, num_games=0, season="2022-23",matchup="none"):
        self.player_name = player_name
        self.player_id = players.find_players_by_full_name(self.player_name)[0]['id']
        self.season = season
        self.prop_val = prop_val
        self.stat_list = stat_list
        self.bool = bool
        if num_games == 0:
            self.num_games_played = self.get_games_played()
        else:
            self.num_games_played = num_games
        self.matchup = matchup

    # Helper Method
    # Determines if a bet hits based on if a stat is greater than or less than the prop value
    def bet_won_bool(self, stat):
        if (stat > self.prop_val and self.bool == True):
            return True
        elif (stat > self.prop_val and self.bool == False):
            return False
        elif (stat < self.prop_val and self.bool == True):
            return False
        elif (stat < self.prop_val and self.bool == False):
            return True

    # Helper Method
    # Determines all the times the stat hits.
    def num_stat_hit(self):
        num_stat_hit = 0
        response = playergamelog.PlayerGameLog(player_id=self.player_id, season=self.season)
        for i in range(self.num_games_played):
            complete_stat_total = 0
            for stat_name in self.stat_list:
                complete_stat_total += response.get_normalized_dict()['PlayerGameLog'][i][stat_name.upper()]
            if self.bet_won_bool(complete_stat_total):
                num_stat_hit += 1
        return num_stat_hit

    def get_games_played(self):
        response = playergamelog.PlayerGameLog(player_id=self.player_id, season=self.season)
        return len(response.get_normalized_dict()['PlayerGameLog'])

    # Helper Method
    def format_bet_string(self):
        if (self.bool == True):
            ovORund = "OVER"
        else:
            ovORund = "UNDER"
        stat_string = self.stat_list[0] + ","
        for i in range(1, len(self.stat_list)):
            stat_string += self.stat_list[i] + ","
        return f"{self.player_name} will drop {ovORund} {self.prop_val} {stat_string}"

    def prop_hit_analysis(self, printable=False):
        num_hits = self.num_stat_hit()
        percentage_hits = round(num_hits / self.num_games_played * 100, 2)
        bet_string = self.format_bet_string()
        if (printable):
            print(f"The bet that {bet_string} hit {num_hits} out of the last {self.num_games_played} games "
                  f"or {percentage_hits}% of the time")
        return num_hits
