import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Test client fixture for FastAPI app"""
    return TestClient(app)


def test_get_activities(client):
    """Test GET /activities returns all activities with correct structure"""
    # Arrange - client fixture provides the test client

    # Act - make request to get activities
    response = client.get("/activities")

    # Assert - check response status and content
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 9  # Should have 9 activities
    assert "Chess Club" in data
    assert "Programming Class" in data

    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    # Arrange - prepare test data
    activity_name = "Chess Club"
    email = "test@example.com"

    # Act - attempt to sign up
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert - check success response and state change
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    # Verify the participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email in activities_data[activity_name]["participants"]


def test_signup_duplicate_participant(client):
    """Test signup fails when student is already signed up"""
    # Arrange - use an email that's already signed up
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Already in participants

    # Act - attempt duplicate signup
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert - check error response
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up"}


def test_signup_invalid_activity(client):
    """Test signup fails for non-existent activity"""
    # Arrange - use invalid activity name
    activity_name = "Invalid Activity"
    email = "test@example.com"

    # Act - attempt signup for invalid activity
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert - check error response
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_participant_success(client):
    """Test successful unregistration from an activity"""
    # Arrange - first sign up a participant
    activity_name = "Programming Class"
    email = "test@example.com"
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Act - unregister the participant
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert - check success response and state change
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}

    # Verify the participant was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert email not in activities_data[activity_name]["participants"]


def test_unregister_not_signed_up(client):
    """Test unregistration fails when student is not signed up"""
    # Arrange - use email not in participants
    activity_name = "Programming Class"
    email = "notsigned@example.com"

    # Act - attempt to unregister non-participant
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert - check error response
    assert response.status_code == 404
    assert response.json() == {"detail": "Student not signed up for this activity"}


def test_unregister_invalid_activity(client):
    """Test unregistration fails for non-existent activity"""
    # Arrange - use invalid activity name
    activity_name = "Invalid Activity"
    email = "test@example.com"

    # Act - attempt unregister from invalid activity
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert - check error response
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_root_redirect(client):
    """Test root endpoint redirects to static index"""
    # Arrange - client fixture provides the test client

    # Act - make request to root
    response = client.get("/")

    # Assert - check redirect response
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"