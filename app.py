'''
Authors: Cam Kirn, Colin Kirn
Get times from json and run main application to display records for each course
'''

from flask import Flask, render_template, request, redirect, url_for
import json

from courses import Courses, format_course_names


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static/courseImages"


def read_world_records() -> dict[str, dict[str, str]]:
    """
    Author: Cam Kirn
    Open world record json
    """
    with open("world_records.json", "r") as infile:
        world_records = json.load(infile)
    return world_records

def write_cc_json(cc_records: dict[str, dict[str, dict[str, str]]]) -> None:
    """
    Author: Cam Kirn
    Write json for Colin and Cam's records
    """
    with open("cc_records.json", "w") as outfile:
        json.dump(cc_records, outfile)

#No longer used
'''
def populate_cc_json() -> None:
    """
    Author: Cam Kirn
    Write default values to json for Colin and Cam's records
    """
    cc_records = {}
    info_dict = {"time": "9'59\"999", "character": "N/A", "vehicle": "N/A"}
    member_dict = {"Cam": info_dict, "Colin": info_dict, "Difference": "0'00\"000"}
    for course in Courses:
        cc_records[format_course_names(course.name)] = member_dict
    write_cc_json(cc_records)
'''

def update_cc_json(cam_times: list[str], colin_times: list[str]) -> None:
    """
    Author: Cam Kirn
    Take in a list of Cam's times and Colin's times, calculate the difference and then update cc_records with new times and differences 
    """
    cc_records = {}
    for course in Courses:
        cam_time_str = cam_times[course.value-1]
        colin_time_str = colin_times[course.value-1]
        # Times are written as a string in the json, so they must be converted to milliseconds to calculate the difference.
        cam_time_ms = parse_time(cam_time_str)
        colin_time_ms = parse_time(colin_time_str)
        difference_ms = abs(cam_time_ms - colin_time_ms)
        difference_str = format_time(difference_ms)
        cam_dict = {"time": cam_time_str, "character": "N/A", "vehicle": "N/A"}
        colin_dict = {"time": colin_time_str, "character": "N/A", "vehicle": "N/A"}
        member_dict = {"Cam": cam_dict, "Colin": colin_dict, "Difference": difference_str}
        cc_records[format_course_names(course.name)] = member_dict
    write_cc_json(cc_records)

def read_cc_json() -> dict[str, dict[str, dict[str, str]]]:
    """
    Author: Cam Kirn
    Open json for Colin and Cam's records
    """
    with open("cc_records.json", "r") as infile:
        cc_records = json.load(infile)
    return cc_records

def return_time_lists() -> tuple[list[str], list[str], list[str], list[str]]:
    """
    Author: Cam Kirn
    Return 4 lists of Cam's records, Colin's records, the difference between them, and world records
    """
    cc_records = read_cc_json()
    world_records = read_world_records()
    cam_times = []
    colin_times = []
    time_difference = []
    wr_times = []
    for course in cc_records:
        cam_times.append(cc_records[course]['Cam']['time'])
        colin_times.append(cc_records[course]['Colin']['time'])
        time_difference.append(cc_records[course]['Difference'])
        wr_times.append(world_records[course]['time'])
    return cam_times, colin_times, time_difference, wr_times

def parse_time(time: str) -> int:
    """
    Author: Colin Kirn
    Convert a string of a time (formatted as 9'59"999) into an int expressing that time in milliseconds
    """
    try:
        minutes, rest = time.split('\'')
        seconds, milliseconds = rest.split('"')
        return (int(minutes) * 60 * 1000) + (int(seconds) * 1000) + int(milliseconds)
    except:
        return -1

def format_time(ms: int) -> str:
    """
    Author: Colin Kirn
    Convert a time in milliseconds into a string formatted as 9'59"999
    """
    minutes = ms // (60 * 1000)
    ms %= (60 * 1000)
    seconds = ms // 1000
    milliseconds = ms % 1000
    return f"{int(minutes)}'{int(seconds):02d}\"{int(milliseconds):03d}"

def is_p1_winning(p1_time: str, p2_time: str) -> str:
    """
    Author: Cam Kirn
    Return whether or not player 1 is winning based on if their time is lower than player 2's
    """
    p1_ms = parse_time(p1_time)
    p2_ms = parse_time(p2_time)
    if p1_ms < p2_ms:
        return "winning"
    elif p1_ms > p2_ms:
        return "losing"
    else:
        return "tied"

@app.route("/input", methods=["GET", "POST"])
def input_screen():
    cam_times, colin_times, time_difference, wr_times = return_time_lists()

    if request.method == "POST":
        new_data = request.form
        
        for course in Courses:
            i = course.value - 1
            cam_times[i] = new_data.get(f"cam_{course.name}", cam_times[i])
            colin_times[i] = new_data.get(f"colin_{course.name}", colin_times[i])

        update_cc_json(cam_times, colin_times)

        return redirect(url_for("home"))
    return render_template("edit.html", cam_times=cam_times, colin_times=colin_times, courses=Courses, format_course_names=format_course_names)

@app.route("/")
def home():
    #TODO: Implement total row of summed times

    # Separate total row if exists
    '''
    if 'Total' in df['colin'].values:
        total_row = df[df['colin'] == 'Total'].iloc[0]
        df = df[df['colin'] != 'Total'].reset_index(drop=True)
    else:
        total_row = None
    '''

    cam_times, colin_times, time_difference, wr_times = return_time_lists()

    image_dir = "static/courseImages"

    rows = []
    for course in Courses:
        i = course.value - 1
        rows.append({
            "image": f"/{image_dir}/{course.name}.png",
            "cam": cam_times[i],
            "colin": colin_times[i],
            "difference": time_difference[i],
            "world_record": wr_times[i]
        })

    # Add total row at bottom
    '''
    if total_row is not None:
        rows.append({
            'image': '',
            'cam': total_row['cam'],
            'colin': total_row['colin'],
            'difference': total_row['difference'],
            'world_record': total_row['wr']
        })
    '''
    
    return render_template("display.html", rows=rows, calculate_winner=is_p1_winning)

# Route: Best times leaderboard
@app.route("/leaderboard")
def leaderboard_screen():
    cam_times, colin_times, time_difference, wr_times = return_time_lists()
    cam_dict, colin_dict = {},{}

    for course in Courses:
        cam_ms = parse_time(cam_times[course.value - 1])
        colin_ms = parse_time(colin_times[course.value - 1])
        wr_ms = parse_time(wr_times[course.value - 1])
        cam_pct = round((wr_ms / cam_ms) * 100, 2)
        cam_dict[course.name] = cam_pct
        colin_pct = round((wr_ms / colin_ms) * 100, 2)
        colin_dict[course.name] = colin_pct

    combined = []
    for course, number in cam_dict.items():
        combined.append({"player": "Cam", "course":  format_course_names(course), "percentage": number})
    for course, number in colin_dict.items():
        combined.append({"player": "Colin", "course": format_course_names(course), "percentage": number})
    sorted_combined = sorted(combined, key=lambda x: x['percentage'], reverse=True)
    t10 = sorted_combined[:10]
    return render_template("leaderboard.html", top10=t10)

if __name__ == "__main__":
    app.run(debug=True)
