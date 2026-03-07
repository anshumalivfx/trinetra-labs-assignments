"""
Sample Test File
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["service"] == "AI Agent Orchestration System"


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "AI Agent Orchestration System"


def test_upload_invalid_file(test_db):
    """Test upload with invalid file type"""
    files = {"file": ("test.txt", b"not a pdf", "text/plain")}
    data = {"recipient_email": "test@example.com", "user_id": 1}
    
    response = client.post("/api/v1/documents/upload", files=files, data=data)
    assert response.status_code == 400


def test_get_nonexistent_job():
    """Test getting non-existent job"""
    response = client.get("/api/v1/jobs/nonexistent-job-id")
    assert response.status_code == 404
