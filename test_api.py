import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api/v1/chat"

payload = {
  "organization_id": "org_alliance_logistic",
  "session_id": "session_test_001",
  "text": "Алло, це Дмитро. Треба забрати 10 палет з електронікою з Хмельницького і закинути на склад у Люблін. Мій номер +380501112233, пишіть на dmitro@logistic.ua"
}

def run_test():
    print(f"Sending POST to {API_URL}...")
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print("Response Content:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_test()
