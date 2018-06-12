import string
import requests
import json
import random
import time

with open('config.json') as f:
    rules = json.load(f)

with open('utils_and_user_info.json') as f:
    info = json.load(f)

TEST_USER_NAME = info['test_user_name']
GENERIC_PASSWORD = info['generic_password']
SITE_URL = info['site_url']
REGISTER = info['register_url']
API_TOKEN = info['api_token_url']
LIST_OF_USERS = info['list_of_users_url']
LIST_OF_POSTS = info['list_of_posts_url']
POST_CREATION = info['post_creation_url']


def populate_users_and_create_posts():
    for _ in range(0, rules['number_of_users']):
        chars = string.ascii_lowercase
        random_string = ''.join(random.choice(chars) for _ in range(15))
        current_time = time.time()
        valid_email = f'urosh43+{random_string}@gmail.com'
        username = f'{TEST_USER_NAME}-{current_time}'
        requests.post(SITE_URL + REGISTER,
                      json={'username': username, 'email': valid_email, 'password': GENERIC_PASSWORD})
        get_all_posts = requests.post(SITE_URL + API_TOKEN, data={'username': username, 'password': GENERIC_PASSWORD},
                                      headers={'Connection': 'close'})
        token = get_all_posts.json()['access']
        headers = {'Authorization': f'Bearer {token}', 'Connection': 'close'}
        data = {'title': 'Bot posting', 'body': 'Test me please', 'status': 'published'}
        for _ in range(0, random.randint(1, rules['max_posts_per_user'])):
            requests.post(SITE_URL + POST_CREATION, json=data, headers=headers)


def perform_like_activity():
    while True:
        current_max_number_of_posts = 0
        user = ''
        get_all_users = requests.get(SITE_URL + LIST_OF_USERS, headers={'Connection': 'close'})
        for each_user in get_all_users.json():
            number_of_posts = len(each_user['blog_posts'])
            number_of_likes = len(each_user['posts_liked'])
            if number_of_likes == 0:
                if number_of_posts > current_max_number_of_posts:
                    current_max_number_of_posts = number_of_posts
                    user = [each_user['username'], GENERIC_PASSWORD, number_of_likes, each_user['id'],
                            each_user['posts_liked']]

        if user == '':
            break
        get_token_for_user_with_max_number_of_posts = requests.post(SITE_URL + API_TOKEN, data={'username': user[0],
                                                                                                'password': user[1]},
                                                                    headers={'Connection': 'close'})
        token = get_token_for_user_with_max_number_of_posts.json()['access']
        headers = {'Authorization': f'Bearer {token}', 'Connection': 'close'}
        get_all_posts = requests.get(SITE_URL+LIST_OF_POSTS, headers={'Connection': 'close'})
        list_of_posts_from_other_users = []
        for post in get_all_posts.json():
            if post['author']['username'] != user[0] and len(post['users_like']) == 0:
                list_of_posts_from_other_users.append(post)
        if not list_of_posts_from_other_users:
            if get_all_posts.json():
                break
        list_of_posts_from_other_users_2 = list_of_posts_from_other_users[:]

        while user[2] < rules['max_likes_per_user'] and list_of_posts_from_other_users_2:
            for each_post in list_of_posts_from_other_users:
                    all_posible = list(set(each_post['author']['blog_posts']).difference(user[4]))
                    random_chosen = random.choice(all_posible)
                    if random_chosen == each_post['id']:
                        list_of_posts_from_other_users_2.remove(each_post)
                    requests.get(SITE_URL+LIST_OF_POSTS+f'{random_chosen}/like/', headers=headers)
                    user[2] += 1
                    user[4].append(random_chosen)
                    if user[2] == rules['max_likes_per_user']:
                        break


if __name__ == '__main__':
    populate_users_and_create_posts()
    perform_like_activity()
