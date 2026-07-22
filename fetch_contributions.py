import requests
import json
from datetime import datetime, timedelta

USERNAME = "jimeod"

url = f"https://github.com/users/{USERNAME}/contributions"

html = requests.get(url).text

print("Descargado:", len(html))
