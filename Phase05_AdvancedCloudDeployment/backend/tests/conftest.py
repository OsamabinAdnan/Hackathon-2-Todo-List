import pytest
from sqlmodel import Session, SQLModel, create_engine
from fastapi.testclient import TestClient

from app.database import get_session
from main import app


@pytest.fixture(name="session")
def session_fixture():
    # NOTE:
    # The Task model uses PostgreSQL ARRAY for tags.
    # SQLite cannot compile ARRAY, so for local pytest we use an in-memory Postgres
    # or run against Postgres in CI. Until then, backend tests that touch the DB
    # should be skipped.
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False},
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
