"""Filters SENTRY messages logged to a file for data of interest.

Writes all messages received from seperate queues to seperate file targets.

Example: python sentry_filter.py -t ./data/raw_sentry617.txt -f ./ -n sentry617
File reads in raw data stored in ./data/raw_sentry617.txt and writes filtered
science, status, or instrument data
to ./sentry617_sentry_{status, science, instrument}.

Authors: Genevieve Flaspohler and Victoria Preston
Update: January 2022
Contact: {geflaspo, vpreston}@mit.edu
"""
import os
import argparse

# Globals which may need to change
STATUS_QUEUE = 0
SCIENCE_QUEUE = 34


def filter_status_message(message):
    """Strips the vehicle status message.
        vehicle_status_queue (SDQ 0)
        SentryVehicleState.msg
        float32 INVALID = -999.99 
        ds_acomms_msgs/Vector3_F32 pos_ned
        ds_acomms_msgs/Vector3_F32 goal_ned
        float32 altitude
        float32 heading
        float32 horz_velocity
        float32 vert_velocity
        float32 battery_pct
        uint16 trackline
        bool abort_status
    """
    try:
        return message
    except:
        return None


def filter_science_message(message):
    """Strips the vehicle science message.
        vehicle_scalar_science_queue (SDQ 4)
        SentryScalarScience.msg
        float32 oxygen_concentration
        float32 obs_raw
        float32 orp_raw
        float32 ctd_temperature
        float32 ctd_salinity
        float32 paro_depth
    """
    try:
        packet = str(message).split(" ")
        o2 = packet[0]
        obs = packet[1]
        orp = packet[2]
        temp = packet[3]
        salt = packet[4]
        depth = packet[5]
        return f"{o2},{obs},{orp},{temp},{salt},{depth}"
    except:
        return None


def filter_experimental_message(message):
    """Stand-in function for experimental sensors parsed in queue."""
    pass


def parse_payload(message):
    """Inspects the message and returns the message type.

    One of "status", "science", or None
    Returns message type, message payload, and cleaned timestamp.
    """
    if not "SDQ" in message:
        return None, message, None

    payload = message[message.index("SDQ"):]
    timestamp = message.split("|")[0]

    # Starting from index 4 to remove leading "SDQ "
    try:
        queue = int(payload[4:payload.index(":")])
        payload = payload[payload.index(":")+1:]
        if queue == STATUS_QUEUE:
            return "status", payload, timestamp
        elif queue == SCIENCE_QUEUE:
            return "science", payload, timestamp
        else:
            return None, message, timestamp
    except:
        return None, message, timestamp


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", action="store", type=str,
                        help="Where to look for raw data.",
                        default="./raw_sentry_default.txt")
    parser.add_argument("-f", "--filepath", action="store", type=str,
                        help="Write data at this filepath.",
                        default="./")
    parser.add_argument("-n", "--name", action="store", type=str,
                        help="Write data to a file with this name.",
                        default="")
    # Create commandline parser
    parse = parser.parse_args()

    # Parse commandline input
    name = parse.name
    filepath = parse.filepath
    raw_file = parse.target
    queue_names = ["status", "science", "experimental"]
    queue_filters = [filter_status_message,
                     filter_science_message, filter_experimental_message]
    queue_files = [os.path.join(
        filepath, f"{name}_sentry_{q}.txt") for q in queue_names]

    # Now parse the file target by polling and parsing any new lines
    last_line = 0
    while(1):
        # Idle if no file with raw data
        if not os.path.isfile(raw_file):
            continue

        # Convert raw file to various processed files
        f = open(raw_file, "r").read()
        lines = f.split("\n")
        if last_line == len(lines)-1:  # grab latest lines
            continue
        parse_lines = lines[last_line:]
        last_line = len(lines)-1

        # Populate data
        for i, line in enumerate(parse_lines):
            if len(line) == 0:
                continue

            msg_type, payload, timestamp = parse_payload(line)

            if msg_type is None:  # only care about certain queues
                continue

            # Get the matching queue index for message type
            qidx = queue_names.index(msg_type)

            # Filter the data
            data = queue_filters[qidx](payload)
            if data is None:
                continue

            # Log the filtered data
            if os.path.isfile(queue_files[qidx]):
                mode = "a"
            else:
                mode = "w+"
            print(timestamp)
            print(data)
            with open(queue_files[qidx], mode) as rf:
                rf.write(f"{timestamp+','+data}\n")
                rf.flush()
