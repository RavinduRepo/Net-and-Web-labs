from urllib import request

response = request.urlopen("https://eng.pdn.ac.lk")
body = response.read()
response.close()

# Printing the type of body variable
print("Type of 'body' variable: ", type(body))