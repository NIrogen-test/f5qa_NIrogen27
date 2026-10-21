

class TestMoviePositive:

    def test_get_poster(self, api_manager, movie_params):
        response = api_manager.movies_api.filter_movies(movie_params)
        response_data = response.json()

        assert response.status_code == 200
        assert response_data["page"] == movie_params["page"]
        assert response_data["pageSize"] == movie_params["pageSize"]
        assert movie_params["genreId"] == response_data['movies'][0]['genreId']

    def test_get_movie_info(self, api_manager, movie_id):
        response = api_manager.movies_api.get_movie_info(movie_id)
        response_data = response.json()
        assert response.status_code == 200
        assert movie_id == response_data["id"]

    def test_create_movie(self, api_manager, new_movie, admin_credential):
        api_manager.auth_api.authenticate(admin_credential)
        response = api_manager.movies_api.create_movie(new_movie)
        response_data = response.json()
        assert response.status_code == 201
        assert response_data["name"] == new_movie["name"]
        assert response_data["price"] == new_movie["price"]
        assert response_data["genreId"] == new_movie["genreId"]

    def test_patch_movie(self, api_manager, movie_id, new_movie, admin_credential):
        api_manager.auth_api.authenticate(admin_credential)
        response = api_manager.movies_api.patch_movie(movie_id, new_movie)
        response_data = response.json()
        assert response.status_code == 200
        assert response_data["name"] == new_movie["name"]

    def test_delete_movie(self, api_manager, movie_id, admin_credential):
        api_manager.auth_api.authenticate(admin_credential)
        response = api_manager.movies_api.delete_movie(movie_id)
        response_data = response.json()
        assert response.status_code == 200
        assert response_data['id'] == movie_id


class TestMovieNegative:

    def test_negative_create_empty_movie(self, api_manager, admin_credential, empty_movie):
        api_manager.auth_api.authenticate(admin_credential)
        response = api_manager.movies_api.create_movie(empty_movie, expected_status=400)
        response_data = response.json()
        assert response.status_code == 400
        assert response_data["message"] == [
        "name should not be empty",
        "Поле name должно быть строкой",
        "Поле price должно быть числом",
        "Поле description должно быть строкой",
        "Поле location должно быть одним из: MSK, SPB",
        "Поле location должно быть строкой",
        "Поле published должно быть булевым значением",
        "Поле genreId должно быть числом"
    ]

    def test_negative_patch_movie_with_empty_data(self, api_manager, movie_id, empty_movie, admin_credential):
        api_manager.auth_api.authenticate(admin_credential)
        response = api_manager.movies_api.patch_movie(movie_id, empty_movie)
        assert response.status_code == 200

    def test_negative_create_movie_without_access(self, unauthenticated_api_manager, new_movie):
        response = unauthenticated_api_manager.movies_api.create_movie(new_movie, expected_status=401)
        assert response.status_code == 401, f"Ожидался статус 401, получили {response.status_code}"

    def test_negative_delete_movie_without_access(self, unauthenticated_api_manager, movie_id_without_authentication):
        response = unauthenticated_api_manager.movies_api.delete_movie(movie_id_without_authentication, expected_status=401)
        assert response.status_code == 401

    def test_negative_patch_movie_without_access(self, unauthenticated_api_manager, movie_id_without_authentication, new_movie):
        response = unauthenticated_api_manager.movies_api.patch_movie(movie_id_without_authentication, new_movie,  expected_status=401)
        assert response.status_code == 401