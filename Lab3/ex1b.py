import requests

username = 'RavinduRepo' # my github username.
response = requests.get(f'https://api.github.com/users/{username}')
print(response.json())
