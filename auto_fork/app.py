from flask import Flask, session, request, make_response, render_template
from werkzeug import exceptions
import requests
from urllib import parse
from waitress import serve
import uuid

from config import AppConfig

app = Flask(__name__, template_folder='templates')
app.config.from_object(AppConfig.flask)


@app.route("/")
def index():
    state = str(uuid.uuid4())
    session['auto_fork_state'] = state

    auth_endpoint = parse.urljoin(request.base_url, '/auth')

    params = {'client_id': AppConfig.github.client_id,
              'state': state,
              'scope': 'public_repo',
              'redirect_uri': auth_endpoint}
    authorize_url = f"{AppConfig.github.authorize_endpoint}?" + parse.urlencode(params)

    return make_response(render_template('index.html', auth_url=authorize_url))


@app.route("/auth", methods=['GET'])
def auth():
    code = request.args.get("code")
    state = request.args.get("state")

    # verify this is a response to our request
    state_good = state == session.pop('auto_fork_state') if 'auto_fork_state' in session else False

    if not state_good or not code:
        raise exceptions.NotAcceptable
    elif request.method != 'GET':
        raise exceptions.MethodNotAllowed
    else:
        headers = {'Accept': 'application/json'}
        payload = {'code': code,
                   'client_id': AppConfig.github.client_id,
                   'client_secret': AppConfig.github.client_secret,
                   'scope': 'public_repo'}
        res = requests.post(AppConfig.github.token_endpoint, headers=headers, json=payload)

        if res.status_code == 200:
            data = res.json()
            access_token = data['access_token']
            session['github_access_token'] = access_token
            fork_endpoint = parse.urljoin(request.base_url, '/fork')
            return make_response(render_template('authorized.html', fork_endpoint=fork_endpoint))
        elif res.status_code == 403:
            raise exceptions.Forbidden
        else:
            raise exceptions.ServiceUnavailable


@app.route("/fork", methods=['GET'])
def fork():
    if request.method != 'GET':
        raise exceptions.MethodNotAllowed
    elif 'github_access_token' not in session:
        raise exceptions.Forbidden
    else:
        access_token = session['github_access_token']
        headers = {'Authorization': f'token {access_token}'}
        forked_res = requests.post(AppConfig.github.fork_endpoint, headers=headers)

        if forked_res.status_code == 202:
            base_url = parse.urljoin(request.base_url, '/')
            response = make_response(render_template('forked.html', base_url=base_url))
        elif forked_res.status_code == 403:
            raise exceptions.Forbidden
        else:
            raise exceptions.ServiceUnavailable

    return response


@app.errorhandler(exceptions.NotAcceptable)
@app.errorhandler(exceptions.Forbidden)
@app.errorhandler(exceptions.ServiceUnavailable)
@app.errorhandler(exceptions.MethodNotAllowed)
def error_handler(error: exceptions.HTTPException):
    base_url = parse.urljoin(request.base_url, '/')
    template = render_template('error.html', error_name=error.name, error_desc=error.description, base_url=base_url)
    return make_response(template, error.code)


@app.errorhandler(exceptions.NotFound)
def not_found(error: exceptions.HTTPException):
    base_url = parse.urljoin(request.base_url, '/')
    template = render_template('not_found.html', base_url=base_url)
    return make_response(template, error.code)


if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
