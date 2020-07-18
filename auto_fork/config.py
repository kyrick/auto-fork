from os import environ


class FlaskConfig(object):
    SECRET_KEY: str = environ.get('SECRET_KEY')


class AppConfig(object):
    flask = FlaskConfig()
    client_id: str = environ.get('CLIENT_ID')
    client_secret: str = environ.get('CLIENT_SECRET')
