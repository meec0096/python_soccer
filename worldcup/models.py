from django.db import models
from datetime import datetime

class Team(models.Model):
    teamName = models.CharField(max_length=12, primary_key=True)
    isEliminated = models.BooleanField(default=False)
    totalGoals = models.IntegerField(default = 0)

    def __str__(self):
        return self.teamName 

class Match(models.Model):
    RightTeam = models.ForeignKey( Team, related_name = "rightteam",on_delete = models.CASCADE )
    LeftTeam = models.ForeignKey( Team, related_name = "leftteam", on_delete = models.CASCADE ) 
    date = models.DateField()

    def __str__(self):
        return "[ " + str(self.date) + "] : " + self.LeftTeam.teamName + " vs. " + self.RightTeam.teamName

class Scored(models.Model):
    match = models.ForeignKey(Match, on_delete = models.CASCADE)
    leftScore = models.IntegerField(default = 0)
    rightScore = models.IntegerField(default = 0)

    def __str__(self):
        return  self.match.LeftTeam.teamName + " : "+ str(self.leftScore) +  "-" + str(self.rightScore) + " : " + self.match.RightTeam.teamName

# Create your models here.
