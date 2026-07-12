import requests

# Test /ask
response = requests.post(
    "http://localhost:8000/ask",
    json={"question": "where is the nearest restroom"}
)
print("POST /ask:", response.status_code)
print(response.text)

# Test /ask with empty question (should be 400)
response2 = requests.post(
    "http://localhost:8000/ask",
    json={"question": ""}
)
print("POST /ask (empty):", response2.status_code)
print(response2.text)

# Test /health
response3 = requests.get("http://localhost:8000/health")
print("GET /health:", response3.status_code)
print(response3.text)