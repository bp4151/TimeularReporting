import os
import sys

import dotenv
import json
import logging
import requests
from datetime import datetime, timedelta

baseurl = 'https://api.timeular.com/api/v3/'

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger()


def get_activities(_api_token: str) -> list:

    url = 'activities'

    payload = {}
    headers = {
        'Authorization': 'Bearer ' + _api_token
    }

    response = requests.request('GET', baseurl + url, headers=headers, data=payload)
    return response.json()['activities']


def get_entries_by_dates(_api_token: str, _start_date: datetime, _end_date: datetime) -> list:
    url = f'time-entries/{_start_date}/{_end_date}'

    payload = {}
    headers = {
        'Authorization': 'Bearer ' + _api_token
    }

    response = requests.request("GET", baseurl + url, headers=headers, data=payload)

    return response.json()['timeEntries']


def get_spaces(_api_token: str) -> list:

    url = 'space'

    payload = {}
    headers = {
        'Authorization': 'Bearer ' + _api_token
    }

    response = requests.request('GET', baseurl + url, headers=headers, data=payload)
    return response.json()['data']


def get_tags(_api_token: str) -> list:

    url = 'tags-and-mentions'

    payload = {}
    headers = {
        'Authorization': 'Bearer ' + _api_token
    }

    response = requests.request('GET', baseurl + url, headers=headers, data=payload)
    return response.json()['data']


def login(_api_key: str, _api_secret: str) -> str:

    logger.debug('Logging in to Timelar API to get API token')

    url = 'developer/sign-in'
    payload = json.dumps({
        "apiKey": _api_key,
        "apiSecret": _api_secret
    })
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        response = requests.request("POST", baseurl + url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()['token']
    except requests.exceptions.HTTPError as errh:
        logger.error(msg=f'An HTTP error occurred. {errh.response.text}')
    except requests.exceptions.ConnectionError as errc:
        logger.error(msg=f'A Connection error occurred', exc_info=errc)
    except requests.exceptions.Timeout as errt:
        logger.error(msg=f'A Timeout error occurred', exc_info=errt)
    except requests.exceptions.RequestException as err:
        logger.error(msg=f'A general RequestException occurred', exc_info=err)
    return ''


def replace_tag(_text: str, _tags: list) -> str:
    if _text.startswith('<'):
        start = _text.index('<')
        end = _text.index('>')
        id_text = _text[start:end+1].replace('<{{|t|', '').replace('|}}>', '')
        text = _text.replace(_text[start:end+1], '')
        if text != '':
            label = ''
            for tag in _tags:
                tag_id = tag.get('id')
                if id_text == str(tag_id):
                    label = tag.get("label")
                    break
            return f'{label} {text}'
        else:
            return ''


def main(_api_key: str, _api_secret: str):
    five_days = timedelta(days=5)

    end_date = datetime.today()
    start_date = end_date - five_days
    end_date_obj = end_date.isoformat(timespec='milliseconds')
    start_date_obj = start_date.isoformat(timespec='milliseconds')

    logger.info(f'Start Date is {start_date_obj}, End Date is {end_date_obj}')

    api_token = login(_api_key=_api_key, _api_secret=_api_secret)
    spaces = get_spaces(_api_token=api_token)
    activities = get_activities(_api_token=api_token)
    entries = get_entries_by_dates(_api_token=api_token, _start_date=start_date_obj, _end_date=end_date_obj)

    included_activity_ids = set()
    for activity in activities:
        name = activity.get('name')
        activity_id = activity.get('id')
        if name not in ['Break', 'Lunch', 'Meeting']:
            included_activity_ids.add(activity_id)

    selected_entries = [e for e in entries if e['activityId'] not in included_activity_ids]

    unique_tags = set()
    notes = []
    for entry in selected_entries:
        text = entry.get('note').get('text')
        tags = entry.get('note').get('tags')
        if text is not None:
            new_text = replace_tag(_text=text, _tags=tags)
            if new_text != '' and new_text is not None:
                notes.append(new_text)
        for tag in tags:
            unique_tags.add(tag.get('label'))
    print()
    print('Results')
    print('_' * 150)
    print('Tags:', ', '.join(str(s) for s in unique_tags))
    print('Notes:', ', '.join(str(s) for s in notes))
    print('_' * 150)


if __name__ == '__main__':
    dotenv.load_dotenv()

    try:
        if not os.path.isfile('.env'):
            raise ValueError('.env file not found. Make sure there is a .env file in the same folder as this file and'
                             'that it contains API_KEY and API_SECRET strings')

        api_key = os.getenv('API_KEY')
        api_secret = os.getenv('API_SECRET')

        if api_key is None or api_key == '':
            raise ValueError('API_KEY value in .env file not found')
        if api_secret is None or api_secret == '':
            raise ValueError('API_SECRET value in .env file not found')

        main(_api_key=api_key, _api_secret=api_secret)
    except Exception as ex:
        logger.error(ex)
        sys.exit(1)

