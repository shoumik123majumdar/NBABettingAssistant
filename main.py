import json
import time
from BettingAssistant import BettingAssistant
from selenium import webdriver
import matplotlib.pyplot as plt
import mplcursors


'''
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

Sample Game Log:
{'SEASON_ID': '22023', 'Player_ID': 203084, 'Game_ID': '0022300663', 'GAME_DATE': 'JAN 29, 2024', 'MATCHUP': 'SAC @ MEM', 'WL': 'W', 'MIN': 35, 'FGM': 5, 'FGA': 15, 'FG_PCT': 0.333, 'FG3M': 2, 'FG3A': 10, 'FG3_PCT': 0.2, 'FTM': 0, 'FTA': 0, 'FT_PCT': 0.0, 'OREB': 0, 'DREB': 3, 'REB': 3, 'AST': 4, 'STL': 0, 'BLK': 0, 'TOV': 1, 'PF': 1, 'PTS': 12, 'PLUS_MINUS': 15, 'VIDEO_AVAILABLE': 1}
'''


LEAGUE_ID = 7  # NBA league ID from PrizePicks database
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

#Names that are excluded due to the NBA API not containing these players
#due to possible incongruency between how it is spelled in PrizePicks database, and the NBA API database
bad_names = ["GG Jackson II", "Nicolas Claxton", "Trey Jemison"]


# Makes the request to scrape PrizePick's board using selenium
def scrape_html(page_url):
    driver = webdriver.Chrome()
    driver.get(page_url)
    json_text = driver.page_source
    driver.quit()
    return clean_json(json_text)


# Cleans html text provided so it only reveals the json
def clean_json(html_text):
    start_index = html_text.find('{')
    end_index = html_text.rfind('}')
    if start_index != -1 and end_index !=-1:
        return html_text[start_index:end_index+1]
    else:
        return "Not Found"


#Creates a hashmap of playerID--> name and creates a list of playerIDs
def generate_playerid_list(json, name_dict):
    playerIDList = []
    for i in range(len(json['included'])):
        playerID = json['included'][i]['id']
        #If it is a player and has not already been added to the playerIDList...
        if(json['included'][i]['type'] == "new_player" and playerIDList.__contains__(playerID) != True):
            playerID = json['included'][i]['id']
            name_dict[playerID] = json['included'][i]['attributes']['name']
            playerIDList.append(playerID)


# Gets all the different projection types for the day ie: 'Rebs+Asts'
# Creates dict of corresponding dictionaries for every projection type ie: 'Pts+Rebs+Asts': {id:line_score}
def get_projection_types(dict):
    proj_list = []
    for i in range(len(dict['included'])):
        # Second conditional makes sure to only pick stat_types that are tracked in the game log
        if dict['data'][i]['type'] == "projection" and dict['data'][i]['attributes']['stat_type'] in stat_mapping.keys():
            proj_list.append(dict['data'][i]['attributes']['stat_type'])
    proj_list = list(set(proj_list))
    projection_dict = {proj: {} for proj in proj_list}
    return projection_dict


#Fills the projection dictionary after it is created
def fill_projection_dict(x,projection_dict):
    for projection_data in x['data']:
        proj_type = projection_data['attributes']['stat_type']
        player_id = projection_data['relationships']['new_player']['data']['id']
        line_score = projection_data['attributes']['line_score']
        if proj_type in projection_dict and player_id not in projection_dict[proj_type] and projection_data['attributes']['odds_type'] == "standard":
            projection_dict[proj_type][player_id] = line_score


#Converts the given stat text from the PrizePicks database into a stat_list
#This is so that the BettingAssistant class can process it
def convert_to_readable_stat(stat, stat_mapping):
    return stat_mapping.get(stat, [])


#Creates a visualization of all of the props and their probabilities.
def visualize_props(data):
    probability_list = []
    prop_list = []
    for player, prop_info in data.items():
        projection = prop_info['Prop Text']
        probability = prop_info['Probability']

        prop_list.append(projection)
        probability_list.append(probability)

    plt.figure(figsize=(10, 6))
    plot = plt.scatter(prop_list, probability_list, color='blue', alpha=0.5)
    plt.title('Probability vs. Projection')
    plt.xlabel('Projection')
    plt.ylabel('Probability (%)')
    plt.xticks([])
    mplcursors.cursor(plot)
    plt.show()


def main():
    #First load up the json by scraping the PrizePicks website
    x = json.loads(scrape_html(
        f"https://api.prizepicks.com/projections?league_id={LEAGUE_ID}&per_page=250&state_code=MA&single_stat=true&game_mode=prizepools"))

    #Map the players name to their database id
    name_dict = {}
    generate_playerid_list(x, name_dict)

    #Map the projections to the corresponding player's database id
    projection_dict = get_projection_types(x)
    fill_projection_dict(x, projection_dict)

    #This dictionary will contain all of the props in a tabularized format
    final_dict = {}
    counter = 1
    for proj in projection_dict:
        for id in projection_dict[proj]:
            #Make sure we are not including multi-player bets (will have "+" in them)
            #Avoid certain players due to their name's not being registered in the NBA API database
            if name_dict[id].__contains__("+") != True and name_dict[id] not in bad_names:
                assistant = BettingAssistant(name_dict[id],projection_dict[proj][id],convert_to_readable_stat(proj,stat_mapping),True)
                #Wait 0.4 seconds so the NBA API doesn't get swarmed with our requests all at once and block IP addy
                time.sleep(0.400)
                final_dict[counter] = assistant.tabularize_prop()
                counter+=1

    #Outputs the Best Picks for the day (sorts them by probability)
    print("\n\n\n\n\nBest Picks of the Day!:")
    sorted_props = sorted(final_dict.items(),key=lambda x: x[1]["Probability"],reverse=True)
    for player, prop_data in sorted_props:
        print(prop_data['Printable Result'])

    visualize_props(final_dict)


if __name__ == "__main__":
    main()


