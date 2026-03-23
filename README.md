# ScheduleGen
### Functional

A passion project I am working on to help people manage their time better. 

Note: Version 1.0.0 is identical to my public submission for the BeachHacks 9.0 hackathon, which is public on my page. This is the repo in which I will continue development on this project

## Current Version: 1.0.0

## Setup
After download, ensure that main.py, schedule.py. task.py, gcal.py, and ui.py are all in the same folder

Then, follow these steps:
1. Go to https://console.cloud.google.com
2. Create a new project and enable the Google Calendar API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download the credentials file and rename it to `credentials.json`
5. Place it in the project root
6. Run `pip install -r requirements.txt`
7. Run `python main.py` — a browser window will open to authenticate

## To Implement:
- Implement a calandar program for this to run on
- UI changes for an easier user experience
- Implement an easy way to manually block out timeslots for breaks
- Add Canvas API
