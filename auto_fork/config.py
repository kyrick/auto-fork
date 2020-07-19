from os import environ


class FlaskConfig(object):
    SECRET_KEY: str = environ.get('AF_SECRET_KEY')


class AppConfig(object):
    flask = FlaskConfig()
    client_id: str = environ.get('AF_CLIENT_ID')
    client_secret: str = environ.get('AF_CLIENT_SECRET')
    repo_fork_endpoint: str = environ.get('FORK_ENDPOINT', "https://api.github.com/repos/kyrick/auto-fork/forks")
