import requests

BASE_URL = "https://restcountries.com/v3.1/name/"


def get_country_info(country: str):

    url = BASE_URL + country

    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()[0]

    result = {
        "name": data["name"]["common"],
        "capital": data.get("capital", ["Unknown"])[0],
        "region": data.get("region", "Unknown"),
        "population": data.get("population", 0),
        "flag": data.get("flags", {}).get("png", "")
    }

    return result