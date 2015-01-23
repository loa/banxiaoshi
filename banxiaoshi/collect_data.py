#!/usr/bin/env python3
from base64 import b64encode
import datetime
import json
import os
import subprocess
import urllib
import urllib.parse
import urllib.request
import yaml


def get_token(username, password, oauth_name, oauth_secret):
    url = 'https://www.skritter.com/api/v0/oauth2/token'

    OAUTH_CLIENT_NAME = oauth_name
    OAUTH_CLIENT_SECRET = oauth_secret

    USER_NAME = username
    USER_PASSWORD = password

    params = {
        'grant_type':  'password',
        'client_id':   OAUTH_CLIENT_NAME,
        'username':    USER_NAME,
        'password':    USER_PASSWORD,
    }
    credentials = "%s:%s" % (OAUTH_CLIENT_NAME, OAUTH_CLIENT_SECRET)
    credentials = b64encode(bytes(credentials, "utf-8"))
    credentials = "basic %s" % credentials.decode('UTF-8')

    data = urllib.parse.urlencode(params)
    data = data.encode('utf-8')
    request = urllib.request.Request(url, data)

    request.add_header('AUTHORIZATION', credentials)

    response = urllib.request.urlopen(request)
    packet = json.loads(response.read().decode('UTF-8'))

    return packet.get('access_token')


def get_user_data(username):
    if os.path.isfile("data/%s.yaml" % username):
        user_data = yaml.load(open("data/%s.yaml" % username, 'r'))

        latest_date = None
        if user_data:
            for key in user_data.keys():
                key_parts = key.split('-')

                current_date = datetime.date(
                    int(key_parts[0]),
                    int(key_parts[1]),
                    int(key_parts[2]))

                if latest_date is None:
                    latest_date = current_date
                elif latest_date < current_date:
                    latest_date = current_date

            return latest_date, user_data

    return datetime.date.today(), {}


def get_days(token, start_date, end_date):
    url = 'http://www.skritter.com/api/v0/progstats?'

    params = {
        'start': start_date,
        'end': end_date,
        'step': 'day'
    }

    url += urllib.parse.urlencode(params)
    request = urllib.request.Request(url)

    credentials = "bearer %s" % token
    request.add_header('Authorization', credentials)

    response = urllib.request.urlopen(request)
    return json.loads(response.read().decode('UTF-8'))


def decrypt_password(password):
    return subprocess.check_output(
        "echo '%s' | base64 --decode | openssl rsautl -decrypt -inkey encrypt/private_rsa" % password,
        shell=True,
        env=os.environ.copy()).decode('UTF-8')

if __name__ == "__main__":
    users = yaml.load(open('users.yaml', 'r'))

    for user in users['users']:
        # Get user token
        token = get_token(
            user['username'],
            decrypt_password(user['password']),
            users['client']['username'],
            decrypt_password(users['client']['password'])
        )

        latest_date, user_data = get_user_data(user['username'])

        today = datetime.date.today()
        while not today < latest_date:
            next_date = min(
                datetime.date.today(),
                latest_date + datetime.timedelta(days=14))

            print (
                user['username'] + ': '
                + str(latest_date) + ' '
                + str(next_date))

            days = get_days(token, latest_date, next_date)

            for day in days['ProgressStats']:
                user_data[day['date']] = int(day['timeStudied']['day'])

            latest_date = next_date + datetime.timedelta(days=1)

        yaml.dump(
            user_data,
            open("data/%s.yaml" % user['username'], 'w'),
            default_flow_style=False)
