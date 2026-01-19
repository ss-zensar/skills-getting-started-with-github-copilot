"""Tests for the Mergington High School Activities API"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original activities
    original = {
        "Basketball Team": {
            "description": "Competitive basketball team with practices and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in matches",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["sarah@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and mixed media techniques",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "lucas@mergington.edu"]
        },
        "Drama Club": {
            "description": "Participate in theatrical productions and performances",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["ava@mergington.edu", "ethan@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore STEM concepts",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 22,
            "participants": ["james@mergington.edu"]
        },
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
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original)
    
    yield
    
    # Reset after test
    activities.clear()
    activities.update(original)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Basketball Team" in data
        assert "Tennis Club" in data
    
    def test_get_activities_contains_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball Team"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_has_participants(self):
        """Test that activities have participants listed"""
        response = client.get("/activities")
        data = response.json()
        assert len(data["Basketball Team"]["participants"]) > 0
        assert "alex@mergington.edu" in data["Basketball Team"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self):
        """Test successfully signing up a new participant"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=newemail@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        participants = activities_response.json()["Basketball Team"]["participants"]
        assert "newemail@mergington.edu" in participants
    
    def test_signup_duplicate_participant_fails(self):
        """Test that signing up an already registered participant fails"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self):
        """Test that signing up for a non-existent activity fails"""
        response = client.post(
            "/activities/NonExistent/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_multiple_participants(self):
        """Test that multiple different participants can sign up"""
        emails = ["participant1@mergington.edu", "participant2@mergington.edu"]
        for email in emails:
            response = client.post(
                f"/activities/Tennis%20Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all were added
        activities_response = client.get("/activities")
        participants = activities_response.json()["Tennis Club"]["participants"]
        for email in emails:
            assert email in participants


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_success(self):
        """Test successfully unregistering an existing participant"""
        response = client.post(
            "/activities/Basketball%20Team/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        participants = activities_response.json()["Basketball Team"]["participants"]
        assert "alex@mergington.edu" not in participants
    
    def test_unregister_nonexistent_participant_fails(self):
        """Test that unregistering a non-registered participant fails"""
        response = client.post(
            "/activities/Basketball%20Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity_fails(self):
        """Test that unregistering from a non-existent activity fails"""
        response = client.post(
            "/activities/NonExistent/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_signup_and_unregister_flow(self):
        """Test complete flow of signing up and then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Drama%20Club"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify participant is registered
        activities_response = client.get("/activities")
        participants = activities_response.json()["Drama Club"]["participants"]
        assert email in participants
        
        # Unregister
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        participants = activities_response.json()["Drama Club"]["participants"]
        assert email not in participants


class TestIntegration:
    """Integration tests for the API"""
    
    def test_root_redirect(self):
        """Test that root path redirects to static content"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
    
    def test_activity_spots_calculation(self):
        """Test that available spots are calculated correctly"""
        response = client.get("/activities")
        data = response.json()
        
        # Basketball Team has 15 max and 1 participant, so 14 spots
        basketball = data["Basketball Team"]
        available_spots = basketball["max_participants"] - len(basketball["participants"])
        assert available_spots == 14
    
    def test_concurrent_signups_different_activities(self):
        """Test signing up the same user for different activities"""
        email = "multiactivity@mergington.edu"
        activities_list = ["Basketball%20Team", "Tennis%20Club", "Art%20Studio"]
        
        for activity in activities_list:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify participant is in all activities
        response = client.get("/activities")
        data = response.json()
        for activity_name in ["Basketball Team", "Tennis Club", "Art Studio"]:
            assert email in data[activity_name]["participants"]
