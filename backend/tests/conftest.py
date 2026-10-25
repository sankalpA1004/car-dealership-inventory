import os
import tempfile
import pytest
from fastapi.testclient import TestClient

@pytest.fixture()
def client(monkeypatch):
    # Import after setting the test database URL so each test run is isolated.
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    from app.database import Base, get_db
    from app.main import app
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)
    def override_get_db():
        db = TestingSession()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture()
def user_token(client):
    response = client.post("/api/auth/register", json={"email":"customer@example.com","full_name":"Test Customer","password":"strong-pass-123"})
    assert response.status_code == 201
    return response.json()["access_token"]

@pytest.fixture()
def admin_token(client):
    # Admin creation is deliberately a local-development bootstrap operation, not a public API.
    from app.database import get_db
    from app.models import User
    from app.security import hash_password, create_access_token
    from app.main import app
    generator = app.dependency_overrides[get_db]()
    db = next(generator)
    admin = User(email="admin@example.com", full_name="Test Admin", hashed_password=hash_password("admin-pass-123"), is_admin=True)
    db.add(admin); db.commit(); db.refresh(admin)
    token = create_access_token(str(admin.id))
    db.close()
    try: generator.close()
    except Exception: pass
    return token
