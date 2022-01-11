"""Live plotter for SENTRY science data time series.

Example: python sentry_plotter.py -t ./test_sentry_science.txt -x 0 -y 1,2 -n O2,OBS -s
Plots data from live-updating test_sentry_science.txt file, in which
column 0 is a timestamp, and columns 1 and 2 (O2 and OBS) are to be plotted
in subplots. Everything is plotted as a scatter plot.

Authors: Genevieve Flaspohler and Victoria Preston
Update: January 2022
Contact: {geflaspo, vpreston}@mit.edu
"""
import os
import argparse
import time
import yaml
import pandas as pd
import numpy as np

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.animation as animation
from matplotlib.widgets import Button
from matplotlib import style

style.use('fivethirtyeight')

class CallbackXlim(object):
    def __init__(self, obj, idx):
        self.idx = idx
        self.obj = obj
        self.callback_time = time.time()

    def __call__(self, event_ax):
        xloc = matplotlib.dates.num2date(event_ax.xdata)
        self.obj.prev_xlim[self.idx] = self.obj.xlim[self.idx]
        self.obj.xlim[self.idx] = [xloc, None]
        self.obj.live_mode[self.idx] = False
        self.obj.new_xlim[self.idx] = self.obj.xlim[self.idx]


class LiveTimePlot(object):
    """Creates a plot that live updates when data is written to file."""

    def __init__(self, file, time_index=1, col_index=[2, 3],
                 col_names=["X", "Y"], scatter=False, max_pts=3600):
        """Initializes a live plot.

        Arguments:
            file (str): filepointer to data
            time_index (int): part of message with timestamp
            col_index (list(int)): part of message to display
            col_names (list(str)): what to call those data
            scatter (bool): whether to connect points
            max_pts (int): maximum number of plotted points
        """
        self.fig = plt.figure()
        self.file = file
        self.time_index = time_index
        self.col_index = col_index
        self.col_names = col_names
        self.num = len(col_index)  # number of subplots
        self.scatter = scatter
        self.max_pts = max_pts
        self.axs = []
        self.callback_xlim = []
        self.callback_ylim = []

        # Initialize button
        buttonax = self.fig.add_axes([0.45, 0.9, 0.19, 0.075])
        self.button = Button(buttonax, "Home View")

        self.live_mode = [True]*self.num
        self.xlim = [None]*self.num
        self.ylim = [None]*self.num
        self.prev_xlim = [None]*self.num
        self.prev_ylim = [None]*self.num
        self.new_xlim = [None]*self.num
        self.new_ylim = [None]*self.num
        self.button_time = time.time()

        # Initialize date string format
        self.xfmt = mdates.DateFormatter("%H:%M:%S")

        # Create the subplots and their callbacks
        for i in range(1, self.num+1):
            self.axs.append(self.fig.add_subplot(self.num, 1, i))
            self.callback_xlim.append(CallbackXlim(self, i-1))

        # Create the refreshing plot
        ani = animation.FuncAnimation(
            self.fig, self.animate, interval=50, repeat=False)
        plt.show()

    def callback_button(self, event_ax):
        """Resets the window viewing when the Home button is clicked."""
        self.button_time = time.time()
        self.live_mode = [True]*self.num
        self.new_xlim = [None]*self.num
        self.new_ylim = [None]*self.num

    def animate(self, i):
        """How the plot should refresh over time."""
        # Grab the data being written to file
        if os.path.isfile(self.file):
            lines = pd.read_csv(self.file, sep=",", header=None)
            lines[self.time_index] = pd.to_datetime(lines[self.time_index],
                                                    utc=True)
            lines = lines.set_index(self.time_index).sort_index()

            # Capture only the most recent max_pts
            if len(lines) > self.max_pts:
                lines = lines.tail(self.max_pts)

            # Format the axes for the live time plot
            for i, ax in enumerate(self.axs):
                ax.clear()
                ax.xaxis.set_major_formatter(self.xfmt)
                ax.xaxis.set_major_locator(plt.MaxNLocator(10))
                ax.yaxis.set_major_locator(plt.MaxNLocator(10))
                ax.set_title(self.col_names[i])

            # Plot the time plots
            time = lines.index

            # Use color to notify whether time stamp has dropped
            if time[-1] == time[-2]:
                color = "r"
            else:
                color = "b"

            for i, ax in enumerate(self.axs):
                if self.scatter is False:
                    ax.plot(time, lines[self.col_index[i]], c=color)
                else:
                    ax.plot(time, lines[self.col_index[i]], c=color,
                            marker="o", linestyle="")

                if self.new_xlim[i] is not None and not self.live_mode[i]:
                    # Set the new xlimit
                    ax.set_xlim(self.new_xlim[i])

                    # Compute the new y axis spread for all columns
                    max_lim = lines[lines.index >=
                                    self.new_xlim[i][0]].max(axis=0).values
                    min_lim = lines[lines.index >=
                                    self.new_xlim[i][0]].min(axis=0).values
                    PAD = (max_lim - min_lim) * 0.05  # pad 5% of range
                    # Set y limits with padding
                    self.new_ylim[i] = (min_lim[i]-PAD[i], max_lim[i]+PAD[i])
                    ax.set_ylim(self.new_ylim[i])

            self.button.on_clicked(self.callback_button)
            for i, ax in enumerate(self.axs):
                self.fig.canvas.mpl_connect(
                    'button_press_event', self.callback_xlim[i])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--target", action="store", type=str,
                        help="Read data continuously from this file.",
                        default="proc_sentry_default.txt")
    parser.add_argument("-x", "--ax_index", action="store", type=int,
                        help="This is the index of the time column.",
                        default=0)
    parser.add_argument("-y", "--plot_index", action="store", type=str,
                        help="Plot these columns.",
                        default="1,2")
    parser.add_argument("-n", "--plot_names", action="store", type=str,
                        help="Name these columns.",
                        default="1,2")
    parser.add_argument("-s", "--scatter", action="store_true",
                        help="Whether to plot as a scatter plot.",
                        default=False)
    # Create commandline parser
    parse = parser.parse_args()

    # Parse commandline input
    filename = parse.target
    ax_index = parse.ax_index
    scatter = parse.scatter
    col_index = parse.plot_index.split(",")
    col_index = [int(x) for x in col_index]
    col_names = parse.plot_names.split(",")
    col_names = [str(x) for x in col_names]

    tp = LiveTimePlot(filename, ax_index, col_index, col_names, scatter)
