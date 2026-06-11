"""Tests for the FastAPI activities application

Uses the AAA (Arrange-Act-Assert) testing pattern:
- Arrange: Set up test data and conditions
- Act: Execute the code being tested
- Assert: Verify the results
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


# Create a test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities before each test"""
    global activities
    activities.clear()
    activities.update({
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
            "participants": ["emma@mergington.edu"]
        }
    })
    yield


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self):
        """Should return all activities"""
        # Arrange
        # (activities fixture is already set up)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
        
    def test_get_activities_includes_participants(self):
        """Should include participants list for each activity"""
        # Arrange
        expected_count = 2
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert "participants" in data["Chess Club"]
        assert len(data["Chess Club"]["participants"]) == expected_count
        
    def test_get_activities_includes_activity_details(self):
        """Should include all activity details"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        for field in required_fields:
            assert field in activity


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_valid_student(self):
        """Should successfully sign up a new student"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess%20Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        
    def test_signup_adds_participant_to_list(self):
        """Should add participant to the activity's participants list"""
        # Arrange
        email = "newcomer@mergington.edu"
        activity = "Programming%20Class"
        
        # Act
        client.post(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")
        
        # Assert
        participants = response.json()["Programming Class"]["participants"]
        assert email in participants
        
    def test_signup_duplicate_student_rejected(self):
        """Should reject duplicate signup - BUG FIX VERIFICATION"""
        # Arrange
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        activity = "Chess%20Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
        
    def test_signup_activity_not_found(self):
        """Should return 404 for non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        activity = "Nonexistent%20Club"
        expected_status = 404
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == expected_status
        data = response.json()
        assert "Activity not found" in data["detail"]
        
    def test_signup_multiple_students_different_activities(self):
        """Should allow same student to sign up for different activities"""
        # Arrange
        email = "test@mergington.edu"
        activity1 = "Chess%20Club"
        activity2 = "Programming%20Class"
        
        # Act
        response1 = client.post(f"/activities/{activity1}/signup?email={email}")
        response2 = client.post(f"/activities/{activity2}/signup?email={email}")
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_unregister_existing_participant(self):
        """Should successfully remove a participant"""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess%20Club"
        
        # Act
        response = client.delete(f"/activities/{activity}/participants/{email}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
    def test_unregister_removes_from_list(self):
        """Should remove participant from activity's participants list"""
        # Arrange
        email = "daniel@mergington.edu"
        activity = "Chess%20Club"
        
        # Act
        client.delete(f"/activities/{activity}/participants/{email}")
        response = client.get("/activities")
        
        # Assert
        participants = response.json()["Chess Club"]["participants"]
        assert email not in participants
        
    def test_unregister_participant_not_found(self):
        """Should return 404 when trying to remove non-participant"""
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess%20Club"
        expected_status = 404
        
        # Act
        response = client.delete(f"/activities/{activity}/participants/{email}")
        
        # Assert
        assert response.status_code == expected_status
        data = response.json()
        assert "Participant not found" in data["detail"]
        
    def test_unregister_activity_not_found(self):
        """Should return 404 for non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        activity = "Nonexistent%20Club"
        expected_status = 404
        
        # Act
        response = client.delete(f"/activities/{activity}/participants/{email}")
        
        # Assert
        assert response.status_code == expected_status
        
    def test_unregister_can_re_signup_after_removal(self):
        """Should allow re-signup after being unregistered"""
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess%20Club"
        
        # Act - Remove participant
        client.delete(f"/activities/{activity}/participants/{email}")
        
        # Act - Re-sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200


class TestIntegrationWorkflows:
    """Integration tests using AAA pattern for complete workflows"""
    
    def test_signup_and_view_participant(self):
        """Complete flow: signup then view participant in activity"""
        # Arrange
        email = "alice@mergington.edu"
        activity = "Chess%20Club"
        
        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        
        # Act - View activities
        view_response = client.get("/activities")
        
        # Assert
        assert signup_response.status_code == 200
        participants = view_response.json()["Chess Club"]["participants"]
        assert email in participants
        
    def test_signup_unregister_workflow(self):
        """Complete flow: signup, verify, unregister, verify gone"""
        # Arrange
        email = "bob@mergington.edu"
        activity = "Programming%20Class"
        
        # Act 1 - Verify not present initially
        response = client.get("/activities")
        initial_participants = response.json()["Programming Class"]["participants"]
        
        # Assert 1
        assert email not in initial_participants
        
        # Act 2 - Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")
        
        # Assert 2
        signed_up_participants = response.json()["Programming Class"]["participants"]
        assert email in signed_up_participants
        
        # Act 3 - Unregister
        client.delete(f"/activities/{activity}/participants/{email}")
        response = client.get("/activities")
        
        # Assert 3
        final_participants = response.json()["Programming Class"]["participants"]
        assert email not in final_participants
        
    def test_full_activity_lifecycle(self):
        """Full lifecycle: multiple signups and removals"""
        # Arrange
        students = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        activity = "Programming%20Class"
        initial_count = len(activities["Programming Class"]["participants"])
        
        # Act - Sign up three students
        for student in students:
            client.post(f"/activities/{activity}/signup?email={student}")
        
        # Assert - All three added
        response = client.get("/activities")
        participants = response.json()["Programming Class"]["participants"]
        assert len(participants) == initial_count + 3
        for student in students:
            assert student in participants
        
        # Act - Remove middle student
        client.delete(f"/activities/{activity}/participants/{students[1]}")
        
        # Assert - Correct student removed
        response = client.get("/activities")
        participants = response.json()["Programming Class"]["participants"]
        assert len(participants) == initial_count + 2
        assert students[0] in participants
        assert students[1] not in participants
        assert students[2] in participants
