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
printable = True 
'''


class BettingAssistant():
    def __init__(self, player_name, prop_val, stat_list, bool, num_games=0, season="2022-23", matchup="none",
                 printable=False):
        self.player_name = player_name
        self.player_id = players.find_players_by_full_name(self.player_name)[0]['id']
        self.season = season
        self.prop_val = prop_val
        self.stat_list = stat_list
        self.bool = bool
        self.matchup = matchup
        self.printable = printable
        if num_games == 0:
            self.num_games_played = self.get_games_played()
        else:
            self.num_games_played = num_games

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
    # Determines all the times the stat hits and returns that value.
    def num_stat_hit(self):
        num_stat_hit = 0
        response = playergamelog.PlayerGameLog(player_id=self.player_id, season=self.season)
        if (self.matchup != "none"):
            num_games = len(response.get_normalized_dict()['PlayerGameLog'])
        else:
            num_games = self.num_games_played
        for i in range(num_games):
            complete_stat_total = 0
            for stat_name in self.stat_list:
                matchup_str = response.get_normalized_dict()['PlayerGameLog'][i]['MATCHUP']
                if self.matchup != "none" and matchup_str.__contains__(self.matchup):
                    if self.printable:
                        print(str(
                            response.get_normalized_dict()['PlayerGameLog'][i][stat_name.upper()]) + " " + stat_name)
                    complete_stat_total += response.get_normalized_dict()['PlayerGameLog'][i][stat_name.upper()]
                elif self.matchup == "none":
                    if self.printable:
                        print(str(
                            response.get_normalized_dict()['PlayerGameLog'][i][stat_name.upper()]) + " " + stat_name)
                    complete_stat_total += response.get_normalized_dict()['PlayerGameLog'][i][stat_name.upper()]
            if self.bet_won_bool(complete_stat_total):
                num_stat_hit += 1
        return num_stat_hit

    def get_games_played(self):
        response = playergamelog.PlayerGameLog(player_id=self.player_id, season=self.season)
        games = response.get_normalized_dict()['PlayerGameLog']
        games_played = 0
        if self.matchup == "none":
            return len(games)
        else:
            for i in range(len(games)):
                if (games[i]["MATCHUP"].__contains__(self.matchup)):
                    games_played += 1
        return games_played

    # Helper Method
    def format_bet_string(self):
        if self.bool == True:
            over_under = "OVER"
        else:
            over_under = "UNDER"
        stat_string = self.stat_list[0] + ","
        for i in range(1, len(self.stat_list)):
            stat_string += self.stat_list[i] + ","
        if self.matchup == "none":
            matchup = "every team in the league"
        else:
            matchup = self.matchup
        return f"{self.player_name} will drop {over_under} {self.prop_val} {stat_string} against {matchup},"

    def prop_hit_analysis(self, printable=False):
        num_hits = self.num_stat_hit()
        percentage_hits = round(num_hits / self.num_games_played * 100, 2)
        bet_string = self.format_bet_string()
        if printable:
            print(f"The bet that {bet_string} hit {num_hits} out of his last {self.num_games_played} games "
                  f"or {percentage_hits}% of the time")
        return percentage_hits
