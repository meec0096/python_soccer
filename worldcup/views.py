from django.shortcuts import render
from django.http import HttpResponse
from .models import Team,Match,Scored
from .scoreutils import get_scores
from datetime import datetime
from .twitter_functions import get_tweets
def index(request):
    score_list = get_scores()
    if score_list == None:
        return HttpResponse("No team is playing currently.")
    else:
        string = ""
        for item in score_list:
            lteam = Team.objects.get(pk = item['leftplayer'])
            rteam = Team.objects.get(pk = item['rightplayer'])

            curr_match = Match.objects.get(LeftTeam = lteam, RightTeam = rteam, date = datetime.now().date())

            scored = Scored.objects.get(match = curr_match)
            string += "Current " + str(curr_match) + str(scored) + "\n\n"
        
        return HttpResponse(string)

def twitterfeed(request):
    tweetList = get_tweets('world cup')
    #return HttpResponse(str(tweetList))
    return render(request, 'twitter.html', {'tweet_list': tweetList})
# Create your views here. 