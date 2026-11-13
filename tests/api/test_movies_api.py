import pytest
import allure
from allure_commons.types import Severity
from models.base_models import FindOneMovieResponse, MovieResponse, FindAllMoviesResponse

from utils.data_generator import DataGenerator
import random

@allure.epic("Тестирование API Movies")
@allure.feature("Позитивные тесты")
class TestMoviePositive:

    @allure.story("Получение списка фильмов с фильтрацией")
    @allure.title("Проверка фильтрации фильмов по параметрам")
    @pytest.mark.regression
    @pytest.mark.parametrize("movie_data", [{"minPrice": 100, "maxPrice": 5000}, {"location":"SPB"}, {"genreId":7}])
    def test_get_poster(self, api_manager, movie_data):

        expected_page = movie_data.get("page", 1)
        expected_page_size = movie_data.get("pageSize", 10)

        with allure.step(f"Отправка GET запроса на получение фильмов с параметрами: {movie_data}"):
            response = api_manager.movies_api.get_movies(movie_data)
            response_data = response.json()

        with allure.step("проверка параметров пагинации (page и pageSize)"):
            assert response_data["page"] == expected_page
            assert response_data["pageSize"] == expected_page_size

        movies = response_data["movies"]
        with allure.step("Проверка что список фильмов не пустой"):
            assert len(movies) > 0

        if "minPrice" in movie_data and "maxPrice" in movie_data:
            with allure.step(f"Проверка соответствия цен диапазону от {movie_data['minPrice']} до {movie_data['maxPrice']}"):
                assert all(movie_data["minPrice"] <= m['price'] <= movie_data["maxPrice"] for m in movies)

        if "location" in movie_data:
            loc = movie_data["location"]
            with allure.step(f"Проверка соответствия локации: {loc}"):
                assert all(m["location"] == loc for m in movies), "Локация не совпадает"

            # 4. Проверка жанра (если он есть)
        if "genreId" in movie_data:
            genre = movie_data["genreId"]
            with allure.step(f"Проверка соответствия жанра (genreId: {genre})"):
                assert all(m["genreId"] == genre for m in movies), "Жанр не совпадает"

    @allure.story("Получение описание фильма")
    @allure.title("Описание фильма по movie_id")
    @pytest.mark.smoke
    def test_get_movie_info(self, super_admin, movie_id):
        with allure.step(f"отправка GET запроса на получение описания фильма по id:{movie_id}"):
            response = super_admin.api.movies_api.get_movie(movie_id)
            response_data = response.json()

        with allure.step("Валидация через Pydantic"):
            movie = FindOneMovieResponse(**response_data)

        with allure.step("Проверка что id фильма в ответе соответствует movie_id"):
            assert movie_id == movie.id


    @allure.story("Создание фильма")
    @allure.title("Создание фильма через админ пользователя")
    @pytest.mark.smoke
    def test_create_movie(self, new_movie, super_admin):
        with allure.step("Отправляет POST запрос под админ пользователем"):
            data = new_movie.model_dump(mode="json")
            data.pop("id", None)
            response = super_admin.api.movies_api.create_movie(data)

        with allure.step("Валидация через Pydantic"):
            response_data = response.json()
            movie = MovieResponse(**response_data)


        with allure.step("Проверяем что созданный фильм соответствует данным, которые мы отправили при создании"):
            assert movie.name == new_movie.name
            assert movie.price == new_movie.price
            assert movie.genreId == new_movie.genreId


    #на этом тесте можно сделать параметризацию
    @allure.story("Обновление данных фильма")
    @allure.title("Обновление данных фильма с параметризацией через админ пользователя")
    @pytest.mark.parametrize("data_movie", [{'name': DataGenerator.generate_name(), 'location': "MSK"},
                                            {'price': random.randint(500, 5000), 'location': 'SPB'},
                                            {'genreId': 9, 'published': DataGenerator.generate_boolean()}
                                            ])
    @pytest.mark.regression
    def test_patch_movie(self,api_manager, movie_id, data_movie, super_admin):
        with allure.step("Отправляем PATCH запрос на обновление данных"):
            super_admin.api.movies_api.patch_movie(movie_id, data_movie)

        with allure.step("Получаем обновленные данные фильма по id и делаем Валидацию через Pydantic"):
            updated_movie = api_manager.movies_api.get_movie(movie_id)
            updated_movie_data = updated_movie.json()
            movie = MovieResponse(**updated_movie_data)


        with allure.step(f"Проверяем, что отправленные данные {data_movie} применились"):
            for key, expected_value in data_movie.items():
                actual_value = getattr(movie, key)

                # Проверяем, что значение в базе совпадает с тем, что мы отправили
                assert actual_value == expected_value, \
                    f"Поле '{key}' не обновилось. Ожидали {expected_value}, получили {actual_value}"

    @allure.story("Удаление фильма")
    @allure.title("Удаление фильма по movie_id через админ пользователя")
    @pytest.mark.smoke
    def test_delete_movie(self, api_manager, movie_id, super_admin):
        with allure.step("Отправка DELETE запроса"):
            response = super_admin.api.movies_api.delete_movie(movie_id)
            response_data = response.json()

        with allure.step("Проверка на то, что сервер возвращает статус 404"):
            api_manager.movies_api.get_movie(movie_id, expected_status=404)

        with allure.step("Проверка на то, что id удаленного фильма равен movie_id"):
            assert response_data['id'] == movie_id

    @allure.story("Обновление данных фильма")
    @allure.title("Обновление фильма пустыми данными")
    @pytest.mark.regression
    def test_patch_movie_with_empty_data(self, api_manager, movie_id, empty_movie, super_admin):
        with allure.step("Отправляем PATCH запрос с пустыми данными"):
            response = super_admin.api.movies_api.patch_movie(movie_id, empty_movie)
            response_data = MovieResponse(**response.json())

        with allure.step("Получаем обновленные данные через movie_id"):
            movie_info = MovieResponse(**api_manager.movies_api.get_movie(movie_id).json())

        with allure.step("Проверяем что данные соответствуют"):
            assert response_data.name == movie_info.name
            assert response_data.price == movie_info.price

@allure.feature("Негативные тесты")
@pytest.mark.negative
class TestMovieNegative:

    @allure.story("Создание фильма")
    @allure.story("Создание пустого фильма через админа")
    def test_negative_create_empty_movie(self, super_admin, empty_movie):
        with allure.step("Отправляем POST запрос на создание фильма"):
            response = super_admin.api.movies_api.create_movie(empty_movie, expected_status=400)
            response_data = response.json()

        with allure.step("Проверяем что в теле ответа есть сообщение об ошибке"):
            assert 'name should not be empty' in response_data["message"]

    @allure.story("Создание фильма")
    @allure.title("Создание фильма без аутентификации")
    def test_negative_create_movie_without_access(self, unauthenticated_api_manager, new_movie):
        with allure.step("Пытаемся создать фильм без нужной авторизации"):
            data = new_movie.model_dump(mode="json")
            data.pop("id", None)
            response = unauthenticated_api_manager.movies_api.create_movie(data, expected_status=401)
            response_data = response.json()

        with allure.step("Проверяем что есть сообщение об ошибке"):
            assert response_data["message"] == "Unauthorized"

    @allure.story("Удаление фильма")
    @allure.title("Удаление фильма без аутентификации")
    def test_negative_delete_movie_without_access(self, unauthenticated_api_manager, movie_id_without_authentication):
        with allure.step("Пытаемся удалить фильм без нужной авторизации"):
            response = unauthenticated_api_manager.movies_api.delete_movie(movie_id_without_authentication, expected_status=401)
            response_data = response.json()

        with allure.step("Проверяем что есть сообщение об ошибке"):
            assert response_data["message"] == "Unauthorized"

    @allure.story("Обновление данных фильма")
    @allure.title("Обновление данных фильма без аутентификации")
    def test_negative_patch_movie_without_access(self, unauthenticated_api_manager, movie_id_without_authentication, new_movie):
        with allure.step("Пытаемся обновить данные фильма без нужной авторизации"):
            data = new_movie.model_dump(mode="json")
            data.pop("id", None)
            response = unauthenticated_api_manager.movies_api.patch_movie(movie_id_without_authentication, data,  expected_status=401)
            response_data = response.json()

        with allure.step("Проверяем что есть сообщение об ошибке"):
            assert response_data["message"] == "Unauthorized"

    @allure.story("Создание фильма")
    @allure.title("Создание фильма через обычного пользователя")
    def test_create_movie_common_user(self, common_user, new_movie):
        with allure.step("Пытаемся создать фильм под обычным пользователем"):
            data = new_movie.model_dump(mode="json")
            data.pop("id", None)
            response_data = common_user.api.movies_api.create_movie(data, expected_status=403).json()

        with allure.step("Проверяем что сообщение об ошибки соответствует"):
            assert response_data['message'] == "Forbidden resource"

@allure.feature("Тесты с Базой Данных")
@pytest.mark.db
class TestMoviesBD:

    @allure.story("Создание и удаление фильма в Базе Данных")
    @allure.title("Проверка всего цикла от создания до удаления")
    @allure.severity(Severity.CRITICAL)
    def test_movies_db_requests(self, super_admin, db_helper, movie_data):
        movie_name = movie_data['name']

        with allure.step("Проверяем что фильма пока что нет в бд"):
            movie_db_before = db_helper.get_movie_by_name(movie_name)
            assert movie_db_before is None

        with allure.step("Создаем фильм в бд"):
            db_movie_data = movie_data.copy()
            db_movie_data.pop("id", None)

            created_movie = db_helper.create_test_movie(db_movie_data)

        with allure.step("Проверяем что фильм есть в бд"):
            movie_db_after = db_helper.get_movie_by_name(movie_name)
            assert movie_db_after is not None
            assert movie_db_after.id == created_movie.id

        with allure.step("Удаляем фильм из бд"):
            db_helper.delete_movie(created_movie)

        with allure.step("Проверяем что фильм удалился из бд"):
            movie_in_db_final = db_helper.get_movie_by_name(movie_name)
            assert movie_in_db_final is None, "Ошибка: фильм остался в базе после удаления!"