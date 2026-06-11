"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Team training and competitive matches for aspiring soccer players",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["maria@mergington.edu", "alex@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Build swimming skills, technique, and endurance in the pool",
        "schedule": "Mondays and Wednesdays, 3:00 PM - 4:30 PM",
        "max_participants": 16,
        "participants": ["nina@mergington.edu", "kevin@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore drawing, painting, and other visual arts projects",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
    },
    "Drama Club": {
        "description": "Practice acting, stage production, and performance skills",
        "schedule": "Thursdays, 4:30 PM - 6:00 PM",
        "max_participants": 20,
        "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop argumentation, public speaking, and research skills",
        "schedule": "Tuesdays, 5:00 PM - 6:30 PM",
        "max_participants": 15,
        "participants": ["oliver@mergington.edu", "ava@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts together",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["liam@mergington.edu", "emma2@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
   """Sign up a student for an activity"""
   # Validate activity exists
   if activity_name not in activities:
      raise HTTPException(status_code=404, detail="Activity not found")

   # Get the activity
   activity = activities[activity_name]

   # Validate student is not already signed up
   if email in activity["participants"]:
     raise HTTPException(status_code=400, detail="Student is already signed up")

   # Add student
   activity["participants"].append(email)
   return {"message": f"Signed up {email} for {activity_name}"}
