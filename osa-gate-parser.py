#!/usr/bin/env python
# Copyright 2017, Major Hayden <major@mhtx.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -----------------------------------------------------------------------------
#
# Usage ./osa-gate-parser.py <GATE_CONSOLE_URL>
#
"""Parse OSA gate jobs and report on timings."""
import operator
import re
import sys
from dateutil.parser import parse

import requests


def pretty_time(seconds):
    """Convert seconds into pretty hours/minutes/seconds."""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    pretty_time = "%02d:%02d:%02d" % (h, m, s)

    return pretty_time


class GateParser:
    """Class for parsing timing data from OpenStack-Ansible job runs."""

    def __init__(self, url):
        """Constructor function."""
        self.current_play = None
        self.previous_task = None
        self.stats = {}

        self.r = requests.get(url, stream=True).iter_lines()
        for line in self.r:
            self.process_line(line)

        self.calculate_duration()

    def process_line(self, raw_line):
        """Process a line from the console output."""
        try:
            timestamp, line = raw_line.split(" | ", 1)
        except ValueError:
            return False

        # Handle each task line
        if line.startswith("TASK") or line.startswith('RUNNING HANDLER'):
            self.handle_task(timestamp, line)
            return True

        # When we get to the PLAY RECAP line, we need to write the final
        # time to the last task we saw and flush the name of the previous task.
        if line.startswith("PLAY RECAP"):

            # Sometimes we get two play recaps in a row without tasks between
            # them.
            if self.previous_task is None:
                return True

            self.stats[self.previous_task].append(parse(timestamp))
            self.previous_task = None
            return True

    def handle_task(self, timestamp, line):
        """Handle the TASK lines in the output."""
        match = re.search(r"(TASK|RUNNING HANDLER) \[(.*)\] \**", line)
        task_name = match.groups()[1]

        timestamp = parse(timestamp)

        # Add a stats entry for the start of this task
        if task_name in self.stats.keys():
            self.stats[task_name].append(timestamp)
        else:
            self.stats[task_name] = [timestamp]

        # Save the ending time for the previous task
        if self.previous_task is not None:
            self.stats[self.previous_task].append(timestamp)

        self.previous_task = task_name

    def calculate_duration(self):
        """Calculate the duration of each task."""
        for task_name, timestamps in self.stats.items():
            total_time = 0

            # If we only got one timestamp, we likely found our first or last
            # task. This needs to be handled better in the future. ;)
            if len(timestamps) % 2 != 0:
                self.stats[task_name] = 0
                continue

            # Create timestamp pairs and calculate the total time.
            timestamp_pairs = [timestamps[x:x + 2]
                               for x in range(0, len(timestamps), 2)]
            for pair in timestamp_pairs:
                total_time += (pair[1] - pair[0]).total_seconds()
            self.stats[task_name] = total_time

    def display_output(self):
        """Pretty prints the stats dict."""
        all_time = pretty_time(sum(self.stats.values()))
        print("---------- TOTAL TIME {} ".format(all_time).ljust(80, '-'))

        sorted_stats = sorted(
            self.stats.items(),
            key=operator.itemgetter(1),
            reverse=True)
        for task_name, total_time in sorted_stats[:50]:
            print("{} - {}".format(pretty_time(total_time), task_name))


x = GateParser(sys.argv[1])
x.display_output()
