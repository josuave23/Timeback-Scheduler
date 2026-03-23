from task import Task
from schedule import Schedule
from datetime import datetime, timedelta

# test tasks
task1 = Task("Finish assignment", 90, 5, "hard", "study", datetime.now() + timedelta(hours=5))
task2 = Task("Do laundry", 120, 2, "soft", "chore", datetime.now() + timedelta(days=3))
task3 = Task("Review notes", 60, 3, "soft", "study", datetime.now() + timedelta(days=1))

# test schedule
from datetime import time
s = Schedule(
    tasks=[task1, task2, task3],
    dayStart=time(8, 0),
    dayEnd=time(22, 0),
    slotSize=5
)

timeline, unscheduled = s.genSchedule([])

for slot in timeline:
    if slot[2] is not None:
        print(f"{slot[0].strftime('%I:%M %p')} → {slot[2].n}")

print("Unscheduled:", [t.n for t in unscheduled])



