from models.base_models import RegisterUserResponse

class TestAuth:
    def test_register_user(self, api_manager, test_user):
        response = api_manager.auth_api.register_user(test_user.model_dump(mode="json"))
        register_user_response = RegisterUserResponse(**response.json())

        assert register_user_response.email == test_user.email, "Email не совпадает"


    def test_register_and_login_user(self, api_manager, registered_user):
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }

        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        assert "accessToken" in response_data
        assert response_data["user"]["email"] == registered_user["email"]

    def test_get_user_info(self, api_manager, authenticated_user):
        response = api_manager.user_api.get_user(authenticated_user['id'])
        response_data = response.json()
        assert response.status_code == 200
        assert response_data["email"] == authenticated_user["email"]
        assert response_data["id"] == authenticated_user["id"]

    def test_logout_user(self, api_manager, registered_user):
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        api_manager.auth_api.login_user(login_data)
        response_logout = api_manager.auth_api.logout_user()

        assert response_logout.status_code == 200
        assert "refresh_token" not in response_logout.cookies

    def test_delete_user(self, api_manager, registered_user, admin_credential):
        api_manager.auth_api.authenticate(admin_credential)
        response_delete = api_manager.user_api.delete_user(registered_user['id'])
        assert response_delete.status_code == 200

    def test_delete_multiple_users(self, api_manager, create_users, admin_credential):
        api_manager.auth_api.authenticate(admin_credential)

        user_1 = create_users()
        user_2 = create_users()
        user_3 = create_users()

        response = api_manager.user_api.delete_users(user_1["id"], user_2["id"], user_3["id"])

        assert response.status_code == 200


