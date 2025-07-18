import requests
from bs4 import BeautifulSoup

def scrape_world_record_times():
    url = "https://mkwrs.com/mkworld/"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print("Failed to fetch world records:", e)
        return ["N/A"] * 30  # fallback empty values
    
    soup = BeautifulSoup(response.text, "html.parser")

    # Based on inspecting the page, records seem to be inside a table or list.
    # We need to find the correct elements containing the times.
    # (You might want to inspect the page source for exact selectors.)

    # For example, assume times are in table rows with class 'worldrecord' or similar.
    # Here is a generic approach, you must adjust selectors after inspecting site.

    times = []
    try:
        # This is just a placeholder selector — adjust as needed:
        rows = soup.select("table tbody tr")  # Select all rows in main table
        for row in rows[:30]:  # get first 30 rows or whatever you need
            # Suppose time is in 3rd <td> (adjust based on actual site)
            tds = row.find_all("td")
            if len(tds) >= 3:
                time_text = tds[2].get_text(strip=True)
                times.append(time_text)
            else:
                times.append("N/A")
    except Exception as e:
        print("Error parsing times:", e)
        return ["N/A"] * 30

    # If fewer than 30 found, pad:
    while len(times) < 30:
        times.append("N/A")
    return times[:30]
