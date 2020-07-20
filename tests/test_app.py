import pytest
from flask import Response, template_rendered
from contextlib import contextmanager
import requests
from auto_fork.app import app
from tests.util import mock_post


# Borrowed with love from https://stackoverflow.com/questions/23987564/test-flask-render-template-context
@contextmanager
def captured_templates(test_app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((sender, template, context, extra))

    template_rendered.connect(record, test_app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, test_app)


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_index(client):
    with captured_templates(app) as templates:
        rv: Response = client.get('/')

        assert rv.status_code == 200

        _, template, context, _ = templates[0]
        assert template.name == 'index.html'
        assert 'client_id=client_id_not_set' in context['auth_url']
        with client.session_transaction() as session:
            assert 'auto_fork_state' in session


def test_auth_success(client, monkeypatch):
    with captured_templates(app) as templates:
        with client.session_transaction() as session:
            session['auto_fork_state'] = 'app_state'

        # mock out the successful response from github
        monkeypatch.setattr(requests, "post", mock_post(200, {'access_token': 'test_token'}))

        # mock the callback from github
        data = {'code': 'supplied_code', 'state': 'app_state'}
        rv: Response = client.get('/auth', query_string=data, content_type='application/json')

        assert rv.status_code == 200

        _, template, context, _ = templates[0]
        assert template.name == 'authorized.html'
        assert context['fork_endpoint'] == 'http://localhost/fork'

        # make sure state is cleared
        with client.session_transaction() as session:
            assert 'auto_fork_state' not in session
            assert 'github_access_token' in session
            assert session['github_access_token'] == 'test_token'


def test_auth_invalid_state(client):
    with captured_templates(app) as templates:
        with client.session_transaction() as session:
            session['auto_fork_state'] = 'state_mismatch'

        # mock the callback from github
        data = {'code': 'supplied_code', 'state': 'app_state'}
        rv: Response = client.get('/auth', query_string=data, content_type='application/json')

        assert rv.status_code == 406
        _, template, _, _ = templates[0]
        assert template.name == 'error.html'


def test_auth_missing_state(client):
    with captured_templates(app) as templates:
        # mock the callback from github
        data = {'code': 'supplied_code', 'state': 'app_state'}
        rv: Response = client.get('/auth', query_string=data, content_type='application/json')

        assert rv.status_code == 406
        _, template, _, _ = templates[0]
        assert template.name == 'error.html'


def test_auth_missing_code(client):
    with captured_templates(app) as templates:
        with client.session_transaction() as session:
            session['auto_fork_state'] = 'app_state'

        # mock the callback from github
        data = {'state': 'app_state'}
        rv: Response = client.get('/auth', query_string=data, content_type='application/json')

        assert rv.status_code == 406
        _, template, _, _ = templates[0]
        assert template.name == 'error.html'


def test_auth_forbidden(client, monkeypatch):
    with captured_templates(app) as templates:
        with client.session_transaction() as session:
            session['auto_fork_state'] = 'app_state'

        # mock out the successful response from github
        monkeypatch.setattr(requests, "post", mock_post(403, {}))

        # mock the callback from github
        data = {'code': 'code', 'state': 'app_state'}
        rv: Response = client.get('/auth', query_string=data, content_type='application/json')

        assert rv.status_code == 403

        _, template, _, _ = templates[0]
        assert template.name == 'error.html'


# Make sure any unexpected status code results in an error page
def test_auth_service_unavailable(client, monkeypatch):
    with captured_templates(app) as templates:
        with client.session_transaction() as session:
            session['auto_fork_state'] = 'app_state'

        # mock out the successful response from github
        monkeypatch.setattr(requests, "post", mock_post(500, {}))

        # mock the callback from github
        data = {'code': 'code', 'state': 'app_state'}
        rv: Response = client.get('/auth', query_string=data, content_type='application/json')

        assert rv.status_code == 503

        _, template, _, _ = templates[0]
        assert template.name == 'error.html'


def test_fork_success(client, monkeypatch):
    with captured_templates(app) as templates:
        with client.session_transaction() as session:
            session['github_access_token'] = 'test_token'

        # mock out the successful response from github
        monkeypatch.setattr(requests, "post", mock_post(202, {}))

        rv: Response = client.get('/fork')

        assert rv.status_code == 200

        _, template, context, _ = templates[0]
        assert template.name == 'forked.html'
        assert context['base_url'] == 'http://localhost/'


def test_fork_missing_access_token(client):
    with captured_templates(app) as templates:
        rv: Response = client.get('/fork')
        assert rv.status_code == 403

        _, template, _, _ = templates[0]
        assert template.name == 'error.html'


def test_fork_forbidden(client, monkeypatch):
    with captured_templates(app) as templates:
        with client.session_transaction() as session:
            session['github_access_token'] = 'test_token'

        monkeypatch.setattr(requests, "post", mock_post(403, {}))

        rv: Response = client.get('/fork')
        assert rv.status_code == 403

        _, template, _, _ = templates[0]
        assert template.name == 'error.html'


def test_fork_service_service_unavailable(client, monkeypatch):
    with captured_templates(app) as templates:
        with client.session_transaction() as session:
            session['github_access_token'] = 'test_token'

        monkeypatch.setattr(requests, "post", mock_post(500, {}))

        rv: Response = client.get('/fork')
        assert rv.status_code == 503

        _, template, _, _ = templates[0]
        assert template.name == 'error.html'


def test_not_found(client):
    with captured_templates(app) as templates:
        rv: Response = client.get('/random_endpoint')
        assert rv.status_code == 404
        _, template, context, _ = templates[0]
        assert template.name == 'not_found.html'
        assert context['base_url'] == 'http://localhost/'
