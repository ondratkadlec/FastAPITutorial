from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

from app import database, models
from app.config import settings
from app.main import app
from app.oauth2 import create_access_token

TEST_SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/testingdb'

testing_engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)
if not database_exists(testing_engine.url):
    create_database(testing_engine.url)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=testing_engine)

@pytest.fixture
def testing_session():
    database.Base.metadata.drop_all(bind=testing_engine)
    database.Base.metadata.create_all(bind=testing_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def testing_client(testing_session):
    def override_get_db():
        try:
            yield testing_session
        finally:
            testing_session.close()

    app.dependency_overrides[database.get_db] = override_get_db
    yield TestClient(app)

@pytest.fixture
def test_user(testing_client):
    user_data = {"email": "sanjeev@gmail.com",
                 "password": "password123"}
    res = testing_client.post("/user/", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def test_user2(testing_client):
    user_data = {"email": "andrew@gmail.com",
                 "password": "YouShallNotPass"}
    res = testing_client.post("/user/", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})

@pytest.fixture
def authorized_testing_client(testing_client, token):
    testing_client.headers = {
        **testing_client.headers,
        "Authorization": f"Bearer {token}",
    }
    return testing_client

@pytest.fixture
def test_posts(test_user, test_user2, testing_session):
    posts_data = [
        {
            "title": "first title",
            "content": "first content",
            "owner_id": test_user['id']
        },
        {
            "title": "2nd title",
            "content": "2nd content",
            "owner_id": test_user['id']
        },
        {
            "title": "3rd title",
            "content": "3rd content",
            "owner_id": test_user['id']
        },
        {
            "title": "4th title",
            "content": "4th content",
            "owner_id": test_user2['id']
        }
    ]

    def create_post_model(post):
        return models.Post(**post)

    post_map = map(create_post_model, posts_data)
    posts = list(post_map)

    testing_session.add_all(posts)
    testing_session.commit()

    posts = testing_session.query(models.Post).all()
    return posts