import hmac

from flask import Flask, make_response, request

from constants import GITHUB_SECRET
from handlers import handle_github_request, handle_telegram_request

app = Flask(__name__)


def _check_github_signature():
    """
    Verify the sha1 signature contained in X-Hub-Signature header.

    If the header is not present or is in incorrect format, an exeption
    is handled inside this method, and False is returned.
    Return
    ------
    bool
        True if the method in the signature is sha1 and the digests match
    """
    try:
        sha_name, signature = request.headers.get('X-Hub-Signature').split('=')
    except (AttributeError, ValueError):
        # AttributeError raised when splitting a NoneType
        # ValueError raised when the number of splitted elements is not two.
        return False
    mac = hmac.new(GITHUB_SECRET.encode(), msg=request.data, digestmod='sha1')
    return sha_name == 'sha1' and hmac.compare_digest(
        str(mac.hexdigest()), str(signature))


@app.route('/github', methods=['POST'])
def github_handler():
    """
    Handle POSTS in /github.

    Verifies the sha1 signature contained in X-Hub-Signature and then
    delegates the event to the declared handler in handlers.py.
    """
    if not (app.debug or _check_github_signature()):
        return make_response("Bad Credentials", 401)

    if not request.is_json:
        return make_response("Bad Request", 400)

    return handle_github_request(app)


@app.route('/telegram', methods=['POST'])
def telegram_handler():
    """Handle POSTS in /telegram."""
    return handle_telegram_request(app)


if __name__ == '__main__':
    # Calling this module directly will launch the server in debug mode
    app.run(debug=True)
