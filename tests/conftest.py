from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Reset shared in-memory activity data between tests."""
    original_state = deepcopy(activities)
    try:
        yield
    finally:
        activities.clear()
        activities.update(deepcopy(original_state))


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
