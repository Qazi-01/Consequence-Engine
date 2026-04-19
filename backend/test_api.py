import requests

url = "http://127.0.0.1:5000/simulate"

payload = {
    "scenario": "I want to start a business"
}

res = requests.post(url, json=payload)

print(res.status_code)
print(res.json())