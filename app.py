from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
import json
from enum import IntEnum
from courses import Courses


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
    return render_template('edit.html', df=df, next_screen='home')

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
            'world_record': total_row['wr']
        })
    return render_template('display.html', rows=rows, next_screen='input_screen')

if __name__ == "__main__":
    app.run(debug=True)
