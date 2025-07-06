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
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.mergington_high
activities_collection = db.activities

# Initialize data if collection is empty
async def init_db():
    count = await activities_collection.count_documents({})
    if count == 0:
        initial_activities = {
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
    # Sports related activities
    "Soccer Team": {
        "description": "Join the school soccer team and compete in local leagues",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 18,
        "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
    },
    "Basketball Club": {
        "description": "Practice basketball skills and play friendly matches",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["liam@mergington.edu", "ava@mergington.edu"]
    },
    # Artistic activities
    "Drama Club": {
        "description": "Act, direct, and participate in school theater productions",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Workshop": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
    },
    # Intellectual activities
    "Math Olympiad": {
        "description": "Prepare for math competitions and solve challenging problems",
        "schedule": "Fridays, 2:00 PM - 3:30 PM",
        "max_participants": 15,
        "participants": ["charlotte@mergington.edu", "elijah@mergington.edu"]
    },
    "Science Club": {
        "description": "Conduct experiments and explore scientific concepts",
        "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["william@mergington.edu", "harper@mergington.edu"]
    }
}
        for name, details in initial_activities.items():
            await activities_collection.insert_one({"_id": name, **details})

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
async def get_activities():
    cursor = activities_collection.find({})
    activities_list = await cursor.to_list(length=100)
    return {doc["_id"]: {k: v for k, v in doc.items() if k != "_id"} for doc in activities_list}


@app.post("/activities/{activity_name}/signup")
async def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists and student is not already signed up
    activity = await activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student already signed up")

    # Update activity with new participant
    result = await activities_collection.update_one(
        {"_id": activity_name},
        {"$push": {"participants": email}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update activity")
        
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
async def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    activity = await activities_collection.find_one({"_id": activity_name})
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if email not in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is not registered for this activity")

    # Remove student from activity
    result = await activities_collection.update_one(
        {"_id": activity_name},
        {"$pull": {"participants": email}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to unregister student")
        
    return {"message": f"Unregistered {email} from {activity_name}"}
