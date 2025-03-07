# tcp-https-and-https-tcp



Using curl:

curl -X POST -d "This is the data I want to send" http://localhost:8000


Using Python requests library:

import requests

data_to_send = "Hello from the client!"
response = requests.post("http://localhost:8000", data=data_to_send)

print("Server Response:")
print(response.text)