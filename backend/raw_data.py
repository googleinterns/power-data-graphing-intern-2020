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


from utils import parse_csv_line


class RawData:
    """Class for processing raw data."""

    def __init__(self, rawfile, number_per_slice, bucket=None):
        self._rawfile = rawfile
        self._number_per_slice = number_per_slice
        self._file = open(rawfile, 'r')
        self._bucket = bucket

    def read(self):
        """Reads raw data for a single slice.

        Returns:
            A list of records.
        """
        if self._file.closed:
            return []

        counter = 0
        records = list()
        while counter < self._number_per_slice:
            line = self._file.readline()
            if line == '':
                self._file.close()
                break
            records.append(parse_csv_line(line))
            counter += 1
        return records

    def readable(self):
        return not self._file.closed

    def close(self):
        if not self._file.closed:
            self._file.close()
