from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities as APP_ACTIVITIES


# Original activities state for resetting between tests
ORIGINAL_ACTIVITIES = deepcopy(APP_ACTIVITIES)


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
