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

"""A Module for processing raw data."""
from google.api_core.exceptions import RequestRangeNotSatisfiable
from utils import parse_csv_line
SIZE_ONE_LINE = 50


class RawDataProcessor:
    """Class for processing raw data."""

    def __init__(self, rawfile, number_per_slice, bucket=None):
        self._blob = None
        self._bucket = bucket
        self._eof = False
        self._file = None
        self._file_pointer = 0
        self._loaded_records = []
        self._number_per_slice = number_per_slice
        self._rawfile = rawfile

        if bucket is None:
            self._file = open(rawfile, 'r')
        else:
            self._blob = self._bucket.blob(self._rawfile)

    # def read_next_slice(self):
    #     """Reads raw data for a single slice.

    #     Returns:
    #         A list of records.
    #     """

        # counter = 0
        # records = list()
        # while counter < self._number_per_slice:
        #     line = self._file.readline()
        #     if line == '':
        #         self._file.close()
        #         break
        #     records.append(parse_csv_line(line))
        #     counter += 1
        # return records

    def read_next_slice(self):
        """Reads raw data for a single slice.

        Returns:
            A list of records.
        """
        raw_records = []
        records = []

        if self._bucket is None:
            counter = 0
            while counter < self._number_per_slice:
                line = self._file.readline()
                if line == '':
                    self._file.close()
                    break
                records.append(parse_csv_line(line))
                counter += 1
            return records

        if len(self._loaded_records) - 1 >= self._number_per_slice:
            records = [parse_csv_line(
                line) for line in self._loaded_records[:self._number_per_slice]]
            self._loaded_records = self._loaded_records[self._number_per_slice:]
            return records

        while len(self._loaded_records) + len(raw_records) - 1 < self._number_per_slice:
            try:
                end = self._file_pointer + self._number_per_slice * SIZE_ONE_LINE
                raw_records.extend(self._blob.download_as_string(
                    start=self._file_pointer, end=end).decode().split('\n'))
                self._file_pointer = end
            except RequestRangeNotSatisfiable:
                self._eof = True
                break
        if raw_records and self._loaded_records:
            raw_records[0] = self._loaded_records[-1] + raw_records[0]
            self._loaded_records[-1] = ''

        for index in range(len(self._loaded_records)):
            record = parse_csv_line(self._loaded_records[index])
            if record:
                records.append(record)
        for index, raw_record in enumerate(raw_records):
            if len(records) >= self._number_per_slice:
                self._loaded_records = raw_records[index:]
                break
            record = parse_csv_line(raw_record)
            if record:
                records.append(record)
        return records

    def readable(self):
        """Checks if the raw file is readable.

        Returns:
            A boolnean indicating if raw is readable.
        """
        return not self._eof
