import requests
import pytest
from clients.api_manager import ApiManager
from utils.data_generator import DataGenerator
import random




@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)


@pytest.fixture(scope="function")
def test_user():
    password = DataGenerator.generate_password()
    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_name(),
        "password": password,
        "passwordRepeat": password,
        "roles": ["USER"]
    }
@pytest.fixture(scope="function")
def test_user2():
    password = DataGenerator.generate_password()
    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_name(),
        "password": password,
        "passwordRepeat": password,
        "roles": ["USER"]
    }
@pytest.fixture(scope="function")
def test_user3():
    password = DataGenerator.generate_password()
    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_name(),
        "password": password,
        "passwordRepeat": password,
        "roles": ["USER"]
    }

@pytest.fixture(scope="function")
def admin_credential():
    return {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q",
    }


@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    test_user["id"] = response["id"]
    return test_user

@pytest.fixture(scope="function")
def registered_super_admin(api_manager, super_admin):
    response = api_manager.auth_api.register_user(super_admin).json()
    super_admin["id"] = response["id"]
    return super_admin


@pytest.fixture(scope="function")
def authenticated_user(api_manager, test_user, admin_credential):
    response = api_manager.auth_api.register_user(test_user)
    response_data = response.json()
    cred = (admin_credential['email'], admin_credential['password'])
    api_manager.auth_api.authenticate(cred)
    return response_data

@pytest.fixture(scope="session")
def unauthenticated_api_manager(registered_user):
    http_session = requests.Session()
    yield ApiManager(http_session)
    http_session.close()

@pytest.fixture(scope="function")
def movie_params():
    return {
        "genreId": random.randint(1, 10),
        "pageSize": random.randint(1, 10),
        "page": 1,
    }

@pytest.fixture(scope="function")
def new_movie():
    return {
      "name": "Название фильма",
      "imageUrl": "https://image.url",
      "price": 100,
      "description": "Описание фильма",
      "location": "SPB",
      "published": True,
      "genreId": 1
    }

@pytest.fixture(scope="function")
def movie_id():
    return 836