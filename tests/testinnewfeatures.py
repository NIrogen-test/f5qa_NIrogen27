import requests
from custom_requester.custom_requester import CustomRequester
from data.auth.register_data import get_register_payload
from clients.api_manager import ApiManager
session = requests.Session()
requester = CustomRequester(session=session, base_url = "https://auth.dev-cinescope.f5")


# def test_something():
#     login_response = requester.send_request(
#         "POST",
#         "/login",
#         data={
#             "email": "api1@gmail.com",
#             "password": "asdqwe123Q"
#         }
#     )
#     token = login_response.json()["accessToken"]
#     requester.update_session_headers({"Authorization": f"Bearer {token}"})
#
#     response = requester.send_request(
#         "GET",
#         "/user/me"
#     )
#     assert response.status_code == 200


response = requests.post(url="https://auth.dev-cinescope.f5qa.ru/register", data={
        "email": "prirop7@gmail.com",
        "fullName": "roman nikit",
        "password": "password27",
        "passwordRepeat": "password27",
        "roles": "USER"
        }
        )

login_response = requests.post(url="https://auth.dev-cinescope.f5qa.ru/login", data={
        "email": "prirop@gmail.com",
        "password": "password27",
        })

response_data = response.json()

print(response_data)
