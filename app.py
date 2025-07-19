from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
import os
import json
from enum import IntEnum

class Courses(IntEnum):
    Mario_Bros_Circuit = 1
    Crown_City = 2
    Whistlestop_Summit = 3
    DK_Spaceport = 4
    Desert_Hills = 5
    Shy_Guy_Bazaar = 6
    Wario_Stadium = 7
    Airship_Fortress = 8
    DK_Pass = 9
    Starview_Peak = 10
    Sky_High_Sundae = 11
    Wario_Shipyard = 12
    Koopa_Troopa_Beach = 13
    Faraway_Oasis = 14
    Peach_Stadium = 15
    Peach_Beach = 16
    Salty_Salty_Speedway = 17
    Dino_Dino_Jungle = 18
    Great_Block_Ruins = 19
    Cheep_Cheep_Falls = 20
    Dandelion_Depths = 21
    Boo_Cinema = 22
    Dry_Bones_Burnout = 23
    Moo_Moo_Meadows = 24
    Choco_Mountain = 25
    Toads_Factory = 26
    Bowsers_Castle = 27
    Acorn_Heights = 28
    Mario_Circuit = 29
    Rainbow_Road = 30


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/courseImages'

# Helper: fetch world records from json
def fetch_world_records():
    with open("world_records.json", "r") as infile:
        world_records = json.load(infile)

    wr_times = []
    for course in world_records:
        wr_times.append(world_records[course]["time"])
    return wr_times

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
        return redirect(url_for("home"))

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
        <a href="{{ url_for('home') }}">Back to home</a>
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
        'cam': format_time(df['cam_ms'].sum()),
        'colin': format_time(df['colin_ms'].sum()),
        'difference': format_time(df['difference_ms'].sum())
    }

    df.drop(['colin_ms', 'cam_ms', 'difference_ms'], axis=1, inplace=True)
    df = df[['cam', 'colin', 'difference']]
    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
    return df

# Route: main display
@app.route("/")
def home():
    df = pd.read_csv("numbers.csv")

    # Separate total row if exists
    if 'Total' in df['colin'].values:
        total_row = df[df['colin'] == 'Total'].iloc[0]
        df = df[df['colin'] != 'Total'].reset_index(drop=True)
    else:
        total_row = None

    cam_times = df['cam'].tolist()
    colin_times = df['colin'].tolist()
    time_difference = df['difference'].tolist()
    wr_times = fetch_world_records()

    image_dir = "static/courseImages"

    rows = []
    for course in Courses:
        i = course.value - 1
        rows.append({
            'image': f"/{image_dir}/{course.name}.png",
            'cam': cam_times[i],
            'colin': colin_times[i],
            'difference': time_difference[i],
            'world_record': wr_times[i]
        })

    # Add total row at bottom
    if total_row is not None:
        rows.append({
            'image': '',
            'cam': total_row['cam'],
            'colin': total_row['colin'],
            'difference': total_row['difference'],
            'image': '',
            'world_record': total_row['wr']
        })
    return render_template_string("""
        <h1>Mario Kart Times</h1>
        <table border="1" cellspacing="0" cellpadding="5">
            <tr><th>Course</th><th>Cam</th><th>Colin</th><th>Difference</th><th>World Record</th></tr>
            {% for row in rows %}
                <tr>
                    <td>{% if row.image %}<img src="{{ row.image }}" height="50">{% endif %}</td>
                    <td>{{ row.cam }}</td>
                    <td>{{ row.colin }}</td>
                    <td>{{ row.difference }}</td>
                    <td>{{ row.world_record }}</td>
                </tr>
            {% endfor %}
        </table>
        <br>
        <a href="{{ url_for('input_screen') }}">Edit Times</a>
    """, rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
