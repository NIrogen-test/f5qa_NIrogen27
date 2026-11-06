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


def test_account_transaction_template(db_session):

    stan = AccountTransactionTemplate(user=f"Stan_{DataGenerator.generate_random_int(10)}", balance=1000)
    bob = AccountTransactionTemplate(user=f"Bob_{DataGenerator.generate_random_int(10)}", balance=500)
    db_session.add(stan)
    db_session.add(bob)
    db_session.commit()

    def transfer_money(session, from_account, to_account, amount):

        from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account.user).one()
        to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account.user).one()

        if from_account.balance < amount:
            raise ValueError("not enough money")

        from_account.balance -= amount
        to_account.balance += amount

        session.commit()

    assert stan.balance == 1000
    assert bob.balance == 500

    try:
        transfer_money(db_session, from_account=stan, to_account=bob, amount=1200)
        pytest.fail("Функция перевода должна была выбросить ValueError, но не сделала этого!")

    except ValueError as e:
        db_session.rollback()
        db_session.refresh(stan)
        db_session.refresh(bob)
        assert bob.balance == 500
        assert stan.balance == 1000


    finally:
        db_session.delete(stan)
        db_session.delete(bob)
        db_session.commit()







