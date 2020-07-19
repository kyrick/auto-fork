from os import environ


class FlaskConfig(object):
    SECRET_KEY: str = environ.get('AF_SECRET_KEY', 'localtest')


class GitHubConfig(object):
    client_id: str = environ.get('AF_CLIENT_ID')
    client_secret: str = environ.get('AF_CLIENT_SECRET')
    fork_endpoint: str = environ.get('AF_FORK_ENDPOINT', "https://api.github.com/repos/kyrick/auto-fork/forks")
    authorize_endpoint: str = environ.get('AF_AUTH_ENDPOINT', "https://github.com/login/oauth/authorize")
    token_endpoint: str = environ.get('AF_TOKEN_ENDPOINT', "https://github.com/login/oauth/access_token")


class AppConfig(object):
    flask = FlaskConfig()
    github = GitHubConfig()
