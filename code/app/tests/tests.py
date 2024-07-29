import pytest
import httpx
from fastapi import status

@pytest.fixture
def client():
    with httpx.Client(base_url="http://127.0.0.1:8000") as client:
        yield client

def test_register_user(client):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "password": "testpassword",
        "email": "testuser@example.com"
    })
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "testuser@example.com"
    assert not data["verified"]

def test_login_user(client):
    # Register user first
    client.post("/auth/register", json={
        "username": "testuser2",
        "password": "testpassword2",
        "email": "testuser2@example.com"
    })
    
    response = client.post("/auth/login", data={
        "username": "testuser2",
        "password": "testpassword2"
    })
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

def test_create_post(client):
    # Register and login user
    client.post("/auth/register", json={
        "username": "postuser",
        "password": "postpassword",
        "email": "postuser@example.com"
    })
    login_response = client.post("/auth/login", data={
        "username": "postuser",
        "password": "postpassword"
    })
    login_data = login_response.json()
    access_token = login_data["access_token"]

    # Create post
    response = client.post("/posts/", json={
        "title": "Test Post",
        "content": "This is a test post."
    }, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Test Post"
    assert data["content"] == "This is a test post."

def test_get_post(client):
    # Register and login user
    client.post("/auth/register", json={
        "username": "postuser2",
        "password": "postpassword2",
        "email": "postuser2@example.com"
    })
    login_response = client.post("/auth/login", data={
        "username": "postuser2",
        "password": "postpassword2"
    })
    login_data = login_response.json()
    access_token = login_data["access_token"]

    # Create post
    create_response = client.post("/posts/", json={
        "title": "Another Test Post",
        "content": "This is another test post."
    }, headers={"Authorization": f"Bearer {access_token}"})
    post_data = create_response.json()
    post_id = post_data["id"]

    # Get post
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Another Test Post"
    assert data["content"] == "This is another test post."

def test_get_users(client):
    # Register user
    client.post("/auth/register", json={
        "username": "userlistuser",
        "password": "userlistpassword",
        "email": "userlistuser@example.com"
    })
    response = client.get("/users/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0

def test_get_user_by_id(client):
    # Register user
    register_response = client.post("/auth/register", json={
        "username": "specificuser",
        "password": "specificpassword",
        "email": "specificuser@example.com"
    })
    user_data = register_response.json()
    user_id = user_data["id"]

    # Get user by ID
    response = client.get(f"/users/{user_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "specificuser"
    assert data["email"] == "specificuser@example.com"