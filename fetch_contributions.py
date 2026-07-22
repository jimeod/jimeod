import requests
import json
from bs4 import BeautifulSoup

USERNAME = "jimeod"

url = f"https://github.com/users/{USERNAME}/contributions"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

html = response.text

print("Descargado:", len(html))


soup = BeautifulSoup(html, "html.parser")

cells = soup.select("td.ContributionCalendar-day")

if not cells:
    print("No se encontraron contribuciones")
    exit()


data = {}

for index, cell in enumerate(cells):

    level = cell.get("data-level")

    if level is None:
        level = 0
    else:
        level = int(level)

    week = index // 7
    day = index % 7

    data[f"{week},{day}"] = level


with open("contrib_data.json", "w") as f:
    json.dump(data, f)


print("Guardadas:", len(data), "celdas")
