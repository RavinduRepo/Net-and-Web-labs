from urllib import request

response = request.urlopen("http://eng.pdn.ac.lk")
body = response.read()
response.close()

# getting the size of the body in bytes (one byte per letter)
body_size = len(body)
print("Response body size:", body_size, "bytes")