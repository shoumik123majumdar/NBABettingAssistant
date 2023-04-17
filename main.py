from BettingAssistant import BettingAssistant

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
or "None" for all games
printable = True 
'''


assistant = BettingAssistant("Joel Embiid",32.5,["pts"],True,matchup="None",printable=True)

assistant.prop_hit_analysis(printable=True)




'''

IDEAS
# Russell Westbrook, 16, pts

#Later
def graph_analysis():
    return 0
'''
