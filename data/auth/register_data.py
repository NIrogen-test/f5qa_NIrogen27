from utils.data_generator import DataGenerator

def get_register_payload(roles=None):
    password = DataGenerator.generate_password()
    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_name(),
        "password": DataGenerator.generate_password(),
        "passwordRepeat": password,
        "roles": roles or ["USER"]
    }

