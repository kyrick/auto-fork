from dataclasses import dataclass


@dataclass(frozen=True)
class MockResponse:
    """
    Used to mock the status code and json payload from requests.post or requests.get
    """
    status_code: int
    data: dict

    def json(self):
        return self.data


def mock_post(status_code: int, data: dict):
    """
    The return of this function is passed to monkeypatch.setattr() to mock a response.

    example: monkeypatch.setattr(requests, "post", mock_post(202, {'some', 'data'})
    :param status_code:
    :param data:
    :return:
    """
    def _mock_post(*args, **kwargs):
        return MockResponse(status_code, data)
    return _mock_post
