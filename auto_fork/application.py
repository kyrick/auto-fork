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

    params = {'client_id': AppConfig.client_id, 'state': state, 'scope': 'repo', 'redirect_uri': auth_endpoint}
    ask_for_auth_url = "https://github.com/login/oauth/authorize?" + parse.urlencode(params)

    return f'<a href="{ask_for_auth_url}">Click Here to Surrender to Auto Fork</a>'


@application.route("/auth", methods=['GET'])
def auth():
    code = request.args.get("code")
    state = request.args.get("state")

    # verify this is a response to our request
    if state == session.get('auto_fork_state') and code is not None:
        headers = {'Accept': 'application/json'}
        payload = {'code': code, 'client_id': AppConfig.client_id, 'client_secret': AppConfig.client_secret,
                   'scope': 'repo'}
        res = post("https://github.com/login/oauth/access_token", headers=headers, json=payload)
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
    res = post(AppConfig.repo_fork_endpoint, headers=headers)
    return "forked"


if __name__ == "__main__":
    application.run()
