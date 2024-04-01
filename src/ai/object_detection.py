import os 
HUGGINGFACE_API_TOKEN = os.environ['HUGGINGFACE_API_TOKEN']
import json
import requests
import time
import cv2

print("HUGGINGFACE_API_TOKEN: ", HUGGINGFACE_API_TOKEN)
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
API_URL = "https://api-inference.huggingface.co/models/facebook/detr-resnet-50"

image = cv2.imread("savannah.jpg")


def query(filename):

    with open(filename, "rb") as f:
        data = f.read()
    
    
    while True:

      try:
          time.sleep(1)
          response = requests.request("POST", API_URL, headers=headers, data=data)
      
          break

      except Exception:

          continue

    return json.loads(response.content.decode("utf-8"))

data = query("savannah.jpg")
print(data)

for result in data:
    box = result["box"]
    xmin = box["xmin"]
    ymin = box["ymin"]
    xmax = box["xmax"]
    ymax = box["ymax"]
    label = result["label"]

    # Draw a rectangle and label on the image
    cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 0, 255), 2)
    cv2.putText(image, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

# Save the image after processing
cv2.imwrite("after_model.jpg", image)

