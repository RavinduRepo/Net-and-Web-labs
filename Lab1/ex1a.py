from urllib import request

response = request.urlopen("http://eng.pdn.ac.lk")
print("Status code is: ", response.status) # Prints the status code from the response
body = response.read()
response.close()