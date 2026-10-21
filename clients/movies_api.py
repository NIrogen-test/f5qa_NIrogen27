from custom_requester.custom_requester import CustomRequester
from config.base_urls import MOVIE_BASE_URL

MOVIE = '/movies'


class MovieAPI(CustomRequester):
    def __init__(self, session):
        super().__init__(session=session, base_url=MOVIE_BASE_URL)


    def filter_movies(self, filter_data, expected_status = 200):
        return self.send_request(
            method="GET",
            endpoint=MOVIE,
            params=filter_data,
            expected_status = expected_status
        )

    def create_movie(self, new_movie, expected_status = 201):
        return self.send_request(
            method="POST",
            endpoint=MOVIE,
            data=new_movie,
            expected_status = expected_status
        )

    def get_movie_info(self, movie_id, expected_status = 200):
        return self.send_request(
            method="GET",
            endpoint=f'{MOVIE}/{movie_id}',
            expected_status = expected_status
        )

    def delete_movie(self, movie_id, expected_status = 200):
        return self.send_request(
            method="DELETE",
            endpoint=f'{MOVIE}/{movie_id}',
            expected_status = expected_status
        )

    def patch_movie(self, movie_id, new_movie, expected_status = 200):
        return self.send_request(
            method="PATCH",
            endpoint=f'{MOVIE}/{movie_id}',
            data=new_movie,
            expected_status = expected_status
        )