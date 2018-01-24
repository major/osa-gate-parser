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
import argparse
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


def parse_timedelta(timedelta):
    """Parses the Ansible log timedelta string into seconds."""
    items = re.findall(r"([0-9]+):([0-9]+):([0-9]+)\.[0-9]+", timedelta)[0]
    seconds = (3600 * int(items[0])) + (60 * int(items[1])) + int(items[2])
    return seconds


class GateParser:
    """Class for parsing timing data from OpenStack-Ansible job runs."""

    def __init__(self, args):
        """Constructor function."""
        self.current_play = None
        self.current_task = None
        self.previous_task = None
        self.results = args.number
        self.stats = {}

        self.r = requests.get(args.url[0], stream=True).iter_lines()
        for line in self.r:
            self.process_line(line)

    def process_line(self, raw_line):
        """Process a line from the console output."""
        # Search for any lines with tasks or handlers.
        pattern = re.compile(r"(TASK|RUNNING HANDLER) \[(.*)\][ \*]?")
        result = pattern.search(raw_line)
        if result is not None:
            self.handle_task('name', result.groups()[1])
            return True

        # Search for lines with timestamps and deltas.
        pattern = re.compile(r"[\w ]+  [0-9:]+ \+[0-9]{4} \(([0-9:\.]*)\)\s+"
                             "[0-9:\.]+")
        result = pattern.search(raw_line)
        if result is not None:
            self.handle_task('time', result.groups()[0])
            return True

    def handle_task(self, line_type, result):
        """Handle the TASK lines in the output."""
        # If we received a task line, move the current task to the previous
        # task and record this new task as the current one.
        if line_type == 'name':
            self.previous_task = self.current_task
            self.current_task = result
            return True

        # If we received a time delta, apply it to the prevopus task and
        # clear out the previous task variable.
        if line_type == 'time':
            seconds = parse_timedelta(result)
            self.stats[self.previous_task] = seconds
            return True

    def display_output(self):
        """Pretty prints the stats dict."""
        all_time = pretty_time(sum(self.stats.values()))
        print("---------- TOTAL TIME {} ".format(all_time).ljust(80, '-'))

        sorted_stats = sorted(
            self.stats.items(),
            key=operator.itemgetter(1),
            reverse=True)
        for task_name, total_time in sorted_stats[:self.results]:
            print("{} - {}".format(pretty_time(total_time), task_name))


parser = argparse.ArgumentParser(description='Parse OSA gate logs.')
parser.add_argument(
    '--number', '-n',
    type=int,
    help="Number of results to display",
    default=25
)
parser.add_argument(
    'url',
    type=str,
    nargs=1,
    help="URL to console output"
)
args = parser.parse_args()

x = GateParser(args)
x.display_output()
