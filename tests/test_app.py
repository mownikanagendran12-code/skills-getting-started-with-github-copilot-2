from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity: known activity present
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "pytest_user@example.com"

    # ensure not already present
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity].get("participants", [])
    if email in participants:
        # remove if leftover from previous run
        client.post(f"/activities/{quote(activity)}/unregister", params={"email": email})

    # signup
    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in resp.json().get("message", "")

    # verify present in list
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity].get("participants", [])
    assert email in participants

    # duplicate signup should fail
    resp = client.post(f"/activities/{quote(activity)}/signup", params={"email": email})
    assert resp.status_code == 400

    # unregister
    resp = client.post(f"/activities/{quote(activity)}/unregister", params={"email": email})
    assert resp.status_code == 200
    assert "Unregistered" in resp.json().get("message", "")

    # verify removed
    resp = client.get("/activities")
    participants = resp.json()[activity].get("participants", [])
    assert email not in participants
