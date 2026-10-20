import random
from datetime import timedelta
from faker import Faker
import string

faker = Faker(locale='en_US')


class DataGenerator:

    @staticmethod
    def generate_password(length=12):
        letters = string.ascii_letters
        digits = string.digits
        symbols = "@#$%^&*_-+"

        # гарантируем букву и цифру
        password = [
            random.choice(letters),
            random.choice(digits),
        ]
        # добиваем остаток случайными символами
        all_chars = letters + digits + symbols
        password += [random.choice(all_chars) for _ in range(length - 2)]

        random.shuffle(password)
        return "".join(password)

    @staticmethod
    def generate_firstname():
        return faker.first_name()

    @staticmethod
    def generate_lastname():
        return faker.last_name()

    @staticmethod
    def generate_total_price():
        return random.randint(100, 5000)

    @staticmethod
    def generate_deposit_paid():
        return faker.boolean()

    @staticmethod
    def generate_checkin_date():
        return faker.date_between(start_date='today', end_date='+30d')

    @staticmethod
    def generate_checkout_date(checkin):
        return  checkin + timedelta(days=faker.random_int(min=1, max=14))

    @staticmethod
    def generate_late_checkin_date():
        return faker.date_between(start_date='-14d', end_date='today')

    @staticmethod
    def generate_additional_needs():
        options = ["Breakfast", "Lunch", "Dinner", "Late checkout", "Extra bed", ""]
        return random.choice(options)

    @staticmethod
    def generate_random_email():
        return faker.email()

    # @staticmethod
    # def generate_password():
    #     return faker.password()

    @staticmethod
    def generate_name():
        return faker.first_name() + " " + faker.last_name()


