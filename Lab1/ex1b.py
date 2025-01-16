from urllib import request

response = request.urlopen("http://eng.pdn.ac.lk")
body = response.read()
response.close()

# Extract the 'Server' information
server_info = response.headers.get('Server', 'Unknown')
print("Server:", server_info)
