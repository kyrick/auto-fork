from flask import Flask, session, request
from requests import post
from urllib import parse
import uuid
from config import AppConfig

application = Flask(__name__)
application.config.from_object(AppConfig.flask)


@application.route("/")
def index():
    state = str(uuid.uuid4())
    session['auto_fork_state'] = state

    auth_endpoint = parse.urljoin(request.base_url, '/auth')

    params = {'client_id': AppConfig.github.client_id,
              'state': state,
              'scope': 'public_repo',
              'redirect_uri': auth_endpoint}
    authorize_url = f"{AppConfig.github.authorize_endpoint}?" + parse.urlencode(params)

    return f'<a href="{authorize_url}">Click Here to Surrender to Auto Fork</a>'


@application.route("/auth", methods=['GET'])
def auth():
    code = request.args.get("code")
    state = request.args.get("state")

    # verify this is a response to our request
    if state == session.pop('auto_fork_state') and code is not None:
        headers = {'Accept': 'application/json'}
        payload = {'code': code,
                   'client_id': AppConfig.github.client_id,
                   'client_secret': AppConfig.github.client_secret,
                   'scope': 'public_repo'}
        res = post(AppConfig.github.token_endpoint, headers=headers, json=payload)

        data = res.json()
        access_token = data['access_token']
        session['github_access_token'] = access_token
        fork_endpoint = parse.urljoin(request.base_url, '/fork')
        return f'<a href="{fork_endpoint}">Click Here to Fork The Code For This App</a>'
    else:
        return "Request could not be validated"


@application.route("/fork", methods=['GET'])
def fork():
    access_token = session['github_access_token']
    headers = {'Authorization': f'token {access_token}'}
    res = post(AppConfig.github.fork_endpoint, headers=headers)
    return "forked"


if __name__ == "__main__":
    application.run()
