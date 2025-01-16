import requests

with requests.Session() as session:
    session.headers['Authorization'] = 'token ghp_rxCHANGED TO PUsh'
    response = session.post(
        'https://api.github.com/user/repos',
        json={'name': 'test', 'description': 'some test repo'}
    )
    print(response.json())
