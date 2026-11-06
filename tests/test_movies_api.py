import pytest

class TestMoviePositive:

    @pytest.mark.parametrize("movie_data", [{"minPrice": 100, "maxPrice": 5000}, {"location":"SPB"}, {"genreId":7}])
    def test_get_poster(self, api_manager, movie_data):

        expected_page = movie_data.get("page", 1)
        expected_page_size = movie_data.get("pageSize", 10)

        response = api_manager.movies_api.get_movies(movie_data)
        response_data = response.json()

        assert response_data["page"] == expected_page
        assert response_data["pageSize"] == expected_page_size

        movies = response_data["movies"]
        assert len(movies) > 0

        if "minPrice" in movie_data and "maxPrice" in movie_data:
            assert all(movie_data["minPrice"] <= m['price'] <= movie_data["maxPrice"] for m in movies)

        if "location" in movie_data:
            loc = movie_data["location"]
            assert all(m["location"] == loc for m in movies), "Локация не совпадает"

            # 4. Проверка жанра (если он есть)
        if "genreId" in movie_data:
            genre = movie_data["genreId"]
            assert all(m["genreId"] == genre for m in movies), "Жанр не совпадает"


    def test_get_movie_info(self, api_manager, movie_id):
        response = api_manager.movies_api.get_movie(movie_id)
        response_data = response.json()

        assert movie_id == response_data["id"]

    def test_get_movie_common_user(self, common_user, movie_id):
        response_data = common_user.api.movies_api.get_movie(movie_id).json()

        assert response_data["id"] == movie_id

    def test_create_movie(self, new_movie, super_admin):
        response = super_admin.api.movies_api.create_movie(new_movie)
        response_data = response.json()

        assert response_data["name"] == new_movie["name"]
        assert response_data["price"] == new_movie["price"]
        assert response_data["genreId"] == new_movie["genreId"]

    def test_patch_movie(self,api_manager, movie_id, new_movie, super_admin):
        super_admin.api.movies_api.patch_movie(movie_id, new_movie)

        updated_movie = api_manager.movies_api.get_movie(movie_id).json()

        assert updated_movie["name"] == new_movie["name"]
        assert updated_movie["price"] == new_movie["price"]
        assert updated_movie["genreId"] == new_movie["genreId"]
        assert updated_movie["id"] == movie_id

    def test_delete_movie(self, api_manager, movie_id, super_admin):
        response = super_admin.api.movies_api.delete_movie(movie_id)
        response_data = response.json()

        api_manager.movies_api.get_movie(movie_id, expected_status=404)

        assert response_data['id'] == movie_id


    def test_patch_movie_with_empty_data(self, api_manager, movie_id, empty_movie, super_admin):
        response = super_admin.api.movies_api.patch_movie(movie_id, empty_movie)
        response_data = response.json()
        movie_info = api_manager.movies_api.get_movie(movie_id).json()

        assert response_data["name"] == movie_info["name"]
        assert response_data["price"] == movie_info["price"]

class TestMovieNegative:

    def test_negative_create_empty_movie(self, super_admin, empty_movie):
        response = super_admin.api.movies_api.create_movie(empty_movie, expected_status=400)
        response_data = response.json()
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

    def test_negative_create_movie_without_access(self, unauthenticated_api_manager, new_movie):
        response = unauthenticated_api_manager.movies_api.create_movie(new_movie, expected_status=401)
        response_data = response.json()
        assert response_data["message"] == "Unauthorized"

    def test_negative_delete_movie_without_access(self, unauthenticated_api_manager, movie_id_without_authentication):
        response = unauthenticated_api_manager.movies_api.delete_movie(movie_id_without_authentication, expected_status=401)
        response_data = response.json()
        assert response_data["message"] == "Unauthorized"

    def test_negative_patch_movie_without_access(self, unauthenticated_api_manager, movie_id_without_authentication, new_movie):
        response = unauthenticated_api_manager.movies_api.patch_movie(movie_id_without_authentication, new_movie,  expected_status=401)
        response_data = response.json()
        assert response_data["message"] == "Unauthorized"

    def test_create_movie_common_user(self, common_user, new_movie):
        response_data = common_user.api.movies_api.create_movie(new_movie, expected_status=403).json()
        assert response_data['message'] == "Forbidden resource"