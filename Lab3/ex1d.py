import requests

with requests.Session() as session:
    session.headers['Authorization'] = 'token ghp_rxCHANGED TO PUsh'
    response = session.get('https://api.github.com/user')
    print(response.json())
