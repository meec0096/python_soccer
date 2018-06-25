from bs4 import BeautifulSoup
import requests
import re
import os
import sys
from datetime import datetime
sys.path.append("/root/python_soccer/")
#sys.path.append("/mnt/c/Users/meec/Documents/pythonproj/python_soccer")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "python_soccer.settings")

import django
django.setup()

from django.core.exceptions import ObjectDoesNotExist
from worldcup.models import Team,Match,Scored

def get_scores():
    pageText = requests.get("http://livescores.com").text
    
    soup = BeautifulSoup(pageText, 'html.parser')
    #soup = BeautifulSoup(open(r'testing.html'), 'html.parser')

    # get every row in homepage
    worldcupRecords = soup.find_all("div", class_="row-gray")

    # narrow down links to those that only pertain to World Cup
    worldcupRecords = [item for item in worldcupRecords if item.find("a",href=re.compile("worldcup"))]

    minute_list = []
    rplayer_list = []
    lplayer_list = [] 
    scores_list = []

    #Parse information into seperate list
    for item in worldcupRecords:
        minute_list.append(item.find("div", class_="min").text.replace(" ","").replace("'",""))
        rplayer_list.append(item.find("div", class_="ply tright name").text.replace(" ", ""))
        lplayer_list.append(item.find("div", class_="ply name").text.replace(" ",""))
        scores_list.append(item.find("a").text.replace(" ",""))


    # Creeate empty list to store dictionary object represent a currently playing game
    returnScoreList = []
    for item in get_teams_gen(minute_list):
        score_dict = {
            "rightplayer": str(rplayer_list[item]),
            "leftplayer": str(lplayer_list[item]),
            str(rplayer_list[item]): scores_list[item].split("-")[0],
            str(lplayer_list[item]): scores_list[item].split("-")[1],
            "minute": str(minute_list[item])   
        }
        
        returnScoreList.append(score_dict)

    # if no game is playing return None
    if len(returnScoreList) == 0:
        return None
    else:
        return returnScoreList

# iterate through the minute list to find out if a game is currently playing
# Not sure if i needed a generator function
def get_teams_gen(minute_list):
    i = 0
    while i < len(minute_list):
        if minute_list[i] != 'FT' and re.compile("[0-9][0-9]+:[0-9][0-9]+").match(minute_list[i]) == None:
            yield i
        i += 1
# This is gonna be runned at 12:00am every day to update database
def get_today_match():
    pageText = requests.get("http://www.livescores.com").text
    soup = BeautifulSoup(pageText, 'html.parser')

    # get every row in homepage
    worldcupRecords = soup.find_all("div", class_="row-gray")

    # narrow down links to those that only pertain to World Cup
    worldcupRecords = [item for item in worldcupRecords if item.find("a",href=re.compile("worldcup"))]

    rplayer_list = []
    lplayer_list = []
    time_list = []

    for item in worldcupRecords:
        time_list.append(item.find("div", class_="min").text.replace(" ",""))
        rplayer_list.append(item.find("div", class_="ply tright name").text.replace(" ", ""))
        lplayer_list.append(item.find("div", class_="ply name").text.replace(" ",""))

    return rplayer_list, lplayer_list, time_list

# only execute @ 12:00 am
def insert_today_match():
    rplayer, lplayer, time = get_today_match()

    for i in range(len(rplayer)):
        right_team = None
        left_team = None

        #Find out if the team is already in database, if not insert team to database    
        try:
            print(rplayer[i], lplayer[i])
            right_team = Team.objects.get(pk=rplayer[i])
            left_team =  Team.objects.get(pk=lplayer[i])
        except ObjectDoesNotExist:
            if right_team == None:
                right_team = Team(pk = rplayer[i], isEliminated = False, totalGoals = 0)
                right_team.save()
            
            if left_team == None:
                left_team = Team(pk = lplayer[i], isEliminated = False, totalGoals = 0)
                left_team.save()
        
        #insert match for today into database
        insert_match = Match(RightTeam = right_team, LeftTeam = left_team)
        insert_match.save()

        add_score = Scored(match = insert_match)
        add_score.save()

def check_for_new_score():
    scores_list = get_scores()

    if scores_list == None:
        return None

    for item in scores_list:
        # No exception should occure due to insert_today_match function
        right_team = Team.objects.get(pk = item['rightplayer'])
        left_team = Team.objects.get(pk = item['leftplayer'])

        # Given two teams, find the match corresponding match
        current_match = Match.objects.get(RightTeam = right_team, LeftTeam = left_team, date=datetime.now().date())

        #Given match find the correspodning socre
        current_match_score = Scored.objects.get(match = current_match)
 
        # check to see if the score fetched from website is different
        # if it is differnt update the database 
        if current_match_score.leftScore != item[left_team.teamName]:
            current_match_score.leftScore = int(item[left_team.teamName])
            current_match_score.save()

        if current_match_score.rightScore != item[right_team.teamName]:
            current_match_score.rightScore = int(item[right_team.teamName])
            current_match_score.save()

if __name__ == "__main__":
	if sys.argv[1] == "insert":
		insert_today_match()
	else:
		check_for_new_score()