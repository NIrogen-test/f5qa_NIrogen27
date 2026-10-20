
import requests
from custom_requester.custom_requester import CustomRequester

session = requests.Session()
requester = CustomRequester(session=session, base_url = "https://auth.dev-cinescope.f5qa.ru")



class TestAuth:
    def test_register_user(self, api_manager, test_user):
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        assert response_data["email"] == test_user["email"]
        assert "id" in response_data
        assert "USER" in response_data["roles"]


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
        response = api_manager.user_api.get_user_info(authenticated_user['id'])
        response_data = response.json()
        assert response.status_code == 200
        assert response_data["email"] == authenticated_user["email"]
        assert response_data["id"] == authenticated_user["id"]


    # def test_register_timeout(self, api_manager, test_user):
    #     with pytest.raises(requests.exceptions.ConnectTimeout):
    #         api_manager.auth_api.register_user(test_user, timeout=0.001)


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
        api_manager.auth_api.authenticate((admin_credential['email'], admin_credential['password']))
        response_delete = api_manager.user_api.delete_user(registered_user['id'])
        assert response_delete.status_code == 200


    def test_delete_multiple_users(self, api_manager, test_user, test_user2, test_user3, admin_credential):
        api_manager.auth_api.authenticate((admin_credential['email'], admin_credential['password']))
        user_1 = api_manager.auth_api.register_user(test_user).json()
        user_2 = api_manager.auth_api.register_user(test_user2).json()
        user_3 = api_manager.auth_api.register_user(test_user3).json()

        response = api_manager.user_api.delete_users(user_1["id"], user_2["id"], user_3["id"])

        assert response.status_code == 200


