import json
import cloudscraper
import time
from BettingAssistant import BettingAssistant
from scraper import PickScraper
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




LEAGUE_ID = 7  # NBA league ID

scraper = cloudscraper.create_scraper()
resp = scraper.get(f"https://api.prizepicks.com/projections?league_id={LEAGUE_ID}&per_page=250&single_stat=true")
resp2 = scraper.get(f"https://api.prizepicks.com/projections?league_id={LEAGUE_ID}&per_page=250&single_stat=false")

x= json.loads(resp.text)
x2 = json.loads(resp2.text)

#Creates a hashmap of playerID-->name and creates a list of playerIDs
name_dict = {}
playerIDList = [];
for i in range(len(x['included'])):
    if(x['included'][i]['type']== "new_player"):
        name_dict[x['included'][i]['id']] = x['included'][i]['attributes']['name']
        playerIDList.append(x['included'][i]['id'])

for i in range(len(x['included'])):
    if (x2['included'][i]['type'] == "new_player"):
        if (playerIDList.__contains__(x2['included'][i]['id']) != True):
            name_dict[x2['included'][i]['id']] = x2['included'][i]['attributes']['name']
            playerIDList.append(x2['included'][i]['id'])


def get_projection_types(dict):
    proj_list = []
    for i in range(len(dict['included'])):
        if (dict['data'][i]['type'] == "projection"):
            proj_list.append(dict['data'][i]['attributes']['stat_type'])
    proj_list = list(set(proj_list))
    projection_dict = {proj: {} for proj in proj_list}
    return proj_list,projection_dict

projection_list, projection_dict = get_projection_types(x)

def fill_projection_list(x,projection_list,projection_dict):
    for i in range(len(x['data'])):
        for proj in projection_list:
            if(x['data'][i]['attributes']['stat_type'] == proj):
                projection_dict[proj][x['data'][i]['relationships']['new_player']['data']['id']] = x['data'][i]['attributes'][
                    'line_score']



fill_projection_list(x,projection_list,projection_dict)
fill_projection_list(x2,projection_list,projection_dict)


def convertToReadableStat(stat):
    if(stat == "Free Throws Made"):
        return ["ftm"]
    elif(stat == "Rebounds"):
        return ["reb"]
    elif(stat == "Assists"):
        return ["ast"]
    elif(stat == "Points"):
        return ["pts"]
    elif(stat == "Pts+Rebs+Asts"):
        return ["pts","reb","ast"]
    elif(stat == "3-PT Made"):
        return ["fg3m"]
    elif(stat == "Pts+Rebs"):
        return ["pts","reb"]
    elif(stat == "Pts+Asts"):
        return ["pts","ast"]
    elif(stat == "Rebs+Asts"):
        return ["reb","ast"]
    elif(stat == "Blks+Stls"):
        return ["blk","stl"]
    elif(stat=="Steals"):
        return ["stl"]
    elif(stat=="Blocks"):
        return ["blk"]
    elif(stat=="Turnovers"):
        return ["tov"]
    elif(stat == "3-PT Attempted"):
        return ["fg3a"]
    elif(stat == "Personal Fouls"):
        return ["pf"]
    elif(stat=="FG Attempted"):
        return ["fga"]
    elif(stat=="FG Made"):
        return ["fgm"]
    elif(stat=="Minutes Played"):
        return ["min"]


final_dict = {}
for proj in projection_list:
    for id in playerIDList:
        stat_dict = projection_dict[proj]
        if(id in stat_dict and name_dict[id].__contains__("+") != True and proj!="Fantasy Score" and proj!="Dunks" and proj!="Points In First 6 Minutes"):
            assistant = BettingAssistant(name_dict[id],stat_dict[id],convertToReadableStat(proj),True)
            time.sleep(0.600)
            percentage_chance,print_string = assistant.prop_hit_analysis(printable = True)
            final_dict[percentage_chance] = print_string


print("\n\n\n\n\nBest Picks of the Day!:")
keys = list(final_dict)
keys.sort()
keys.reverse()
for key in keys:
    print(final_dict[key])

'''
assistant = BettingAssistant("Julius Randle",13,["reb","ast"],True,printable=True)

assistant.prop_hit_analysis(printable=True)
'''




#Create a list of totals for each game in a list.
#Compare each total using the


'''
IDEAS
# Russell Westbrook, 16, pts

#Later
def graph_analysis():
    return 0
'''
