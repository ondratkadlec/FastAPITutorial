import pytest
from fastapi import status

from app import schemas


def test_get_all_posts(authorized_testing_client, test_posts, test_user):
    res = authorized_testing_client.get("/posts")

    assert res.status_code == 200
    assert len(res.json()) == len([post for post in test_posts if post.owner_id == test_user["id"]])


def test_get_all_posts_unauthorized_user(testing_client, test_posts):
    res = testing_client.get("/posts")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_one_post(authorized_testing_client, test_posts, test_user):
    res = authorized_testing_client.get(f"/posts/{test_posts[0].id}")
    post = res.json()
    assert res.status_code == 200
    assert post['id'] == test_posts[0].id
    assert post['title'] == test_posts[0].title
    assert post['content'] == test_posts[0].content


def test_get_one_post_unauthorized_user(testing_client, test_posts):
    res = testing_client.get(f"/posts/{test_posts[0].id}")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_one_post_diff_owner(authorized_testing_client, test_posts, test_user):
    posts_diff_owner = [post for post in test_posts if post.owner_id != test_user["id"]]
    assert len(posts_diff_owner) > 0, "No posts with different owner, make sure to add at least one in conftest"

    res = authorized_testing_client.get(f"/posts/{posts_diff_owner[0].id}")
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_get_one_post_not_exists(authorized_testing_client, test_posts):
    res = authorized_testing_client.get("/posts/8888")
    assert res.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize("title, content, published", [
    ("awesome new title", "awesome new content", True),
    ("favorite pizza", "i love pepperoni", False),
    ("tallest skyscrapers", "wahoo", True),
])
def test_create_post(authorized_testing_client, test_posts, test_user, title, content, published):
    new_post = schemas.PostCreate(title=title, content=content, published=published)
    res = authorized_testing_client.post("/posts", json=new_post.model_dump())

    created_post = schemas.PostOut(**res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']


def test_create_post_default_published_true(authorized_testing_client, test_user, test_posts):
    res = authorized_testing_client.post("/posts/", json={"title": "Title", "content": "Content"})

    created_post = schemas.PostOut(**res.json())
    assert res.status_code == 201
    assert created_post.title == "Title"
    assert created_post.content == "Content"
    assert created_post.published == True
    assert created_post.owner_id == test_user['id']


def test_create_post_unauthorized_user(testing_client):
    res = testing_client.post("/posts/", json={"title": "Title", "content": "Content"})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_post(authorized_testing_client, test_posts, test_user):
    test_user_posts = [post for post in test_posts if post.owner_id == test_user["id"]]
    assert len(test_user_posts) > 0, "No posts for test user, make sure to add at least one in conftest"

    res = authorized_testing_client.delete(f"/posts/{test_user_posts[0].id}")
    assert res.status_code == status.HTTP_204_NO_CONTENT


def test_delete_post_unauthorized_user(testing_client, test_posts):
    res = testing_client.delete(f"/posts/{test_posts[0].id}")
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_post_diff_owner(authorized_testing_client, test_posts, test_user):
    posts_diff_owner = [post for post in test_posts if post.owner_id != test_user["id"]]
    assert len(posts_diff_owner) > 0, "No posts with different owner, make sure to add at least one in conftest"

    res = authorized_testing_client.delete(f"/posts/{posts_diff_owner[0].id}")
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_delete_post_not_exists(authorized_testing_client, test_posts, test_user):
    res = authorized_testing_client.delete("/posts/8888")
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_update_post(authorized_testing_client, test_posts, test_user):
    test_user_posts = [post for post in test_posts if post.owner_id == test_user["id"]]
    assert len(test_user_posts) > 0, "No posts for test user, make sure to add at least one in conftest"

    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_user_posts[0].id
    }
    res = authorized_testing_client.put(f"/posts/{test_user_posts[0].id}", json=data)
    updated_post = schemas.PostOut(**res.json())
    assert res.status_code == 200
    assert updated_post.title == "updated title"
    assert updated_post.content == "updated content"


def test_update_post_unauthorized_user(testing_client, test_posts, test_user):
    test_user_posts = [post for post in test_posts if post.owner_id == test_user["id"]]
    assert len(test_user_posts) > 0, "No posts for test user, make sure to add at least one in conftest"

    data = {
        "title": "updated title",
        "content": "updated content",
        "id": test_user_posts[0].id
    }
    res = testing_client.put(f"/posts/{test_user_posts[0].id}", json=data)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_post_diff_owner(authorized_testing_client, test_posts, test_user):
    posts_diff_owner = [post for post in test_posts if post.owner_id != test_user["id"]]
    assert len(posts_diff_owner) > 0, "No posts with different owner, make sure to add at least one in conftest"

    data = {
        "title": "updated title",
        "content": "updated content",
        "id": posts_diff_owner[0].id
    }
    res = authorized_testing_client.put(f"/posts/{posts_diff_owner[0].id}", json=data)
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_update_post_not_exists(authorized_testing_client, test_posts, test_user):
    data = {
        "title": "updated title",
        "content": "updated content",
        "id": 8888
    }
    res = authorized_testing_client.put("/posts/8888", json=data)
    assert res.status_code == status.HTTP_404_NOT_FOUND
