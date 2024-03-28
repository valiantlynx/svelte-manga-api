import time
import requests
import json
import os
HUGGINGFACE_API_TOKEN = os.environ['HUGGINGFACE_API_TOKEN']
print("HUGGINGFACE_API_TOKEN: ", HUGGINGFACE_API_TOKEN)

headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}

API_URL = "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-es"


def query(payload):

    data = json.dumps(payload)

    time.sleep(1)

    while True:

        try:

            response = requests.request(
                "POST", API_URL, headers=headers, data=data)
            break

        except Exception:

            continue

    return json.loads(response.content.decode("utf-8"))


data = query(
    {
        "inputs": "Hello I'm valiantlynx",
    }
)
print(data)
