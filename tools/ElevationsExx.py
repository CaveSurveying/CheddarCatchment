#!/usr/bin/env python3
import os
import subprocess
import shutil
import re

"""
Traverses all folders from the root it runs in
Adds a folder called NOTES_DIR  if a subdirectory does not exist.
(assumes all subdirectories that contain a .th file with data contain o further data!)
Produces the .xvi file into the folder.
Produces the .th2 file into the survey folder
Need a thconfig1 file that contains the xvi file that contains
export map -proj [elevation  0] -o TempE000.xvi
The elevation values need to be set to match the elevation required.
Modifies the .th file to include the new th2 file with the other imputs,
Modifying .th file fails if no input lines already exist ##FIXME##

###Improvements to be implimented###
Producesand delete a thconfig file
"""

ELEVATION = "315"
NOTES_DIR = "Notes"

def contains_centreline(th_file):
    try:
        with open(th_file, "r") as f:
            for line in f:
                if line.strip().startswith("centreline"):
                    return True
    except FileNotFoundError:
        print(f"Error: File {th_file} not found.")
    return False

def extract_xvi_data(xvi_file):
    try:
        with open(xvi_file, "r") as f:
            content = f.read()
        match = re.search(r"set XVIstations {\n((?:.*\n)+?)}", content, re.DOTALL)
        if not match:
            print(f"Warning: No match found in {xvi_file}")
            return None
        station_data = match.group(1).strip().split("\n")
        print("Extracted station data:", station_data)
        stations = []
        for line in station_data:
            parts = line.strip("{} ").split()
            if len(parts) == 3:
                try:
                    x, y, name = float(parts[0]), float(parts[1]), parts[2]
                    stations.append((x, y, name))
                    print(f"Matched station: x={x}, y={y}, name={name}")
                except ValueError:
                    print(f"Warning: Invalid station format in line: {line}")
            else:
                print(f"Error: Expected 3 elements in station line, but got {len(parts)} in {line}")
        if not stations:
            return None
        min_x, max_x = min(s[0] for s in stations), max(s[0] for s in stations)
        min_y, max_y = min(s[1] for s in stations), max(s[1] for s in stations)
        x1, y1, first_stn = stations[0]
        return abs(max_x - min_x) + 128, abs(max_y - min_y) + 128, abs(x1 - min_x), abs(y1 - min_y), first_stn
    except FileNotFoundError:
        return None

def modify_th_file(th_file_path, directory_name):
    with open(th_file_path, "r") as f:
        lines = f.readlines()
    insert_index = next((i for i, line in enumerate(lines) if line.lstrip().startswith("input ")), None)
    insert_text = f"input {directory_name}E{ELEVATION}.th2\n\nmap {directory_name}ME{ELEVATION}\n    {directory_name}SE{ELEVATION}_1\nendmap\n"
    new_lines = lines[:insert_index+1] + [insert_text] + lines[insert_index+1:] if insert_index is not None else lines + ["\n", insert_text]
    with open(th_file_path, "w") as f:
        f.writelines(new_lines)

def move_and_rename_xvi_file(base_dir, subdir, subdir_name):
    old_xvi_path = os.path.join(base_dir, f"TempE{ELEVATION}.xvi")
    new_xvi_path = os.path.join(subdir, f"{subdir_name}E{ELEVATION}.xvi")
    if os.path.exists(old_xvi_path):
        shutil.move(old_xvi_path, new_xvi_path)
        subprocess.run(["svn", "add", new_xvi_path], check=False)

def process_directory(base_dir, subdir_path, entry, thconfig_path):
    th_source = os.path.join(subdir_path, f"{entry}.th")
    if os.path.isfile(th_source) and contains_centreline(th_source):
        rel_thconfig = os.path.relpath(thconfig_path, start=subdir_path)
        try:
            subprocess.run(["therion", "-q", "-L",  "-s", f"{entry}.th", rel_thconfig], cwd=subdir_path, check=True)
            subdirs = [d for d in os.listdir(subdir_path) if os.path.isdir(os.path.join(subdir_path, d))]
            if len(subdirs) == 1:
                target_subdir = os.path.join(subdir_path, subdirs[0])
                print(f"Using subdirectory: {subdirs[0]}")
            else:
                target_subdir = os.path.join(subdir_path, NOTES_DIR)
                os.makedirs(target_subdir, exist_ok=True)
                subprocess.run(["svn", "add", target_subdir], check=False)
            move_and_rename_xvi_file(base_dir, target_subdir, entry)
            xvi_file = os.path.join(target_subdir, f"{entry}E{ELEVATION}.xvi")
            xvi_data = extract_xvi_data(xvi_file)
            th2_file = os.path.join(subdir_path, f"{entry}E{ELEVATION}.th2")
            if xvi_data:
                th2_header = (f"encoding  utf-8\n"
                              f"##XTHERION## xth_me_area_adjust -128.0 -128.0 {xvi_data[0]} {xvi_data[1]}\n"
                              f"##XTHERION## xth_me_area_zoom_to 100\n"
                              f"##XTHERION## xth_me_image_insert {{{xvi_data[2]} 1 1.0}} {{{xvi_data[3]} {xvi_data[4]}}} {os.path.relpath(xvi_file, start=subdir_path)} 0 {{}}\n\n")
            else:
                print(f"Warning: No valid xvi data found for {xvi_file}. Using default header.")
                th2_header = "encoding  utf-8\n\n"
            th2_content = f"scrap {entry}SE{ELEVATION}_1 -projection [elevation {int(ELEVATION)}] -scale [-128.0 -128.0 3238.23 -128.0 0.0 0.0 85.502242 0.0 m]\nendscrap\n"
            with open(th2_file, "w") as f:
                f.write(th2_header + th2_content)
            subprocess.run(["svn", "add", th2_file], check=False)
            modify_th_file(th_source, entry)
        except subprocess.CalledProcessError:
            print(f"Error processing {th_source}")
    else:
        print(f"Skipping {th_source}: No 'centreline' found or file missing.")

def main():
    base_dir = os.getcwd()
    thconfig_path = os.path.join(base_dir, "thconfig1")
    if not os.path.isfile(thconfig_path):
        print(f"Error: 'thconfig1' not found in {base_dir}")
        return
    for root, dirs, _ in os.walk(base_dir):
        for entry in dirs:
            process_directory(base_dir, os.path.join(root, entry), entry, thconfig_path)

if __name__ == '__main__':
    main()
