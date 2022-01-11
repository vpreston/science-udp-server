"""Filters USBL messages logged to a file for data of interest.

Writes all messages received to seperate file targets.

Example: python usbl_filter.py -t ./data/raw_usbl.txt -f ./ -n sentry613
Reads in all USBL messages logged to ./data/raw_usbl.txt and writes
filtered status messages to ./sentry613_usbl_{sentry, ship, jason, ctd}.txt.

Authors: Genevieve Flaspohler and Victoria Preston
Update: January 2022
Contact: {geflaspo, vpreston}@mit.edu
"""
import os
import argparse

# THESE MAY NEED TO BE UPDATED DEPENDING ON THE SPECIFIC CRUISE
SENTRY_ID = str(0)
JASON_ID = str(1)
SHIP_ID = str(2)
CTD_ID = str(5)


def filter_message(message, sentry_file_target, jason_file_target,
                   ship_file_target, ctd_file_target):
    """Filters message of format:
    VFR 2019/09/24 13:27:58.033 2 0 SOLN_USBL -125.079565 44.489675 -597.900 0.000 10 0.00 0.00
    """
    mess = str(message)
    packets = mess.split(" ")
    new_stamp = packets[1].replace("/", "-")  # standadize timestamp
    # extract relevant info
    info = f"{new_stamp} {packets[2]},{packets[6]},{packets[7]},{packets[8]}"

    if "VFR" in packets[0]:
        if packets[4] == SENTRY_ID and "USBL" in packets[5]:
            if os.path.isfile(sentry_file_target):
                mode = "a"
            else:
                mode = "w+"
            with open(sentry_file_target, mode) as rf:
                rf.write(f"{info}\n")
                rf.flush()
        elif packets[4] == JASON_ID and "USBL" in packets[5]:
            if os.path.isfile(jason_file_target):
                mode = "a"
            else:
                mode = "w+"
            with open(jason_file_target, mode) as rf:
                rf.write(f"{info}\n")
                rf.flush()
        elif packets[4] == SHIP_ID and "SOLN_GPS0" in packets[5]:
            if os.path.isfile(ship_file_target):
                mode = "a"
            else:
                mode = "w+"
            with open(ship_file_target, mode) as rf:
                rf.write(f"{info}\n")
                rf.flush()
        elif packets[4] == CTD_ID and "USBL" in packets[5]:
            if os.path.isfile(ctd_file_target):
                mode = "a"
            else:
                mode = "w+"
            with open(ctd_file_target, mode) as rf:
                rf.write(f"{info}\n")
                rf.flush()
        else:
            pass
    else:
        pass

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", action="store", type=str,
                        help="Where to look for raw data.",
                        default="./raw_usbl.txt")
    parser.add_argument("-f", "--filepath", action="store", type=str,
                        help="Write data at this filepath.",
                        default="./")
    parser.add_argument("-n", "--name", action="store", type=str,
                        help="Write data to a file with this name.",
                        default="")
    # Create commandline parser
    parse = parser.parse_args()

    # Parse commandline input
    filepath = parse.filepath
    name = parse.name
    raw_file = parse.target
    queue_names = ["sentry", "jason", "ship", "ctd"]
    queue_filter = filter_message
    queue_files = [os.path.join(filepath, f"{name}_usbl_{q}.txt")
                   for q in queue_names]

    # Now parse the file target by polling and parsing any new lines
    last_line = 0
    while(1):
        # Idle if no file
        if not os.path.isfile(raw_file):
            continue

        # Convert raw file to various processed files
        f = open(raw_file, "r").read()
        lines = f.split("\n")
        if last_line == len(lines)-1:  # get latest lines
            continue
        parse_lines = lines[last_line:]
        last_line = len(lines)-1

        # Populate data
        for line in parse_lines:
            if len(line) == 0:
                continue
            filter_message(line, queue_files[0], queue_files[1],
                           queue_files[2], queue_files[3])
