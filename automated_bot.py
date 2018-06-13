import requests
import json
import random
import time

from utils import generate_valid_email

with open('config.json') as f:
    rules = json.load(f)

with open('utils_and_user_info.json') as f:
    info = json.load(f)

choose_port = input('Please enter the port number you are running your app on(can be left blank if you are running it '
                    'on default port of 8000:\n')

TEST_USER_NAME = info['test_user_name']
GENERIC_PASSWORD = info['generic_password']
SITE_URL = info['site_url'].format(choose_port if choose_port.isdigit() else 8000)
REGISTER = info['register_url']
API_TOKEN = info['api_token_url']
LIST_OF_USERS = info['list_of_users_url']
LIST_OF_POSTS = info['list_of_posts_url']
POST_CREATION = info['post_creation_url']


def populate_users_and_create_posts():
    print('Populating users list and verifying email, this may take a while due to a server 2 '
          'second sleep timer between email checks\n')
    for _ in range(0, rules['number_of_users']):
        current_time = time.time()
        valid_email = generate_valid_email()
        username = f'{TEST_USER_NAME}-{current_time}'
        requests.post(SITE_URL + REGISTER,
                      json={'username': username, 'email': valid_email, 'password': GENERIC_PASSWORD})
        get_all_posts = requests.post(SITE_URL + API_TOKEN, data={'username': username, 'password': GENERIC_PASSWORD})
        token = get_all_posts.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        data = {'title': 'Bot posting', 'body': 'Test me please', 'status': 'published'}
        print('Creating posts for generated user\n')
        for _ in range(0, random.randint(1, rules['max_posts_per_user'])):
            requests.post(SITE_URL + POST_CREATION, json=data, headers=headers)


def perform_like_activity():
    print('Liking posts by logic given in specification\n')
    while True:
        current_max_number_of_posts = 0
        user = ''
        get_all_users = requests.get(SITE_URL + LIST_OF_USERS)
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
                                                                                                'password': user[1]})
        token = get_token_for_user_with_max_number_of_posts.json()['access']
        headers = {'Authorization': f'Bearer {token}'}
        get_all_posts = requests.get(SITE_URL+LIST_OF_POSTS)
        list_of_posts_without_likes_and_from_other_users = []
        for post in get_all_posts.json():
            if post['author']['username'] != user[0] and len(post['users_like']) == 0:
                list_of_posts_without_likes_and_from_other_users.append(post)
        if not list_of_posts_without_likes_and_from_other_users:
            if get_all_posts.json():
                break
        temporary_list = list_of_posts_without_likes_and_from_other_users[:]

        finished = False
        while user[2] < rules['max_likes_per_user'] and temporary_list and not finished:
            for each_post in list_of_posts_without_likes_and_from_other_users:
                    all_valid_posts_for_liking = list(set(each_post['author']['blog_posts']).difference(user[4]))
                    try:
                        random_post_chosen = random.choice(all_valid_posts_for_liking)
                    except IndexError:
                        finished = True
                        break
                    if random_post_chosen == each_post['id']:
                        temporary_list.remove(each_post)
                    requests.get(SITE_URL+LIST_OF_POSTS+f'{random_post_chosen}/like/', headers=headers)
                    user[2] += 1
                    user[4].append(random_post_chosen)
                    if user[2] == rules['max_likes_per_user']:
                        break


if __name__ == '__main__':
    populate_users_and_create_posts()
    perform_like_activity()
