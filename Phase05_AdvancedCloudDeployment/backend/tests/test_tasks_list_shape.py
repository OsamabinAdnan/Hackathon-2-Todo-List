import pytest
from fastapi.testclient import TestClient


@pytest.mark.skip(reason="Backend tests require Postgres because Task.tags uses ARRAY; SQLite cannot compile ARRAY.")
def test_get_tasks_returns_array(client: TestClient):
    resp = client.get("/api/00000000-0000-0000-0000-000000000000/tasks")
    assert resp.status_code != 500

    if resp.status_code == 200:
        assert isinstance(resp.json(), list)
