import requests

url = "http://127.0.0.1:5000/simulate"

payload = {
    "scenario": "I want to start going to the gym, but I have a lot of work to do and I feel tired after work. What are the consequences of going to the gym regularly for the next 6 months?   What are the consequences of not going to the gym regularly for the next 6 months?"
}

res = requests.post(url, json=payload)

print(res.status_code)
print(res.json())