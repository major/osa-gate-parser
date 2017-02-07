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
"""Parse OSA gate jobs and report on timings."""
import datetime
import re
import sys
from dateutil.parser import parse

import requests


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

    def process_line(self, raw_line):
        """Process a line from the console output."""
        line = raw_line[29:]

        # Are we at the beginning of a play?
        match = re.search(r'PLAY \[(.*)\] \**', line)
        if match is not None:
            self.handle_play(match.groups()[0])
            return True

        # Are we at the beginning of a task?
        if line.startswith('TASK '):
            self.handle_task(line)

    def handle_play(self, play_name):
        """Handle the PLAY lines in the output."""
        if self.current_play != play_name:
            self.previous_task = None

        self.current_play = play_name
        if play_name not in self.stats.keys():
            self.stats[play_name] = {}

    def handle_task(self, line):
        """Handle the TASK lines in the output."""
        match = re.search(r"TASK \[(.*)\] \**", line)
        task_name = match.groups()[0]

        # Get the next line which has the timing data
        timing_line = self.r.next()[29:]

        # Ensure we got timing data -- if not, get the next one
        if timing_line.startswith('task path'):
            timing_line = self.r.next()[29:]

        match = re.search(
            r"^(\w+ \d\d \w+ \d+\s+\d+:\d+:\d+ \+[0-9]+)",
            timing_line)
        task_start = parse(match.groups()[0])

        if self.previous_task is None:
            pass
        else:
            self.stats[self.current_play][self.previous_task]['elapsed'] = (
                task_start - self.stats[self.current_play][self.previous_task]['start']
            )

        self.stats[self.current_play][task_name] = {
            'start': task_start
        }

        self.previous_task = task_name

    def elapsed_sort(self, task):
        """Sort function for sorting tasks by elapsed time."""
        if 'elapsed' in task[1].keys():
            return task[1]['elapsed']
        else:
            return datetime.timedelta(0)

    def display_output(self):
        """Pretty prints the stats dict."""
        for play, tasks in self.stats.items():

            # Print a header for the play
            header = "PLAY: {} ".format(play).ljust(80, '-')
            print(header)

            # Sort the tasks and print them.
            sorted_tasks = sorted(tasks.items(), key=self.elapsed_sort,
                                  reverse=True)
            for task, timings in sorted_tasks[:20]:
                task = "{} | {}".format(
                    str(timings.get(
                        'elapsed',
                        datetime.timedelta(0))).rjust(9),
                    task)
                print(task)


x = GateParser(sys.argv[1])
x.display_output()
