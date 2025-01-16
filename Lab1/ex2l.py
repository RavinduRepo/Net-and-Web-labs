from urllib import parse, request
encoded_query = parse.quote('රවිදු')
print(encoded_query)
with request.urlopen(f"https://www.duckduckgo.com/?q={encoded_query}") as query:
    headers = query.headers.items()
    body = query.read().decode('utf-8')
    print(body)
    print(query.status)
