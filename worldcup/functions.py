from bs4 import BeautifulSoup
import requests
import re
import os
import sys

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

    index = - 1
    score_dict = None
    # iterate through the minute list to find out if a game is currently playing
    # if note index == -1
    minute_list[1] = str(32)
    for i in range(len(minute_list)):
        if minute_list[i] != 'FT' and re.compile("[0-9][0-9]+:[0-9][0-9]+").match(minute_list[i]) == None:
            index = i
            break

    # if valid game is playing then construct dictionary with info
    # otherwise return none
    if index != -1:
        score_dict = {
            "rightplayer": str(rplayer_list[index]),
            "leftplayer": str(lplayer_list[index]),
            str(rplayer_list[index]): scores_list[index].split("-")[0],
            str(lplayer_list[index]): scores_list[index].split("-")[1],
            "minute": str(minute_list[index])   
        }

    return score_dict

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
    # No exception should occure due to insert_today_match function
    right_team = Team.objects.get(pk = scores_list['rightplayer'])
    left_team = Team.objects.get(pk = scores_list['leftplayer'])

    current_match = Team.objects.get(RightTeam = right_team, LeftTeam = left_team, date=date.now())

    current_match_score = Scoreds.objects.get(match = current_match)

    if current_match_score.LeftScore != scores_list[left_team.teamName]:
        current_match_score.update(LeftScore = int(scores_list[left_team.teamName]))

    if current_match_score.RightScore != scores_list[right_tream.teamName]:
        current_match_score.update(RightScore = int(scores_list[right_team.teamName]))

if __name__ == "__main__":
	if sys.argv[1] == "insert":
		insert_today_match()
	else:
		print(get_scores())
		check_for_new_score()
