"""
Comprehensive test suite for Mergington High School Activities API.

Tests use the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and state
- Act: Execute the operation being tested
- Assert: Verify the results
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Root path should redirect to static index.html"""
        # Arrange: No setup needed for redirect test
        
        # Act: Get root path
        response = client.get("/", follow_redirects=False)
        
        # Assert: Check for redirect status and location
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_returns_nine_activities(self, client):
        """Fetching activities should return all 9 activities."""
        # Arrange: No extra setup needed, client fixture provides default activities
        
        # Act: Fetch all activities
        response = client.get("/activities")
        
        # Assert: Verify response and data
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Debate Team" in activities
    
    def test_activity_has_required_fields(self, client):
        """Each activity should have all required fields."""
        # Arrange: Expected activity fields
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act: Fetch activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Verify each activity has required structure
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_participants_are_emails(self, client):
        """Participants should be email strings."""
        # Arrange: Get activities
        response = client.get("/activities")
        activities = response.json()
        
        # Act & Assert: Verify participants contain email format
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                assert "@" in participant
                assert isinstance(participant, str)
    
    def test_activities_have_correct_initial_participants(self, client):
        """Verify specific activities have expected initial participants."""
        # Arrange: Expected initial states
        expected_states = {
            "Chess Club": ["michael@mergington.edu", "daniel@mergington.edu"],
            "Tennis Club": ["alex@mergington.edu"],
            "Art Studio": ["sophia@mergington.edu", "rachel@mergington.edu"],
        }
        
        # Act: Get activities
        response = client.get("/activities")
        activities = response.json()
        
        # Assert: Verify participants
        for activity_name, expected_participants in expected_states.items():
            assert activities[activity_name]["participants"] == expected_participants


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_student_successfully_signs_up(self, client):
        """A student should successfully sign up for an activity."""
        # Arrange: Known activity and new student email
        activity_name = "Chess Club"
        new_student_email = "student@mergington.edu"
        
        # Act: Sign up student
        response = client.post(
            f"/activities/{activity_name}/signup?email={new_student_email}"
        )
        
        # Assert: Verify success and message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_student_email in data["message"]
        assert activity_name in data["message"]
    
    def test_new_participant_added_to_activity(self, client):
        """New participant should appear in activity's participant list."""
        # Arrange: Get initial participants count
        activity_name = "Tennis Club"
        new_student_email = "tennis@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act: Sign up student
        client.post(f"/activities/{activity_name}/signup?email={new_student_email}")
        
        # Assert: Verify participant was added
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity_name]["participants"])
        assert updated_count == initial_count + 1
        assert new_student_email in updated_response.json()[activity_name]["participants"]
    
    def test_duplicate_signup_returns_400(self, client):
        """Signing up the same student twice should return 400 error."""
        # Arrange: Use existing participant
        activity_name = "Chess Club"
        existing_student = "michael@mergington.edu"
        
        # Act: Try to sign up same student again
        response = client.post(
            f"/activities/{activity_name}/signup?email={existing_student}"
        )
        
        # Assert: Verify 400 error for duplicate
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_with_nonexistent_activity_returns_404(self, client):
        """Signing up for non-existent activity should return 404 error."""
        # Arrange: Invalid activity name
        invalid_activity = "Nonexistent Club"
        student_email = "student@mergington.edu"
        
        # Act: Try to sign up for non-existent activity
        response = client.post(
            f"/activities/{invalid_activity}/signup?email={student_email}"
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_with_special_characters_in_email(self, client):
        """Email with special characters should be accepted when properly URL encoded."""
        # Arrange: Email with + character (must be URL encoded as %2B in query params)
        activity_name = "Drama Club"
        special_email = "student+test@mergington.edu"
        
        # Act: Sign up with special character email (properly URL encoded)
        response = client.post(
            f"/activities/{activity_name}/signup?email=student%2Btest@mergington.edu"
        )
        
        # Assert: Should succeed (app accepts any string as email)
        assert response.status_code == 200
        updated_response = client.get("/activities")
        assert special_email in updated_response.json()[activity_name]["participants"]
    
    def test_signup_multiple_different_students_same_activity(self, client):
        """Multiple different students should be able to sign up for same activity."""
        # Arrange: Activity and multiple new students
        activity_name = "Science Club"
        new_students = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        
        # Act: Sign up all students
        for student in new_students:
            response = client.post(
                f"/activities/{activity_name}/signup?email={student}"
            )
            assert response.status_code == 200
        
        # Assert: All students should be in participant list
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        for student in new_students:
            assert student in participants
    
    def test_signup_response_format(self, client):
        """Signup response should have proper message format."""
        # Arrange: Test data
        activity_name = "Basketball Team"
        email = "player@mergington.edu"
        
        # Act: Sign up
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Check response format
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert f"Signed up {email}" in data["message"]
        assert activity_name in data["message"]


class TestRemoveEndpoint:
    """Tests for DELETE /activities/{activity_name}/remove endpoint"""
    
    def test_participant_successfully_removed(self, client):
        """An existing participant should be successfully removed."""
        # Arrange: Use existing participant
        activity_name = "Chess Club"
        participant_to_remove = "michael@mergington.edu"
        
        # Act: Remove participant
        response = client.delete(
            f"/activities/{activity_name}/remove?email={participant_to_remove}"
        )
        
        # Assert: Verify success
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
    
    def test_participant_removed_from_list(self, client):
        """Participant should no longer appear in activity list after removal."""
        # Arrange: Get initial participant count
        activity_name = "Art Studio"
        participant_to_remove = "sophia@mergington.edu"
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act: Remove participant
        client.delete(
            f"/activities/{activity_name}/remove?email={participant_to_remove}"
        )
        
        # Assert: Verify participant was removed
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity_name]["participants"])
        assert updated_count == initial_count - 1
        assert participant_to_remove not in updated_response.json()[activity_name]["participants"]
    
    def test_remove_from_nonexistent_activity_returns_404(self, client):
        """Removing from non-existent activity should return 404."""
        # Arrange: Invalid activity name
        invalid_activity = "Nonexistent Club"
        student_email = "student@mergington.edu"
        
        # Act: Try to remove from non-existent activity
        response = client.delete(
            f"/activities/{invalid_activity}/remove?email={student_email}"
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_remove_nonexistent_participant_returns_404(self, client):
        """Removing non-existent participant should return 404."""
        # Arrange: Valid activity but non-existent participant
        activity_name = "Programming Class"
        nonexistent_email = "nonexistent@mergington.edu"
        
        # Act: Try to remove non-existent participant
        response = client.delete(
            f"/activities/{activity_name}/remove?email={nonexistent_email}"
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_remove_response_format(self, client):
        """Remove response should have proper message format."""
        # Arrange: Test data
        activity_name = "Drama Club"
        email = "david@mergington.edu"
        
        # Act: Remove
        response = client.delete(
            f"/activities/{activity_name}/remove?email={email}"
        )
        
        # Assert: Check response format
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert f"Removed {email}" in data["message"]
        assert activity_name in data["message"]


class TestIntegration:
    """Integration tests for signup and remove workflows"""
    
    def test_signup_then_verify_in_get_activities(self, client):
        """New participant should appear in activities after signup."""
        # Arrange: New student and activity
        activity_name = "Science Club"
        new_student = "integration@mergington.edu"
        
        # Act: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={new_student}"
        )
        assert signup_response.status_code == 200
        
        # Assert: Verify in activities list
        activities_response = client.get("/activities")
        assert new_student in activities_response.json()[activity_name]["participants"]
    
    def test_remove_then_verify_in_get_activities(self, client):
        """Participant should not appear in activities after removal."""
        # Arrange: Existing participant to remove
        activity_name = "Debate Team"
        participant = "grace@mergington.edu"
        
        # Act: Remove participant
        remove_response = client.delete(
            f"/activities/{activity_name}/remove?email={participant}"
        )
        assert remove_response.status_code == 200
        
        # Assert: Verify not in activities list
        activities_response = client.get("/activities")
        assert participant not in activities_response.json()[activity_name]["participants"]
    
    def test_signup_and_remove_cycle(self, client):
        """Student should be able to sign up and then be removed."""
        # Arrange: Test student
        activity_name = "Basketball Team"
        test_student = "cycle@mergington.edu"
        
        # Act: Sign up
        signup_resp = client.post(
            f"/activities/{activity_name}/signup?email={test_student}"
        )
        assert signup_resp.status_code == 200
        
        # Assert: Verify signed up
        get_resp_1 = client.get("/activities")
        assert test_student in get_resp_1.json()[activity_name]["participants"]
        
        # Act: Remove
        remove_resp = client.delete(
            f"/activities/{activity_name}/remove?email={test_student}"
        )
        assert remove_resp.status_code == 200
        
        # Assert: Verify removed
        get_resp_2 = client.get("/activities")
        assert test_student not in get_resp_2.json()[activity_name]["participants"]
    
    def test_multiple_students_signup(self, client):
        """Multiple students should be able to sign up to same activity."""
        # Arrange: Multiple new students
        activity_name = "Drama Club"
        students = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        
        # Act: Sign up all students
        for student in students:
            response = client.post(
                f"/activities/{activity_name}/signup?email={student}"
            )
            assert response.status_code == 200
        
        # Assert: All in participant list
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity_name]["participants"]
        for student in students:
            assert student in participants
    
    def test_signup_remove_signup_same_student(self, client):
        """Student should be able to re-signup after being removed."""
        # Arrange: Test data
        activity_name = "Tennis Club"
        student = "retest@mergington.edu"
        
        # Act: First sign up
        client.post(f"/activities/{activity_name}/signup?email={student}")
        
        # Assert: Appears in list
        resp1 = client.get("/activities")
        assert student in resp1.json()[activity_name]["participants"]
        
        # Act: Remove
        client.delete(f"/activities/{activity_name}/remove?email={student}")
        
        # Assert: Gone from list
        resp2 = client.get("/activities")
        assert student not in resp2.json()[activity_name]["participants"]
        
        # Act: Sign up again
        client.post(f"/activities/{activity_name}/signup?email={student}")
        
        # Assert: Back in list
        resp3 = client.get("/activities")
        assert student in resp3.json()[activity_name]["participants"]
    
    def test_participant_count_accuracy(self, client):
        """Participant count should accurately reflect additions and removals."""
        # Arrange: Track counts
        activity_name = "Gym Class"
        
        # Act & Assert: Get initial count
        resp1 = client.get("/activities")
        initial_count = len(resp1.json()[activity_name]["participants"])
        
        # Act: Add 2 participants
        client.post(f"/activities/{activity_name}/signup?email=test1@test.edu")
        client.post(f"/activities/{activity_name}/signup?email=test2@test.edu")
        
        # Assert: Count increased by 2
        resp2 = client.get("/activities")
        assert len(resp2.json()[activity_name]["participants"]) == initial_count + 2
        
        # Act: Remove 1 participant
        client.delete(f"/activities/{activity_name}/remove?email=test1@test.edu")
        
        # Assert: Count back to initial + 1
        resp3 = client.get("/activities")
        assert len(resp3.json()[activity_name]["participants"]) == initial_count + 1
