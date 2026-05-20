import copy
import pytest
from fastapi.testclient import TestClient
from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state after each test"""
    original = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original))


def test_get_activities_returns_activities():
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    # Arrange
    activity = "Science Olympiad"
    email = "teststudent@example.com"

    # Act - signup
    signup_response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )
    # Assert
    assert signup_response.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]

    # Act - unregister
    unregister_response = client.delete(
        f"/activities/{activity}/signup", params={"email": email}
    )
    # Assert
    assert unregister_response.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity = "Chess Club"
    email = "duplicate@example.com"

    client.delete(f"/activities/{activity}/signup", params={"email": email})
    client.post(f"/activities/{activity}/signup", params={"email": email})

    # Act
    duplicate_response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )
    # Assert
    assert duplicate_response.status_code == 400


def test_activity_not_found_returns_404():
    # Arrange / Act
    response = client.post(
        "/activities/NoSuchActivity/signup", params={"email": "a@b.com"}
    )
    # Assert
    assert response.status_code == 404


def test_unregister_not_registered_returns_404():
    # Arrange
    activity = "Chess Club"
    email = "notregistered@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity}/signup", params={"email": email}
    )
    # Assert
    assert response.status_code == 404
