import requests
import json
from bs4 import BeautifulSoup

USERNAME = "jimeod"

url = f"https://github.com/users/{USERNAME}/contributions"

headers = {
    "User-Agent": "Mozilla/5.0"
}

html = requests.get(url, headers=headers).text

soup = BeautifulSoup(html, "html.parser")


cells = soup.select("td.ContributionCalendar-day")


print("Celdas encontradas:", len(cells))


data = {}


for index, cell in enumerate(cells):

    level = cell.get("data-level", "0")

    week = index // 7
    day = index % 7

    data[f"{week},{day}"] = int(level)


with open("contrib_data.json", "w") as f:
    json.dump(data, f)


print("Archivo generado")