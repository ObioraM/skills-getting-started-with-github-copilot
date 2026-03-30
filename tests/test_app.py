from urllib.parse import quote


def activity_signup_path(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/signup"


def activity_unregister_path(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/participants"


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_map(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "participants" in payload["Chess Club"]


def test_signup_adds_new_participant(client):
    activity_name = "Chess Club"
    email = "new_student@mergington.edu"

    response = client.post(activity_signup_path(activity_name), params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_rejects_duplicate_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(activity_signup_path(activity_name), params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_rejects_unknown_activity(client):
    response = client.post(activity_signup_path("Unknown Activity"), params={"email": "a@b.com"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_existing_participant(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(activity_unregister_path(activity_name), params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(activity_unregister_path("Unknown Activity"), params={"email": "a@b.com"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_unknown_participant(client):
    activity_name = "Chess Club"
    email = "not-registered@mergington.edu"

    response = client.delete(activity_unregister_path(activity_name), params={"email": email})

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
