from pydoc import Helper

import requests
import pytest
from clients.api_manager import ApiManager
from db_requester.db_client import get_db_session
from utils.data_generator import DataGenerator
import random
from resources.user_creds import SuperAdminCreds
from entities.user import User
from constants.roles import Roles
from models.base_models import TestUser
from sqlalchemy.orm import Session
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper




@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)


@pytest.fixture
def test_user() -> TestUser:
    password = DataGenerator.generate_password()
    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_name(),
        password=password,
        passwordRepeat=password,
        roles=[Roles.USER.value]
    )

@pytest.fixture
def registration_user_data():
    random_password = DataGenerator.generate_password()

    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_name(),
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value]
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
            "roles": [Roles.USER.value]
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
    yield new_movie
    try:
        api_manager.movies_api.delete_movie(new_movie["id"])
    except Exception:  # чтобы не падал тест на удаление ....
        pass

@pytest.fixture(scope="function")
def movie_id(created_movie):
    return created_movie["id"]


@pytest.fixture(scope="function")
def movie_id_without_authentication():
    return 997


@pytest.fixture
def user_session():
    user_pool = [] # созданрие пула созданныхх сессий

    def _create_user_session():
        session = requests.Session() # Создаем новую сессию
        user_session = ApiManager(session) #инициализация обьекта ApiManager
        user_pool.append(user_session) #добавляем сессию в user_pool, для закрытия сессий
        return user_session

    yield _create_user_session()

    for user in user_pool:
        user.close_session()


@pytest.fixture
def super_admin(user_session):
    new_session = user_session

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session
    )

    super_admin.api.auth_api.authenticate(super_admin.creds, )

    return super_admin

@pytest.fixture(scope="function")
def creation_user_data(test_user):
    updated_data = test_user.copy()
    updated_data.update({
        "verified": True,
        "banned": False
    })
    return updated_data

@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    new_session = user_session

    common_user = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.USER.value],
        new_session
    )

    super_admin.api.user_api.create_user(creation_user_data, expected_status=201)
    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user

@pytest.fixture
def admin(user_session, super_admin, creation_user_data):
    new_session = user_session

    admin = User(
        creation_user_data['email'],
        creation_user_data['password'],
        [Roles.ADMIN.value],
        new_session
    )

    super_admin.api.user_api.create_user(creation_user_data, expected_status=201)
    admin.api.auth_api.authenticate(admin.creds)
    return admin

@pytest.fixture(scope="module")
def db_session() -> Session:
    db_session = get_db_session()
    yield db_session
    db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session):
    db_helper = DBHelper(db_session)
    yield db_helper

@pytest.fixture(scope="function")
def created_test_user(db_helper):
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    user_to_delete = db_helper.get_user_by_id(user.id)
    if user_to_delete:
        db_helper.delete_user(user_to_delete)

@pytest.fixture(scope="function")
def movie_data():
    return DataGenerator.generate_movie_data()




