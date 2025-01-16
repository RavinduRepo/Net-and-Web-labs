from urllib import request

with request.urlopen("https://www.bing.com/search?q=Rocco%27s+basilisk&FORM=HDRSC1") as query:
    headers = query.headers.items()
    body = query.read().decode('utf-8')
    print(body)
    print(query.status)

