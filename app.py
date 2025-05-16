import os
import secrets

from flask import Flask, redirect, request, session, url_for, render_template
from glueops.setup_logging import configure as go_configure_logging
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
except KeyError:
    logger.warn(f'could not retrieve APP_SECRET_KEY from env, falling back to generated secret')
    app.secret_key = secrets.token_urlsafe(24)

try:
    slack_token = os.environ['SLACK_API_TOKEN']
    slack_channel = os.environ['SLACK_CHANNEL']
except KeyError:
    logger.exception('could not retrieve environment secret')
    raise



slack_client = WebClient(token=slack_token)

redirect_url = os.getenv('REDIRECT_URL', 'https://www.glueops.dev/book-a-demo/')
APP_PORT = os.getenv('APP_PORT', 5000)
DEBUG_ENABLED = os.getenv('DEBUG_ENABLED', False)



@app.route('/', methods=["POST"])
def login():
    email = request.form.get('email')
    session['email'] = email
    logger.info(f'email: {email}')
    try:
        response = slack_client.chat_postMessage(
            channel=slack_channel,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*New signup*\n*Email Addresses:*\n{email}"
                    }
                }
            ]
        )
        logger.info(f'slack response: {response}')
    except SlackApiError as e:
        logger.exception(f"Error sending message to Slack: {e.response['error']}")
    return redirect(redirect_url)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=APP_PORT, debug=DEBUG_ENABLED)
