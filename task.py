from datetime import datetime

class Task():
    def __init__(self, name, duration, importance, deadType, desc="", deadline=None):
        self.n = name # string 
        self.duration = duration #integer (how long it will take)
        self.deadline = deadline # datetime object (day it is due. Only needed for "hard" deadlines)
        self.importance = importance #integer (1-10 for now)
        self.desc = desc # string (Description of the task)
        self.type = deadType #string ("hard", "soft" | used to differentiate between hard deadlines and flexible ones)
        self.score =1

    def findScore(self, urgencyWeight, impWeight): #finds the score that determines this task's priority
        now = datetime.now()
        if self.deadline is not None:
            timeLeft = (self.deadline - now).total_seconds() / 3600
            urgency = 1/max(timeLeft, 0.1)
        else:
            urgency = 0
        bonus = 2 if self.type == "hard" else 0
        score = (urgencyWeight * urgency) + (impWeight * self.importance) + bonus
        return score

