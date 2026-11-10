from db_requester.models import AccountTransactionTemplate
from utils.data_generator import DataGenerator
import pytest
import allure




@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
class TestAccountTransactionTemplate:

    @allure.story("Корректность перевода денег между счетами")
    @allure.description("""
    Этот тест проверяет корректность перевода денег между двумя счетами.
    Шаги:
    1. Создание двух счетов: Stan и Bob.
    2. Перевод 200 единиц от Stan к Bob.
    3. Проверка изменения балансов.
    4. Очистка тестовых данных.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Roman Nikitin")
    @allure.title("Тест перевода денег между счетами 200 рублей")
    def test_account_transaction_template(self, db_session):
        with allure.step("Создание тестовых данных в базе данных: счета Bob и Stan"):
            stan = AccountTransactionTemplate(user=f"Stan_{DataGenerator.generate_random_int(10)}", balance=1000)
            bob = AccountTransactionTemplate(user=f"Bob_{DataGenerator.generate_random_int(10)}", balance=500)
            db_session.add_all([stan, bob])
            db_session.commit()



        @allure.step("Функция перевода денег: transfer_money")
        @allure.description("""
             функция выполняющая транзакцию, имитация вызова функции на стороне тестируемого сервиса
            и вызывая метод transfer_money, мы как будто бы делим запрос в api_manager.movies_api.transfer_money
        """)

        def transfer_money(session, from_account, to_account, amount):
            with allure.step("получаем счета"):
                from_account = session.query(AccountTransactionTemplate).filter_by(user=from_account.user).one()
                to_account = session.query(AccountTransactionTemplate).filter_by(user=to_account.user).one()

            with allure.step("Проверяем, что на счете достаточно средств"):
                if from_account.balance < amount:
                    raise ValueError("not enough money")

            with allure.step("Выполняем перевод"):
                from_account.balance -= amount
                to_account.balance += amount

            with allure.step("сохраняем изменения"):
                session.commit()

        with allure.step("Проверяем начальные балансы"):
            assert stan.balance == 1000
            assert bob.balance == 500

        try:
            with allure.step("Выполняем перевод 200 единиц от stan к bob"):
                transfer_money(db_session, from_account=stan, to_account=bob, amount=200)

            with allure.step("Проверяем что балансы изменились"):
                assert stan.balance == 800
                assert bob.balance == 700

        except Exception as e:
            with allure.step("ОШИБКА откаты транзаций"):
                db_session.rollback()

            pytest.fail(f"Ошибка при переводе денег: {e}")


        finally:
            with allure.step("Удаляем данные для тестирования из базы"):
                db_session.delete(stan)
                db_session.delete(bob)
                db_session.commit()