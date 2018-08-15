from collections import defaultdict
from textwrap import indent

import requests
from flask import Flask, make_response, request

from constants import SERVER_URL, TELEGRAM_ID, TELEGRAM_TOKEN

_handlers = defaultdict(dict)


def handle_github_request(app: Flask):
    """Handle a request from GitHub."""
    event = request.headers.get('X-GitHub-Event')
    return _handle(app, 'github', event)


def handle_telegram_request(app: Flask):
    """Handle a request from Telegram."""
    pass


def call_telegram_api(function: str, data: dict):
    """Make a raw call to Telegram API."""
    return requests.post(
        f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/{function}', data=data)


def send_telegram_message(text: str, recipient: str, **kwargs):
    """Send a message through Telegram."""
    params = {'text': text, 'chat_id': recipient, **kwargs}
    response = call_telegram_api('sendMessage', params)
    return response.json()


def set_telegram_webhook():
    """Set telegram webhook to receive messages."""
    data = {'url': f'{SERVER_URL}/telegram'}
    response = call_telegram_api('setWebhook', data)
    response.raise_for_status()


def _handles(service: str, event: str):
    def inner(function):
        _handlers[service][event] = function
        return function

    return inner


def _handle(app: Flask, service: str, event: str):
    if event not in _handlers[service]:
        raise NotImplementedError(f'Not implemented {service}:{event}')
    return _handlers[service][event](app)


@_handles('github', 'ping')
def _github_ping(app: Flask):
    payload = request.get_json()
    hook_id = payload['hook_id']
    response = send_telegram_message(f'Ping of {hook_id}', TELEGRAM_ID)

    if response['ok']:
        return make_response('PONG', 200)
    else:
        return make_response(f'Fail: {response["description"]}', 500)


@_handles('github', 'push')
def _github_push(app: Flask):
    payload = request.get_json()

    commits = [commit['id'] for commit in payload['commits']]
    repo = payload['repository']['name']
    pusher = payload['pusher']['name']

    header = f'{pusher} has pushed the following commits in {repo}:'
    body = indent('\n'.join(f'{commit:8.8}' for commit in commits), '- ')

    response = send_telegram_message(f'{header}\n{body}', TELEGRAM_ID)

    if response['ok']:
        return make_response('OK', 200)
    else:
        return make_response(f'Fail: {response["description"]}', 500)
