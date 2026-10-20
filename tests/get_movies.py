import requests
from custom_requester.custom_requester import CustomRequester


session = requests.Session()
requester = CustomRequester(session=session, base_url = "https://api.dev-cinescope.coconutqa.ru")

response = requester.send_request(
    method="GET",
    endpoint="/movies",
    params={
        "genreId": 7,
        "pageSize": 1,
        "page": 1,
    }
)
print(response.json()["movies"][0]["genre"]['name'])

def test_get_movies_by_genre_id(movie_params):
    response = requester.send_request(
        method="GET",
        endpoint="/movies",
        params= movie_params
    )

    assert response.json()["movies"][0]["genre"]['name'] == 'Мюзикл'
    assert response.json()["pageSize"] == 1
