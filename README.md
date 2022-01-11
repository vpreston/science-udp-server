# science-udp-server
A listening, saving, and visualizing tool for standard acoustic communications messages served over UDP by AUV SENTRY.

This repository contains UDP tools used to visualize acoustically communicated SENTRY queues during the Michel Guaymas Basin Cruise, 2021. 
When a ship is within acoustic communication range with SENTRY, the status, science, and other standard (or experimental) queues are updated at a rate of one measurements every 30-120 seconds (depending on connection quality and number of queues engaged). 
These tools can be used to log USBL-served location information about SENTRY and other in-water entities (e.g., JASON, CTD Rosette, Gliders) and to log and visualize SENTRY-modem-served messages with instrument information embedded.

## Dependencies
These tools are written in Python 3.5+ and have been tested on an Ubuntu 18.04 operating system. Libraries necessary are:
* socket
* argparse
* datetime
* pandas
* numpy
* matplotlib
* yaml
* bagpy

## Workflow
The `listener.py` utility is the only tool that requires a connection to the SENTRY network (this implies that it must be run ship-side if doing remote operations). This tool logs ALL USBL and/or SENTRY messages that are passed over UDP on the network by running:

```python listener.py -i 127.0.0.1 -p 100 -f ./ -n sentry614 -v```

where the the IP address (`-i`) and port (`-p`) are used to indicate the USBL or SENTRY message address to listen to, and a filepath and filename are specified (`-f`, `-n`). All messages recieved over the port can be optionally printed to the executing terminal for monitoring (`-v`). For remote operations, the filepath and filename that the logs are written could be on synced server which can be polled from shore.

With `listener.py` running, for parsing and visualizing data, the `usbl_filter.py`, `sentry_filter.py`, and `sentry_plotter.py` utilities should be used. Both of the `_filter.py` utilities will read in a pointer to a raw UDP listener log file, and sort messages into new log files under different queue names (e.g., *science*, *status*, *ship*, *jason*, and so on). The USBL filter seperates location information between different ID objects (like SENTRY, JASON, the ship, a CTD Rosette) and the SENTRY filter seperates based on type of queue message.

The new files created by the filter utilities can then be visualized by `sentry_plotter.py` which reads in different queue targets and displays either time or spatial plots which can be updated live if the listener, filter, and plotter are all simultaneously running. The plots have a rudimentary "zoom" feature which can be used to look more closely at a subset of the most recent data messages.

Examples of how to run all utilities in a terminal are provided at the top of each script.

To test the workflow, a `sentry_spoofer.py` is provided which can generate or read out messages of the right format for the SENTRY or USBL services.

## Contact
For questions or comments on this work, please contact Victoria Preston (vpreston) or Genevieve Flaspohler (geflaspohler). An MIT license is applied to this work.