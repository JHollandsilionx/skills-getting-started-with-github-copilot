import pytest
from fastapi.testclient import TestClient
from src.app import app


# Original activities state for resetting between tests
ORIGINAL_ACTIVITIES = {
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
    "Basketball Team": {
        "description": "Competitive basketball league and practice",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu", "sarah@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn tennis skills and match play",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["alex@mergington.edu"]
    },
    "Art Studio": {
        "description": "Painting, drawing, and sculpture techniques",
        "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["sophia@mergington.edu", "rachel@mergington.edu"]
    },
    "Drama Club": {
        "description": "Theater performances and acting workshops",
        "schedule": "Thursdays, 3:30 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["david@mergington.edu", "isabella@mergington.edu"]
    },
    "Science Club": {
        "description": "Explore biology, chemistry, and physics experiments",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 18,
        "participants": ["lucas@mergington.edu", "noah@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 4:30 PM",
        "max_participants": 14,
        "participants": ["grace@mergington.edu", "ryan@mergington.edu"]
    }
}


@pytest.fixture
def client():
    """Fixture providing TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Fixture to reset activities to initial state before each test.
    
    This ensures test isolation - each test starts with the same
    initial activities state.
    """
    from src import app as app_module
    
    # Reset before test
    app_module.activities = {
        activity: {
            "description": data["description"],
            "schedule": data["schedule"],
            "max_participants": data["max_participants"],
            "participants": data["participants"].copy()  # Deep copy participants list
        }
        for activity, data in ORIGINAL_ACTIVITIES.items()
    }
    
    yield
    
    # Clean up after test (restore original state)
    app_module.activities = {
        activity: {
            "description": data["description"],
            "schedule": data["schedule"],
            "max_participants": data["max_participants"],
            "participants": data["participants"].copy()
        }
        for activity, data in ORIGINAL_ACTIVITIES.items()
    }
