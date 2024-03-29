# Copyright 2020 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

"""A Module for reading multiple slices."""
from collections import defaultdict
from math import ceil

from downsample import strategy_reducer
from utils import parse_csv_line


class LevelSlices:
    """A class for reading reacords from multiple slices."""

    def __init__(self, filenames, bucket=None):
        self._filenames = filenames
        self._bucket = bucket
        self._records = defaultdict(list)
        self._minList = defaultdict(float)
        self._maxList = defaultdict(float)

    def read(self, start, end):
        """Reads and loads records from a set of slices, only records in the range
        are included.

        Args:
            start: An int for start time.
            end: An int for end time.
        """
        for slice_path in self._filenames:
            lines = []
            if self._bucket is None:
                with open(slice_path, 'r') as filereader:
                    lines = filereader.readlines()
            else:
                blob = self._bucket.blob(slice_path)
                lines = blob.download_as_string().decode().split('\n')
            for line in lines:
                record = parse_csv_line(line)
                if record and (start is None or start <=
                               record[0]) and (end is None or record[0] <= end):
                    self._records[record[2]].append(record)

    def get_records_count(self):
        """Gets number of records in this slice."""
        number = sum(len(channel) for channel in self._records.values())
        return number

    def downsample(self, strategy, downsample_factor=1, max_records=None):
        """Downsamples the records in this slice.

        Args:
            strategy: A string representing downsampling strategy.
            downsample_factor: Take one record per "downsample_factor" records.
            max_records: An int of threshold for each channel after downsampling.

        Returns:
            A dict of downsampled records.
        """

        for channel in self._records.keys():
            if max_records is not None:
                downsample_factor = ceil(
                    len(self._records[channel]) / max_records)
            self._records[channel] = strategy_reducer(
                self._records[channel], strategy, downsample_factor)
        return self._records

    def format_response(self, minList: defaultdict(float), maxList: defaultdict(float)):
        """Gets current data in dict type for http response.

        Returns:
            A dict of data indicating the name of channel and its data.
        """
        response = list()
        for channel in self._records.keys():
            response.append({
                'name': channel,
                'data': [[record[0], record[1]] for record in self._records[channel]],
                'min': minList[channel],
                'max': maxList[channel],
            })
        return response

    def get_min(self):
        if self._records is not None:
            for channel in self._records.keys():
                channelData = self._records[channel]
                min = channelData[0][1]
                for data in channelData:
                    if data[1] < min:
                        min = data[1]
                self._minList[channel] = min
        return self._minList

    def get_max(self):
        if self._records is not None:
            for channel in self._records.keys():
                channelData = self._records[channel]
                max = channelData[0][1]
                for data in channelData:
                    if data[1] > max:
                        max = data[1]
                self._minList[channel] = max
        return self._minList