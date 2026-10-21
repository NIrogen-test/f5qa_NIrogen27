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
def create_users(api_manager):
    def create_user():
        # Генерируем данные
        password = DataGenerator.generate_password()
        user_data = {
            "email": DataGenerator.generate_random_email(),
            "fullName": DataGenerator.generate_name(),
            "password": password,
            "passwordRepeat": password,
            "roles": ["USER"]
        }

        response = api_manager.auth_api.register_user(user_data).json()
        user_data["id"] = response["id"]

        return user_data

    return create_user




@pytest.fixture(scope="function")
def admin_credential():
    return ("api1@gmail.com", "asdqwe123Q")
    #     "email": "api1@gmail.com",
    #     "password": "asdqwe123Q",
    #


@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    test_user["id"] = response["id"]
    return test_user


@pytest.fixture(scope="function")
def authenticated_user(api_manager, test_user, admin_credential):
    response = api_manager.auth_api.register_user(test_user)
    response_data = response.json()
    cred = admin_credential
    api_manager.auth_api.authenticate(cred)
    return response_data

@pytest.fixture(scope="function")
def unauthenticated_api_manager(registered_user):
    http_session = requests.Session()
    yield ApiManager(http_session)
    http_session.close()

@pytest.fixture(scope="function")
def movie_params():
    return {
        "pageSize": random.randint(1, 10),
        "page": 1,
        "minPrice": 100,
        "maxPrice": random.randint(1000, 5000),
        "location": "SPB",
        "genreId": random.randint(5,10),
    }

@pytest.fixture(scope="function")
def new_movie():
    return {
      "name": DataGenerator.generate_name(),
      "imageUrl": f"https://{DataGenerator.generate_lastname()}.url",
      "price": random.randint(500, 5000),
      "description": "Описание фильма",
      "location": "SPB",
      "published": DataGenerator.generate_boolean(),
      "genreId": 7
    }

@pytest.fixture(scope="function")
def empty_movie():
    return {

    }

@pytest.fixture(scope="function")
def created_movie(api_manager, new_movie, admin_credential):
    api_manager.auth_api.authenticate(admin_credential)
    response = api_manager.movies_api.create_movie(new_movie).json()
    new_movie["id"] = response["id"]
    return new_movie

@pytest.fixture(scope="function")
def movie_id(created_movie):
    return created_movie["id"]

@pytest.fixture(scope="function")
def movie_id_without_authentication():
    return 997