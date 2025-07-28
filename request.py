"""
Authors: Cam Kirn, Colin Kirn
Scrape all world record data for Mario Kart World from mkwrs.com and write to json
"""

import requests
from bs4 import BeautifulSoup
import json

wr_dict = {}

def write_wr_json() -> None:
    """
    Author: Cam Kirn
    Write world record data to json
    """
    with open("world_records.json", "w") as outfile:
        json.dump(wr_dict, outfile)

def scrape_world_record_times() -> None:
    """
    Authors: Cam Kirn, Colin Kirn

    """
    url = "https://mkwrs.com/mkworld/"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print("Failed to fetch world records:", e)
    
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        wr_table = soup.find("table", class_="wr")
        rows = wr_table.find_all("tr")
        total_row = rows[len(rows) - 1]
        rows = rows[1:len(rows) - 1] # Cut out first row of headers and last row of total times
        for row in rows:
            cells = row.find_all("td")
            track_name = cells[0].text # First column is names of tracks
            time = cells[1].text # Second column is world record times
            character = cells[6].text # Seventh column is character used
            vehicle = cells[7].text # Eighth column is vehicle used
            info_dict = {"time": time, "character": character, "vehicle": vehicle}
            wr_dict[track_name] = info_dict
        wr_dict['total'] = {"time": total_row.find_all("td")[1].text}
    except Exception as e:
        print("Error parsing times:", e)

if __name__ == "__main__":
    scrape_world_record_times()
    write_wr_json()
