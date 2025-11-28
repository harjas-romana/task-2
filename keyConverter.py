# Run this in Python to get the single-line JSON
import json

with open("serviceAccountKey.json") as f:
    data = json.load(f)
    
print(json.dumps(data))