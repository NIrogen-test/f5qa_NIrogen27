import pytest
import allure
from utils.data_generator import DataGenerator
import random

@allure.epic("Тестирование API Movies")
@allure.feature("Позитивные тесты")
class TestMoviePositive:

    @allure.story("Получение списка фильмов с фильтрацией")
    @allure.title("Проверка фильтрации фильмов по параметрам")
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
    def test_get_movie_info(self, api_manager, movie_id):
        with allure.step(f"отправка GET запроса на получение описания фильма по id:{movie_id}"):
            response = api_manager.movies_api.get_movie(movie_id)
            response_data = response.json()

        with allure.step("Проверка что id фильма в ответе соответствует movie_id"):
            assert movie_id == response_data["id"]

    def test_get_movie_common_user(self, common_user, movie_id):
        response_data = common_user.api.movies_api.get_movie(movie_id).json()

        assert response_data["id"] == movie_id

    @allure.story("Создание фильма")
    @allure.title("Создание фильма через админ пользователя")
    def test_create_movie(self, new_movie, super_admin):
        with allure.step("Отправляет POST запрос под админ пользователем"):
            response = super_admin.api.movies_api.create_movie(new_movie)
            response_data = response.json()

        with allure.step("Проверяем что созданный фильм соответствует данным, которые мы отправили при создании"):
            assert response_data["name"] == new_movie.name
            assert response_data["price"] == new_movie.price
            assert response_data["genreId"] == new_movie.genreId


    #на этом тесте можно сделать параметризацию
    @allure.story("Обновление данных фильма")
    @allure.title("Обновление данных фильма с параметризацией через админ пользователя")
    @pytest.mark.parametrize("data_movie", [{'name': DataGenerator.generate_name(), 'location': "MSC"},
                                            {'price': random.randint(500, 5000), 'location': 'SPB'},
                                            {'genreId': 9, 'published': DataGenerator.generate_boolean()}
                                            ])
    def test_patch_movie(self,api_manager, movie_id, data_movie, super_admin):
        with allure.step("Отправляем PATCH запрос на обновление данных"):
            super_admin.api.movies_api.patch_movie(movie_id, data_movie)

        with allure.step("Получаем обновленные данные фильма по id"):
            updated_movie = api_manager.movies_api.get_movie(movie_id).json()

        with allure.step(f"Проверяем, что отправленные данные {data_movie} применились"):
            for key, expected_value in data_movie.items():
                actual_value = updated_movie.get(key)

                # Проверяем, что значение в базе совпадает с тем, что мы отправили
                assert actual_value == expected_value, \
                    f"Поле '{key}' не обновилось. Ожидали {expected_value}, получили {actual_value}"

    @allure.story("Удаление фильма")
    @allure.title("Удаление фильма по movie_id через админ пользователя")
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
    def test_patch_movie_with_empty_data(self, api_manager, movie_id, empty_movie, super_admin):
        with allure.step("Отправляем PATCH запрос с пустыми данными"):
            response = super_admin.api.movies_api.patch_movie(movie_id, empty_movie)
            response_data = response.json()

        with allure.step("Получаем обновленные данные через movie_id"):
            movie_info = api_manager.movies_api.get_movie(movie_id).json()

        with allure.step("Проверяем что данные соответствуют"):
            assert response_data["name"] == movie_info["name"]
            assert response_data["price"] == movie_info["price"]

@allure.feature("Негативные тесты")
class TestMovieNegative:

    @allure.story("Создание фильма")
    @allure.story("Создание пустого фильма через админа")
    def test_negative_create_empty_movie(self, super_admin, empty_movie):
        with allure.step("Отправляем POST запрос на создание фильма"):
            response = super_admin.api.movies_api.create_movie(empty_movie, expected_status=400)
            response_data = response.json()

        with allure.step("Проверяем что в теле ответа есть сообщение об ошибке"):
            assert response_data["message"] == [
        "Поле name должно содержать не менее 3 символов",
        "Поле name должно быть строкой",
        "Поле name не может быть пустым",
        "Поле price должно быть больше 0",
        "Поле price должно быть числом",
        "Поле price не может быть пустым",
        "Поле description должно содержать не менее 5 символов",
        "Поле description должно быть строкой",
        "Поле description не может быть пустым",
        "Поле location должно быть одним из: MSK, SPB",
        "Поле location должно быть строкой",
        "Поле location не может быть пустым",
        "Поле published должно быть булевым значением",
        "Поле published не может быть пустым",
        "Поле genreId должно быть больше 0",
        "Поле genreId должно быть целым числом",
        "Поле genreId должно быть числом",
        "Поле genreId не может быть пустым"
    ]

    @allure.story("Создание фильма")
    @allure.title("Создание фильма без аутентификации")
    def test_negative_create_movie_without_access(self, unauthenticated_api_manager, new_movie):
        with allure.step("Пытаемся создать фильм без нужной авторизации"):
            response = unauthenticated_api_manager.movies_api.create_movie(new_movie, expected_status=401)
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
            response = unauthenticated_api_manager.movies_api.patch_movie(movie_id_without_authentication, new_movie,  expected_status=401)
            response_data = response.json()

        with allure.step("Проверяем что есть сообщение об ошибке"):
            assert response_data["message"] == "Unauthorized"

    @allure.story("Создание фильма")
    @allure.title("Создание фильма через обычного пользователя")
    def test_create_movie_common_user(self, common_user, new_movie):
        with allure.step("Пытаемся создать фильм под обычным пользователем"):
            response_data = common_user.api.movies_api.create_movie(new_movie, expected_status=403).json()

        with allure.step("Проверяем что сообщение об ошибки соответствует"):
            assert response_data['message'] == "Forbidden resource"

@allure.feature("Тесты с Базой Данных")
class TestMoviesBD:

    def test_movies_db_requests(self, super_admin, db_helper, movie_data):
        movie_name = movie_data['name']

        movie_db_before = db_helper.get_movie_by_name(movie_name)
        assert movie_db_before is None

        db_movie_data = movie_data.copy()
        db_movie_data.pop("id", None)

        created_movie = db_helper.create_test_movie(db_movie_data)

        movie_db_after = db_helper.get_movie_by_name(movie_name)
        assert movie_db_after is not None
        assert movie_db_after.id == created_movie.id

        db_helper.delete_movie(created_movie)

        movie_in_db_final = db_helper.get_movie_by_name(movie_name)
        assert movie_in_db_final is None, "Ошибка: фильм остался в базе после удаления!"