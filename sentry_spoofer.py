"""Spoofs SENTRY Acoustic communications messages over UDP.

Authors: Genevieve Flaspohler and Victoria Preston
Update: January 2022
Contact: {geflaspo, vpreston}@mit.edu
"""

import argparse
import socket
import time
import numpy as np
from udp_utils import sentry_science_message, sentry_status_message

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--ip", action="store",
                    type=str, help="IP address for spoofer.",
                    default="127.0.0.1")
parser.add_argument("-p", "--port", action="store", type=str,
                    help="Port for spoofer.",
                    default="52464")
parser.add_argument("-f", "--file", action="store", type=str,
                    help="If set, publish line by line from input file.",
                    default=None)
# Create commandline parser
parse = parser.parse_args()

# Parse commandline input
ACOMMS_IP = parse.ip
ACOMMS_PORT = int(parse.port)
file = parse.file

sock = socket.socket(socket.AF_INET,
                     socket.SOCK_DGRAM)

if file is not None:
    data = open(file, 'r').read()
    lines = data.split('\n')
    num_lines = len(lines)
    while(1):
        realline = np.random.randint(0, num_lines)
        msg = np.random.choice([lines[realline], sentry_science_message()])
        if len(msg) > 1:
            print(msg)
            MESSAGE = bytes(msg, encoding="utf8")
            sock.sendto(MESSAGE, (ACOMMS_IP, ACOMMS_PORT))
            time.sleep(0.1)
else:
    while(1):
        msg = np.random.choice(
            [sentry_status_message(), sentry_science_message()])
        print(msg)
        sock.sendto(bytes(msg, encoding='utf8'), (ACOMMS_IP, ACOMMS_PORT))
        time.sleep(20.)
