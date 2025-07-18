from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
import os
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/courseImages'

# Helper: fetch world records from mkwrs.com
def fetch_world_records():
    url = "https://mkwrs.com/mkworld/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find("table")

    records = []
    for row in table.find_all("tr")[1:]:  # skip header
        cells = row.find_all("td")
        if len(cells) >= 5:
            wr_time = cells[4].text.strip()
            records.append(wr_time)
        if len(records) == 30:
            break
        print(cells)
    return records

# Route: input screen
@app.route("/input", methods=["GET", "POST"])
def input_screen():
    if request.method == "POST":
        new_data = request.form
        df = pd.read_csv("numbers.csv")

        for i in range(30):  # assuming 30 rows
            df.at[i, 'colin'] = new_data.get(f'colin_{i}', df.at[i, 'colin'])
            df.at[i, 'cam'] = new_data.get(f'cam_{i}', df.at[i, 'cam'])

        # Recalculate differences
        df = update_differences(df)

        df.to_csv("numbers.csv", index=False)
        return redirect(url_for("display"))

    df = pd.read_csv("numbers.csv")
    return render_template_string("""
        <h1>Edit Colin and Cam Times</h1>
        <form method="POST">
            {% for i in range(30) %}
                <label>Colin {{ i + 1 }}: <input name="colin_{{ i }}" value="{{ df.colin[i] }}"></label>
                <label>Cam {{ i + 1 }}: <input name="cam_{{ i }}" value="{{ df.cam[i] }}"></label><br>
            {% endfor %}
            <input type="submit" value="Update">
        </form>
        <a href="{{ url_for('display') }}">Back to display</a>
    """, df=df)

# Helper: convert time string to ms
def parse_time(time_str):
    try:
        minutes, rest = time_str.split(':')
        seconds, milliseconds = rest.split('.')
        return (int(minutes) * 60 * 1000) + (int(seconds) * 1000) + int(milliseconds)
    except:
        return 0

# Helper: convert ms back to time string
def format_time(ms):
    minutes = ms // (60 * 1000)
    ms %= (60 * 1000)
    seconds = ms // 1000
    milliseconds = ms % 1000
    return f"{int(minutes)}:{int(seconds):02d}.{int(milliseconds):03d}"

# Helper: recalculate difference and total
def update_differences(df):
    df = df.copy()
    df = df[df['colin'] != "Total"].reset_index(drop=True)
    
    df['colin_ms'] = df['colin'].apply(parse_time)
    df['cam_ms'] = df['cam'].apply(parse_time)
    df['difference_ms'] = df['colin_ms'] - df['cam_ms']
    df['difference'] = df['difference_ms'].apply(format_time)

    total_row = {
        'colin': format_time(df['colin_ms'].sum()),
        'difference': format_time(df['difference_ms'].sum()),
        'cam': format_time(df['cam_ms'].sum())
    }

    df.drop(['colin_ms', 'cam_ms', 'difference_ms'], axis=1, inplace=True)
    df = df[['colin', 'difference', 'cam']]
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    return df

# Route: main display
@app.route("/display")
def display():
    df = pd.read_csv("numbers.csv")

    # Separate total row if exists
    if 'Total' in df['colin'].values:
        total_row = df[df['colin'] == 'Total'].iloc[0]
        df = df[df['colin'] != 'Total'].reset_index(drop=True)
    else:
        total_row = None

    numbers_a = df['colin'].tolist()
    numbers_b = df['difference'].tolist()
    numbers_c = df['cam'].tolist()

    try:
        numbers_d = fetch_world_records()
    except:
        numbers_d = ["N/A"] * len(numbers_a)

    image_dir = "static/courseImages"
    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith(".png")])

    rows = []
    for i in range(min(len(numbers_a), len(image_files), len(numbers_d))):
        rows.append({
            'a': numbers_a[i],
            'b': numbers_b[i],
            'c': numbers_c[i],
            'image': f"/{image_dir}/{image_files[i]}",
            'd': numbers_d[i]
        })

    # Add total row at bottom
    if total_row is not None:
        rows.append({
            'a': total_row['colin'],
            'b': total_row['difference'],
            'c': total_row['cam'],
            'image': '',
            'd': 'Total'
        })

    return render_template_string("""
        <h1>Mario Kart Times</h1>
        <table border="1" cellspacing="0" cellpadding="5">
            <tr><th>Colin</th><th>Diff</th><th>Cam</th><th>Image</th><th>WR</th></tr>
            {% for row in rows %}
                <tr>
                    <td>{{ row.a }}</td>
                    <td>{{ row.b }}</td>
                    <td>{{ row.c }}</td>
                    <td>{% if row.image %}<img src="{{ row.image }}" height="50">{% endif %}</td>
                    <td>{{ row.d }}</td>
                </tr>
            {% endfor %}
        </table>
        <br>
        <a href="{{ url_for('input_screen') }}">Edit Times</a>
    """, rows=rows)

# Redirect root to /display
@app.route("/")
def home():
    return redirect("/display")

if __name__ == "__main__":
    app.run(debug=True)
