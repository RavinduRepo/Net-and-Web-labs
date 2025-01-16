from urllib import request

response = request.urlopen("http://unknown.pdn.ac.lk")
print("Response", response)
body = response.read()
response.close()


response = request.urlopen("http://eng.pdn.ac.lk/unknown")
print("Response", response)
body = response.read()
response.close()
