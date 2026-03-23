from datetime import datetime, time, date, timedelta
import math

class Schedule():
    def __init__(self, tasks, dayStart, dayEnd, slotSize, urgencyWeight=0.5, impWeight=0.5, blackouts = [], recBreaks = []): #weight values need to be variable in the end
        self.tasks = tasks #list; list of all tasks in this schedule
        self.start = dayStart #time; time that each day will start
        self.end = dayEnd #time; time that each day ends
        self.slotSize = slotSize #int; the size of each time "block" (in this case likely 5 minutes)
        self.timeline = [] #list; each entry is a timeslot (basically this is the full schedule)
        self.urgencyWeight = urgencyWeight #float; user preference
        self.impWeight = impWeight #float; user preference
        self.unscheduled = []
        self.blackouts = blackouts #one time breaks manually set
        self.rb = recBreaks #reccuring breaks


    def buildTimeline(self, numDays): #temp default, eventually should make either user inputted or the last deadline
        now = datetime.now()
        for i in range(numDays):
            dayStart = datetime.combine(date.today() + timedelta(days=i), self.start)
            dayEnd = datetime.combine(date.today() + timedelta(days=i), self.end)
            current = dayStart
            while current < dayEnd:
                if current > now:
                    self.timeline.append([current, True, None])
                current += timedelta(minutes=self.slotSize)

    def blockRecurringBreaks(self):
        for slot in self.timeline:
            for b in self.rb:
                slotTime = slot[0].time()
                if slotTime >= b["start"] and slotTime < b["end"]:
                    slot[1] = False

    def blockBlackouts(self):
        for slot in self.timeline:
            for b in self.blackouts:
                if slot[0] >= b["start"] and slot[0] < b["end"]:
                    slot[1] = False
                    
    def blockEvents(self, events):
        for event in events:
            for i in range(len(self.timeline)):
                if self.timeline[i][0] >= event["start"] and self.timeline[i][0] < event["end"]:
                    self.timeline[i][1] = False

    def scoreTasks(self):
        h = []
        nh = []
        for task in self.tasks:
            task.score = task.findScore(self.urgencyWeight, self.impWeight)
            if task.type == "hard":
                h.append(task)
            elif task.type == "soft":
                nh.append(task)
        return h+nh
    
    def findEarliestSlot(self, slotsNeeded):
        for i in range(len(self.timeline) - slotsNeeded + 1):
            if all(self.timeline[j][1] == True for j in range(i, i + slotsNeeded)):
                return i
        return None #error that not enought slots

    def findLatestSlot(self, slotsNeeded, deadline):
        deadlineIdx = 0
        for i in range(len(self.timeline)):
            if self.timeline[i][0] <= deadline:
                deadlineIdx = i
            else:
                break
        for i in range(deadlineIdx - slotsNeeded, -1, -1):
            if all(self.timeline[j][1] == True for j in range(i, i + slotsNeeded)):
                return i
        return None #not enought slots
    
    def assignSlot(self, task, startIdx, slotsNeeded):
        for i in range(startIdx, startIdx + slotsNeeded):
            self.timeline[i][1] = False
            self.timeline[i][2] = task

    def assignSplitTask(self, task, slotsNeeded):
        remaining = slotsNeeded
        for i in range(len(self.timeline)):
            if remaining == 0:
                break
            if self.timeline[i][1] == True:
                self.timeline[i][1] = False
                self.timeline[i][2] = task
                remaining -= 1
        if remaining > 0:
            self.unscheduled.append(task)

    def genSchedule(self, calendarEvents, numDays=7):
        self.buildTimeline(numDays)
        self.blockRecurringBreaks()
        self.blockBlackouts()
        self.blockEvents(calendarEvents)
        scored = self.scoreTasks()

        for task in scored:
            slotsNeeded = math.ceil(task.duration / self.slotSize)
            if task.type == "hard":
                idx = self.findLatestSlot(slotsNeeded, task.deadline)
                if idx is not None:
                    self.assignSlot(task, idx, slotsNeeded)
                else:
                    self.assignSplitTask(task, slotsNeeded)
            else:
                idx = self.findEarliestSlot(slotsNeeded)
                if idx is not None:
                    self.assignSlot(task, idx, slotsNeeded)
                else:
                    self.assignSplitTask(task, slotsNeeded)

        return self.timeline, self.unscheduled  
