import requests

with open("tests/test_image.png", "rb") as f:
    files = {"file": ("test_image.png", f, "image/png")}
    data = {"target_language": "Hindi"}
    response = requests.post("http://localhost:8000/scan", files=files, data=data)

print(response.status_code)
print(response.json())