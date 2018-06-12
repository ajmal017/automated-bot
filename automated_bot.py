import string

import requests
import json
import random
import time

with open('config.json') as f:
    rules = json.load(f)

list_of_valid_temporary_emails = ['zikoxih@getnada.com', 'wasyso@getnada.com', 'pacyfy@getnada.com',
                                  'cegajino@getnada.com', 'koveg@getnada.com', 'pezefar@getnada.com',
                                  'hecekyz@getnada.com', 'weqe@getnada.com', 'roxin@getnada.com',
                                  'hobulap@getnada.com', 'latu@getnada.com', 'coqorodi@getnada.com',
                                  'xozypena@getnada.com', 'ruto@getnada.com', 'kamicuxu@getnada.com',
                                  'kuboluf@getnada.com', 'gysuqu@getnada.com', 'bysy@getnada.com',
                                  'cuwifuso@getnada.com', 'zedyby@getnada.com', 'ratanoro@getnada.com']


def get_next_valid_mail():
    yield list_of_valid_temporary_emails.pop()


test_user_name = 'Test'
generic_password = 'passmeup123'


def populate_users_and_create_posts():
    for _ in range(0, rules['number_of_users']):
        chars = string.ascii_lowercase
        random_string = ''.join(random.choice(chars) for _ in range(15))
        current_time = time.time()
        valid_email = f'urosh43+{random_string}@gmail.com'
        # valid_email = next(get_next_valid_mail())
        print(valid_email)
        username = f'{test_user_name}-{current_time}'
        ss = requests.post('http://127.0.0.1:8000/api/register/',
                      json={'username': username, 'email': valid_email, 'password': generic_password})
        print(ss.json())
        get_all_posts = requests.post('http://127.0.0.1:8000/api/token/',
                                      data={'username': username, 'password': generic_password},
                                      headers={'Connection': 'close'})
        token = get_all_posts.json()['access']
        headers = {'Authorization': f'Bearer {token}', 'Connection': 'close'}
        data = {'title': 'Bot posting', 'body': 'Test me please', 'status': 'published'}
        for _ in range(0, random.randint(1, rules['max_posts_per_user'])):
            requests.post('http://127.0.0.1:8000/api/post-list/create/', json=data, headers=headers)


def perform_like_activity():
    post_with_zero_likes_exists = True
    while post_with_zero_likes_exists:
        current_max_number_of_posts = 0
        user = ''
        get_all_users = requests.get(f'http://127.0.0.1:8000/api/user-list/', headers={'Connection': 'close'})
        for each_user in get_all_users.json():
            number_of_posts = len(each_user['blog_posts'])
            number_of_likes = len(each_user['posts_liked'])
            if number_of_likes < rules['max_likes_per_user']:
                if number_of_posts > current_max_number_of_posts:
                    current_max_number_of_posts = number_of_posts
                    user = [each_user['username'], generic_password, number_of_likes, each_user['id']]

        if user == '':
            break
        get_token_for_user_with_max_number_of_posts = requests.post('http://127.0.0.1:8000/api/token/',
                                                                    data={'username': user[0],
                                                                          'password': user[1]},
                                                                    headers={'Connection': 'close'})
        token = get_token_for_user_with_max_number_of_posts.json()['access']
        headers = {'Authorization': f'Bearer {token}', 'Connection': 'close'}
        get_all_posts = requests.get(f'http://127.0.0.1:8000/api/post-list/', headers={'Connection': 'close'})
        list_of_posts_from_other_users_that_user_didnt_like = []
        for post in get_all_posts.json():
            if post['author']['username'] != user[0] and user[3] not in post['users_like']:
                list_of_posts_from_other_users_that_user_didnt_like.append(post)
        get_all_users = requests.get(f'http://127.0.0.1:8000/api/user-list/', headers={'Connection': 'close'})
        if not list_of_posts_from_other_users_that_user_didnt_like:
            current_max_number_of_posts = 0
            for each_user in get_all_users.json():
                number_of_posts = len(each_user['blog_posts'])
                number_of_likes = len(each_user['posts_liked'])
                if number_of_likes < rules['max_likes_per_user'] and each_user['username'] != user[0]:
                    if number_of_posts > current_max_number_of_posts:
                        current_max_number_of_posts = number_of_posts
                        user = [each_user['username'], generic_password, number_of_likes, each_user['id']]
                        get_token_for_user_with_max_number_of_posts = requests.post('http://127.0.0.1:8000/api/token/',
                                                                                    data={'username': user[0],
                                                                                          'password': user[1]},
                                                                                    headers={'Connection': 'close'})
                        token = get_token_for_user_with_max_number_of_posts.json()['access']
                        headers = {'Authorization': f'Bearer {token}', 'Connection': 'close'}
        list_of_posts_from_other_users = []
        for post in get_all_posts.json():
            if post['author']['username'] != user[0]:
                list_of_posts_from_other_users.append(post)
        finished = False
        for each_post in list_of_posts_from_other_users:
            if len(each_post['users_like']) == 0:
                post_pk_of_random_post_from_user_that_has_a_post_with_no_likes = random.choice(
                    each_post['author']['blog_posts'])
                post_to_like = requests.get(f"http://127.0.0.1:8000/api/post-list/"
                                            f"{random.choice(each_post['author']['blog_posts'])}",
                                            headers={'Connection': 'close'})
                timeout = time.time() + 6
                while True:
                    if user[3] not in post_to_like.json()['users_like']:
                        requests.get(f'http://127.0.0.1:8000/api/post-list/'
                                     f'{post_pk_of_random_post_from_user_that_has_a_post_with_no_likes}/like',
                                     headers=headers)
                        user[2] += 1
                        break
                    else:
                        post_pk_of_random_post_from_user_that_has_a_post_with_no_likes = random.choice(
                            each_post['author']['blog_posts'])
                        post_to_like = requests.get(f'http://127.0.0.1:8000/api/post-list/'
                                                    f'{post_pk_of_random_post_from_user_that_has_a_post_with_no_likes}',
                                                    headers={'Connection': 'close'})
                    if time.time() > timeout:
                        finished = True
                        break
            if user[2] == rules['max_likes_per_user'] or finished:
                break
        get_all_posts = requests.get(f'http://127.0.0.1:8000/api/post-list/', headers={'Connection': 'close'})
        for each_post in get_all_posts.json():
            if len(each_post['users_like']) == 0:
                break
        else:
            post_with_zero_likes_exists = False


if __name__ == '__main__':
    populate_users_and_create_posts()
    perform_like_activity()
