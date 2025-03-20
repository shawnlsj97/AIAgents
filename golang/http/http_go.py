import requests

# GET REQUEST
url = "http://localhost:8080/hello"
response = requests.get(url)

print("GET Response:", response.json())

# POST REQUEST
url = "http://localhost:8080/echo"
data = {"message": "Hello from Python"}

response = requests.post(url, json=data)

print("POST Response:", response.json())
