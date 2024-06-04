import os
import secrets

from flask import Flask, redirect, request, session, url_for, render_template
from glueops.setup_logging import configure as go_configure_logging
from requests_oauthlib import OAuth2Session
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from werkzeug.middleware.proxy_fix import ProxyFix


# configure logger
logger = go_configure_logging(
    name='SIGNUP',
    level=os.getenv('PYTHON_LOG_LEVEL', 'INFO')
)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

try:
    app.secret_key = os.environ['APP_SECRET_KEY']
except AttributeError:
    logger.warn(f'could not retrieve APP_SECRET_KEY from env, falling back to generated secret')
    app.secret_key = secrets.token_urlsafe(24)

try:
    client_id = os.environ['GITHUB_CLIENT_ID']
    client_secret = os.environ['GITHUB_CLIENT_SECRET']
    slack_token = os.environ['SLACK_API_TOKEN']
    slack_channel = os.environ['SLACK_CHANNEL']
except KeyError:
    logger.exception('could not retrieve environment secret')
    raise


authorization_base_url = 'https://github.com/login/oauth/authorize'
token_url = 'https://github.com/login/oauth/access_token'
user_url = 'https://api.github.com/user'
emails_url = 'https://api.github.com/user/emails'


slack_client = WebClient(token=slack_token)

redirect_url = os.getenv('REDIRECT_URL', 'https://www.glueops.dev/book-a-demo/')
APP_PORT = os.getenv('APP_PORT', 5000)
DEBUG_ENABLED = os.getenv('DEBUG_ENABLED', False)



@app.route('/')
def login():
    github = OAuth2Session(client_id)
    authorization_url, state = github.authorization_url(authorization_base_url)
    session['oauth_state'] = state
    logger.info(f'oauth_state: {state}')
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    github = OAuth2Session(client_id, state=session['oauth_state'])
    token = github.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)
    session['oauth_token'] = token
    return redirect(url_for('.profile'))

@app.route('/profile')
def profile():
    github = OAuth2Session(client_id, token=session['oauth_token'])
    user = github.get(user_url).json()
    logger.info(f'gh user info: {user}')
    github_handle = user["login"]
    github_emails = github.get(emails_url).json()

    try:
        response = slack_client.chat_postMessage(
            channel=slack_channel,
            text=f"New signup: GitHub Handle: {github_handle}, Email: {github_emails}"
        )
        logger.info(f'slack response: {response}')
    except SlackApiError as e:
        logger.error(f"Error sending message to Slack: {e.response['error']}")

    return redirect(redirect_url)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT, debug=DEBUG_ENABLED)
