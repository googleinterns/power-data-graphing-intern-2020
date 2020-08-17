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

"""A module for fetching from multiple-level preprocessing."""

import utils

from level_slices_reader import LevelSlices
from metadata import Metadata


class DataFetcher:
    """Class for for fetching from multiple-level preprocessing."""

    def __init__(self, file_path, root_dir, preprocess_bucket=None):

        self._rawfile = file_path
        self._preprocess_bucket = preprocess_bucket

        original_file_name = utils.get_file_name(file_path)
        self._preprocess_dir = '/'.join([root_dir, original_file_name])

    def is_preprocessed(self):
        """Returns if the raw data is preprocessed.

        Returns:
            A boolean indicating if the raw file is preprocessed.
        """
        metadata = Metadata(self._preprocess_dir,
                            bucket=self._preprocess_bucket)
        error = metadata.load()
        if error is None:
            return True
        return False

    def fetch(self, strategy, number_records, timespan_start, timespan_end):
        """Gets the records in given timespan, downsample the fetched data with
            given strategy if needed.

        Read the records and downsample the records to be within number_records.
        Optional arguments start and end to specify a timespan in which records must be laid.

        Args:
            strategy: A string representing a downsampling strategy.
            number_records: An interger representing number of records to return.
            timespan_start: An integer representing the timestamp in microseconds
                of the start of timespan.
            timespan_end: An integer representing the timestamp in microseconds
                of the end of timespan.

        Returns:
            A list of downsampled data in the given file, and precision for this result.
            Example:
                [
                    {
                        'name':'sys',
                        'data':[
                            [time,power],
                            [time,power]
                        ]},
                    {
                        'name': 'channel2',
                        'data': [
                            [time,power]
                        ]
                    }
                ]
        """
        self._metadata = Metadata(
            self._preprocess_dir, bucket=self._preprocess_bucket)
        self._metadata.load()

        if timespan_start is None:
            timespan_start = self._metadata['start']
        if timespan_end is None:
            timespan_end = self._metadata['end']

        if timespan_start > self._metadata['end'] or timespan_end < self._metadata['start']:
            return []

        required_frequency = number_records / (timespan_end - timespan_start)

        # Finds Downsample Level.
        target_level_index = self._binary_search(
            [self._metadata['levels'][level_name]['frequency']
             for level_name in self._metadata['levels']['names']],
            required_frequency, True)

        target_level = self._metadata['levels'][self._metadata['levels']
                                                ['names'][target_level_index]]

        level_metadata = Metadata(
            self._preprocess_dir, strategy, utils.get_level_name(
                target_level_index), bucket=self._preprocess_bucket)
        level_metadata.load()
        first_slice = self._binary_search([level_metadata[single_slice]
                                           for single_slice in target_level['names']],
                                          timespan_start)
        last_slice = self._binary_search([level_metadata[single_slice]
                                          for single_slice in target_level['names']],
                                         timespan_end)
        target_slices_names = target_level['names'][first_slice:last_slice+1]
        target_slice_paths = [utils.get_slice_path(
            self._preprocess_dir,
            utils.get_level_name(target_level_index),
            single_slice, strategy) for single_slice in target_slices_names]

        # Reads records and downsamples.
        target_slices = LevelSlices(
            target_slice_paths, self._preprocess_bucket)
        target_slices.read(timespan_start, timespan_end)
        number_target_records = target_slices.get_records_count()

        target_slices.downsample(strategy, max_records=number_records)
        downsampled_data = target_slices.format_response()
        number_result_records = target_slices.get_records_count()

        if number_target_records == 0:
            precision = 0
        else:
            precision = number_result_records / \
                number_target_records * \
                (target_level['number']/self._metadata['raw_number'])
        return downsampled_data, precision

    def _binary_search(self, data_list, value, reverse=False):
        """Searches the index of the left or right element closest to the given value from the list,
        if reverse is true, the list is decreasing.

        Args:
            data_list: A list of integers.
            value: The value to be inserted.
            reverse: True if data_list is decreasing.

        Returns:
            An int of index for the result.
        """
        if not data_list:
            return -1

        left = 0
        right = len(data_list) - 1
        pivot = (left + right + 1) // 2

        while left < right:
            if reverse:
                if data_list[pivot] >= value:
                    left = pivot
                else:
                    right = pivot - 1
            else:
                if data_list[pivot] < value:
                    left = pivot
                else:
                    right = pivot - 1
            pivot = (left + right + 1) // 2
        return pivot
