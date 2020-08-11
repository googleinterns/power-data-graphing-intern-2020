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

"""A Module for processing single slice."""
from collections import defaultdict
from math import ceil

from downsample import strategy_reducer
from utils import convert_to_csv
from utils import parse_csv_line


class LevelSlice:
    """A class for processing slice and its records."""

    def __init__(self, filename=None, filenames=None, bucket=None):
        """Initialises slice object.

        filname and filenames cannot be None at the same time.
        filename is used to load and save for single slice, and filenames is used to
        read multiple slices at the same time.

        Args:
            bucket: An bucket object.
            filename: (optional) A string of the path to the slice.
            filenames: (optional) A list of string that represent the path to slices.

        Raises:
            TypeError: Both arguments are None.
        """
        if filename is None and filenames is None:
            raise TypeError
        self._filename = filename
        self._filenames = filenames
        self._bucket = bucket

        # key: channel name, value: list of records.
        self._records = defaultdict(list)
        self._start = -1

    def read(self):
        """Reads records from slice file."""
        if self._filename is None:
            return
        lines = []
        if self._bucket is None:
            with open(self._filename, 'r') as filereader:
                lines = filereader.readlines()
        else:
            blob = self._bucket.blob(self._filename)
            lines = blob.download_as_string().decode().split('\n')
        for line in lines:
            record = parse_csv_line(line)
            if record:
                if self._start == -1:
                    self._start = record[0]
                self._records[record[2]].append(record)

    def read_slices(self, start, end):
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
                    if self._start == -1:
                        self._start = record[0]

    def get_first_timestamp(self):
        """Gets the earliest time of record in this slice."""
        return self._start

    def save(self, records=None):
        """Saves records to slice file."""
        records_list = list()
        if records is not None:
            records_list = records
        else:
            if not self._records:
                return
            for channeled_records in self._records.values():
                records_list.extend(channeled_records)
            records_list = sorted(records_list, key=lambda record: record[0])

        data_csv = convert_to_csv(records_list)
        if self._bucket is None:
            with open(self._filename, 'w') as filewriter:
                filewriter.write(data_csv)
                filewriter.flush()
        else:
            blob = self._bucket.blob(self._filename)
            blob.upload_from_string(data_csv)

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

    def add_records(self, records):
        """Adds records to the slice.

        Args:
            records: A dict of records.
        """
        if self._start == -1:
            start = min([records[channel][0][0]
                         for channel in records.keys() if records[channel]])

            self._start = start
        for channel in records.keys():
            self._records[channel].extend(records[channel])

    def format_response(self):
        """Gets current data in dict type for http response.

        Returns:
            A dict of data indicating the name of channel and its data.
        """
        response = list()
        for channel in self._records.keys():
            response.append({
                'name': channel,
                'data': [[record[0], record[1]] for record in self._records[channel]]
            })
        return response
