from db_requester.models import AccountTransactionTemplate
from utils.data_generator import DataGenerator
import pytest


# Можете сделать рандомный тестовый файл для проверки работы фикстуры
# Так сказать - поиграться

def test_db_requests(super_admin, db_helper, created_test_user):
    assert created_test_user == db_helper.get_user_by_id(created_test_user.id)
    assert db_helper.user_exists_by_email("api1@gmail.com")

def test_movies_db_requests(super_admin, db_helper, movie_data):
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










