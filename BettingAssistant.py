import matplotlib
from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import matplotlib.pyplot as plt

stat_mapping = {
        "Free Throws Made": ["ftm"],
        "Rebounds": ["reb"],
        "Assists": ["ast"],
        "Points": ["pts"],
        "Pts+Rebs+Asts": ["pts", "reb", "ast"],
        "3-PT Made": ["fg3m"],
        "Pts+Rebs": ["pts", "reb"],
        "Pts+Asts": ["pts", "ast"],
        "Rebs+Asts": ["reb", "ast"],
        "Blks+Stls": ["blk", "stl"],
        "Steals": ["stl"],
        "Blocked Shots": ["blk"],
        "Turnovers": ["tov"],
        "3-PT Attempted": ["fg3a"],
        "Personal Fouls": ["pf"],
        "FG Attempted": ["fga"],
        "FG Made": ["fgm"],
        "Minutes Played": ["min"],
        "Defensive Rebounds":["dreb"],
        "Offensive Rebounds":["oreb"]
}

class BettingAssistant():
    def __init__(self, player_name, prop_val, stat_list, bool, num_games=0, season="2023-24", matchup="None",
                 printable=False):
        self.player_name = player_name
        self.player_id = players.find_players_by_full_name(self.player_name)[0]['id']
        self.season = season
        self.prop_val = prop_val
        self.stat_list = stat_list
        self.bool = bool
        self.bool_str = ""
        if self.bool == False:
            self.bool_str = "UNDER"
        else:
            self.bool_str = "OVER"
        self.matchup = matchup
        self.printable = printable
        if num_games == 0:
            self.num_games_played = self.get_games_played()
        else:
            self.num_games_played = num_games
        self.totals = []

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
        elif(stat==self.prop_val and self.bool==True):
            return False
        elif(stat==self.prop_val and self.bool==False):
            return True

    # Helper Method
    # Determines all the times the stat hits and returns that value.
    def num_stat_hit(self):
        num_stat_hit = 0
        response = playergamelog.PlayerGameLog(player_id=self.player_id, season=self.season)
        if (self.matchup != "None"):
            num_games = len(response.get_normalized_dict()['PlayerGameLog'])
        else:
            num_games = self.num_games_played
        for i in range(num_games):
            complete_stat_total = 0
            for stat_name in self.stat_list:
                matchup_str = response.get_normalized_dict()['PlayerGameLog'][i]['MATCHUP']
                if self.matchup != "None" and matchup_str.__contains__(self.matchup):
                    if self.printable:
                        print(str(
                            response.get_normalized_dict()['PlayerGameLog'][i][stat_name.upper()]) + " " + stat_name)
                    complete_stat_total += response.get_normalized_dict()['PlayerGameLog'][i][stat_name.upper()]
                elif self.matchup == "None":
                    if self.printable:
                        print(str(
                            response.get_normalized_dict()['PlayerGameLog'][i][stat_name.upper()]) + " " + stat_name)
                    complete_stat_total += response.get_normalized_dict()['PlayerGameLog'][i][stat_name.upper()]
            self.totals.append(complete_stat_total)
            if self.bet_won_bool(complete_stat_total):
                num_stat_hit += 1
        return num_stat_hit

    def get_games_played(self):
        response = playergamelog.PlayerGameLog(player_id=self.player_id, season=self.season)
        games = response.get_normalized_dict()['PlayerGameLog']
        games_played = 0
        if self.matchup == "None":
            return len(games)
        else:
            for i in range(len(games)):
                if (games[i]["MATCHUP"].__contains__(self.matchup)):
                    games_played += 1
        return games_played

    # Helper Method
    def format_bet_string(self):
        stat_string = self.stat_list[0] + ","
        for i in range(1, len(self.stat_list)):
            stat_string += self.stat_list[i] + ","
        if self.matchup == "None":
            matchup = "every team in the league"
        else:
            matchup = self.matchup
        return f"{self.player_name} will drop {self.bool_str} {self.prop_val} {stat_string} against {matchup},"

    def prop_hit_analysis(self, printable=False):
        num_hits = self.num_stat_hit()
        percentage_hits = round(num_hits / self.num_games_played * 100, 2)

        bet_string = self.format_bet_string()
        print_string = f"The bet that {bet_string} hit {num_hits} out of his last {self.num_games_played} games or {percentage_hits}% of the time"
        if printable:
            print(print_string)
        return percentage_hits,print_string

    def tabularize_prop(self):
        data = {
            "Name" : self.player_name,
            "Line Score": self.prop_val,
            "Stat Type" : self.stat_list,
            "Over/Under?" : self.bool_str
        }

        percentage_hits, print_string = self.prop_hit_analysis()
        data["Probability"] = percentage_hits
        data["Printable Prop"] = print_string
        return data


    def visualize_prop(self):
        self.prop_hit_analysis()
        plt.plot(range(len(self.totals)),self.totals)
        plt.axhline(y=self.prop_val, color='r', linestyle='--', label="Given Prop")

        stat_type = ""
        for key in stat_mapping:
            if stat_mapping[key] == self.stat_list:
                stat_type = key

        plt.xlabel("Games Played")
        plt.ylabel(stat_type)
        plt.title(f"{self.player_name}'s performance trying to get {self.bool_str} {self.prop_val} {stat_type} ")
        plt.show()