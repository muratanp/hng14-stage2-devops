import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient


# Patch redis.Redis before importing main so the module-level connection is mocked
@pytest.fixture(scope="module")
def mock_redis_class():
    with patch("redis.Redis") as mock_cls:
        mock_cls.return_value = MagicMock()
        yield mock_cls.return_value


@pytest.fixture(scope="module")
def client(mock_redis_class):
    # Import here so the patch is already active
    from main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_redis(mock_redis_class):
    mock_redis_class.reset_mock()


# Test 1: POST /jobs creates a job and returns a job_id
def test_create_job_returns_job_id(client, mock_redis_class):
    mock_redis_class.lpush.return_value = 1
    mock_redis_class.hset.return_value = 1

    response = client.post("/jobs")

    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert len(data["job_id"]) == 36  # UUID4 length


# Test 2: POST /jobs pushes to the correct Redis queue
def test_create_job_pushes_to_queue(client, mock_redis_class):
    mock_redis_class.lpush.return_value = 1
    mock_redis_class.hset.return_value = 1

    response = client.post("/jobs")
    job_id = response.json()["job_id"]

    mock_redis_class.lpush.assert_called_once_with("jobs", job_id)
    mock_redis_class.hset.assert_called_once_with(f"job:{job_id}", "status", "queued")


# Test 3: GET /jobs/{id} returns status when job exists
def test_get_job_found(client, mock_redis_class):
    mock_redis_class.hget.return_value = b"queued"

    response = client.get("/jobs/some-job-id")

    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == "some-job-id"
    assert data["status"] == "queued"


# Test 4: GET /jobs/{id} returns 404 for unknown jobs
def test_get_job_not_found(client, mock_redis_class):
    mock_redis_class.hget.return_value = None

    response = client.get("/jobs/does-not-exist")

    assert response.status_code == 404
    assert "detail" in response.json()


# Test 5: GET /health pings Redis and returns ok
def test_health_endpoint(client, mock_redis_class):
    mock_redis_class.ping.return_value = True

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    mock_redis_class.ping.assert_called_once()