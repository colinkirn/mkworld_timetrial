import requests
from bs4 import BeautifulSoup
import json

wr_dict = {}

def write_wr_json():
    with open("world_records.json", "w") as outfile:
        json.dump(wr_dict, outfile)

def scrape_world_record_times():
    url = "https://mkwrs.com/mkworld/"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print("Failed to fetch world records:", e)
    
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        wr_table = soup.find("table", class_="wr")  # Select main table containing wr info
        rows = wr_table.find_all("tr")
        rows = rows[1:len(rows) - 1] # Cut out first row of headers and last row of total times
        for row in rows:
            cells = row.find_all("td")
            track_name = cells[0].text # First column is names of tracks
            time = cells[1].text # Second column is world record times
            character = cells[6].text # Seventh column is character used
            vehicle = cells[7].text # Eighth column is vehicle used
            info_dict = {"time": time, "character": character, "vehicle": vehicle}
            wr_dict[track_name] = info_dict

    except Exception as e:
        print("Error parsing times:", e)


def main():
    scrape_world_record_times()
    write_wr_json()

if __name__ == "__main__":
    main()
