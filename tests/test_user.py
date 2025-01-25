from app import schemas
from fastapi import status


def test_create_user(testing_client):
    res = testing_client.post('/user/', json={
        'email': 'ondrej.tkadlec@world.com',
        'password': 'mv',
    })
    added_user = schemas.UserOut(**res.json())
    assert res.status_code == 201
    assert added_user.email == 'ondrej.tkadlec@world.com'


def test_get_user(test_user, testing_client):
    res = testing_client.get(f'/user/{test_user["id"]}')
    assert res.status_code == 200
    assert res.json()['email'] == test_user['email']


def test_get_user_not_found(test_user, testing_client):
    res = testing_client.get(f'/user/{test_user["id"] + 1}')
    assert res.status_code == status.HTTP_404_NOT_FOUND
