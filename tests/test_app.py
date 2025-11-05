import os
import importlib.util
from fastapi.testclient import TestClient


# Load app from src/app.py by file path to avoid package import issues
HERE = os.path.dirname(__file__)
APP_PATH = os.path.normpath(os.path.join(HERE, "..", "src", "app.py"))
spec = importlib.util.spec_from_file_location("app_mod", APP_PATH)
app_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_mod)
app = getattr(app_mod, "app")

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Basic sanity: known activity exists
    assert "Chess Club" in data


def test_signup_duplicate_and_unregister():
    activity = "Chess Club"
    email = "test.user+pytest@mergington.edu"

    # Ensure signup works
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200
    assert f"Signed up {email}" in r.json().get("message", "")

    # Duplicate signup should return 400
    r2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert r2.status_code == 400

    # Participant should be listed
    r3 = client.get("/activities")
    assert email in r3.json()[activity]["participants"]

    # Now unregister
    ru = client.post(f"/activities/{activity}/unregister?email={email}")
    assert ru.status_code == 200
    assert f"Unregistered {email}" in ru.json().get("message", "")

    # Verify removed
    r4 = client.get("/activities")
    assert email not in r4.json()[activity]["participants"]
