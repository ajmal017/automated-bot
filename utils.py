import string
import random


def generate_valid_email():
    chars = string.ascii_lowercase
    random_string = ''.join(random.choice(chars) for _ in range(15))
    return f'api.rest.test.me+{random_string}@gmail.com'
