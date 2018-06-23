from django.shortcuts import render
from django.http import HttpResponse
from .models import Team,Match,Scored
from .functions import get_scores
from datetime import datetime
def index(request):
    score_list = get_scores()
    print(score_list)
    if score_list == None:
        return HttpResponse("No team is playing currently.")
    
    lteam = Team.objects.get(pk = score_list['leftplayer'])
    rteam = Team.objects.get(pk = score_list['rightplayer'])

    curr_match = Match.objects.get(LeftTeam = lteam, RightTeam = rteam, date = datetime.now().date())

    scored = Scored.objects.get(match = curr_match)
    string = "Current " + str(curr_match) + str(scored)
    return HttpResponse(string)
# Create your views here.