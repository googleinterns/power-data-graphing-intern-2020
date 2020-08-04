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

"""Multiple-level preprocess module."""

from math import ceil
from json import dump
from json import load
import os

from level_slice import LevelSlice
from raw_data import RawData
import utils

DOWNSAMPLE_LEVEL_FACTOR = 100
METADATA = 'metadata.json'
PREPROCESS_DIR = 'mld-preprocess'
MINIMUM_NUMBER_OF_RECORDS_LEVEL = 600
NUMBER_OF_RECORDS_PER_SLICE = 200000

RAW_LEVEL_DIR = 'level0'
STRATEGIES = ['max', 'min', 'avg']
UNIX_TIMESTAMP_LENGTH = 16

TEST_FILENAME = 'rand.csv'


class MultipleLevelPreprocess:
    """Class for multiple level preprocessing"""

    def __init__(self, filename, root_dir=PREPROCESS_DIR):
        self._rawfile = filename
        self._preprocessed = False

        experiment_name = utils.get_experiment_name(filename)
        self._preprocess_dir = '/'.join([root_dir, experiment_name])
        metadata_path = '/'.join([self._preprocess_dir, METADATA])

        if os.path.exists(metadata_path):
            self._preprocessed = True

    def is_preprocessed(self):
        """Returns if the raw data is preprocessed."""
        return self._preprocessed

    def multilevel_inference(self, strategy, number_records, start, end):
        """Reads the preprocessing file and downsample with the given strategy for HTTP request.

        Assume the records file is on local disk, read the records and downsample the records
        to be within max records.
        Optional arguments start and end to specify a timespan in which records must be laid.

        Args:
            strategy: A string representing downsampling strategy.
            number_records: An interger representing number of records to return.
            start: An interger representing start of timespan.
            end: An interger representing the end of timespan.

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
        metadata_path = '/'.join([self._preprocess_dir, METADATA])
        with open(metadata_path, 'r') as filereader:
            self._metadata = load(filereader)

        if start is None:
            start = self._metadata['start']
        if end is None:
            end = self._metadata['end']

        if start > self._metadata['end'] or end < self._metadata['start']:
            return []

        required_frequency = number_records / (end - start)

        # Finds Downsample Level.
        target_level_index = self._binary_search(
            [self._metadata['levels'][level_name]['frequency']
             for level_name in self._metadata['levels']['names']],
            required_frequency, True)

        target_level = self._metadata['levels'][self._metadata['levels']
                                                ['names'][target_level_index]]
        if target_level_index == 0:
            metadata_dir = '/'.join([self._preprocess_dir,
                                     RAW_LEVEL_DIR, METADATA])
        else:
            metadata_dir = '/'.join([self._preprocess_dir, strategy,
                                     utils.get_level_name(target_level_index), METADATA])
        # Finds target slices.
        with open(metadata_dir, 'r') as filereader:
            level_metadata = load(filereader)
        first_slice = self._binary_search([level_metadata[single_slice]
                                           for single_slice in target_level['names']], start)
        last_slice = self._binary_search([level_metadata[single_slice]
                                          for single_slice in target_level['names']], end)
        target_slices_names = target_level['names'][first_slice:last_slice+1]
        target_slice_paths = [utils.get_slice_path(
            self._preprocess_dir,
            target_level_index, single_slice, strategy) for single_slice in target_slices_names]

        # Reads records and downsamples.
        target_slices = LevelSlice(filenames=target_slice_paths)
        target_slices.read_slices(start, end)
        number_target_records = target_slices.get_number_records()

        target_slices.downsample(strategy, max_records=number_records)
        downsampled_data = target_slices.format_response()
        number_result_records = target_slices.get_number_records()

        if number_target_records == 0:
            precision = 0
        else:
            precision = number_result_records / \
                number_target_records * \
                (target_level['number']/self._metadata['raw_number'])
        return downsampled_data, precision

    def multilevel_preprocess(self,
                              number_per_slice,
                              downsample_level_factor,
                              minimum_number_level):
        """Multiple level downsampling entry point.

        Downsamples the raw data from given filename with each of the strategy,
        in a hierarchical fation.

        Args:
            number_per_slice: An int that represents number of records for one slice.
            downsample_level_factor: An int that represents downsample factor between levels.
            minimum_number_level: An int that represents the minimum number of records for a level.
        """
        self._number_per_slice = number_per_slice
        self._downsample_level_factor = downsample_level_factor
        self._minimum_number_level = minimum_number_level
        self._metadata = dict()

        raw_number_records, start, end = self._get_raw_meta_info()
        self._metadata['start'] = int(start)
        self._metadata['end'] = int(end)
        self._metadata['raw_number'] = raw_number_records
        self._metadata['raw_file'] = self._rawfile

        levels, level_names = self._get_levels_metadata(
            raw_number_records, end - start)

        self._metadata['levels'] = dict()
        self._metadata['levels']['names'] = level_names
        for name, level in zip(level_names, levels):
            self._metadata["levels"][name] = level

        utils.mkdir(self._preprocess_dir)
        self._raw_preprocess(number_per_slice)
        with open('/'.join([self._preprocess_dir, METADATA]), 'w') as filewriter:
            dump(self._metadata, filewriter)
        for strategy in STRATEGIES:
            self._preprocess_single_startegy(strategy)
        self._preprocessed = True

    def _raw_preprocess(self, number_per_slice):
        """Splits raw data into slices. keep start time of each slice in a json file.

        Args:
            number_per_slice: An int of records to keep for each slice.
        """
        raw_slice_metadata = dict()
        raw_data = RawData(self._metadata['raw_file'], number_per_slice)
        utils.mkdir('/'.join([self._preprocess_dir, RAW_LEVEL_DIR]))

        slice_index = 0
        while raw_data.readable():
            slice_name = utils.get_slice_path(
                self._preprocess_dir, 0, slice_index)
            level_slice = LevelSlice(slice_name)
            raw_slice = raw_data.read()
            level_slice.save(raw_slice)
            raw_slice_metadata[self._metadata['levels'][RAW_LEVEL_DIR]
                               ['names'][slice_index]] = raw_slice[0][0]
            slice_index += 1
        raw_data.close()

        with open('/'.join([self._preprocess_dir, RAW_LEVEL_DIR, METADATA]), 'w') as filewriter:
            dump(raw_slice_metadata, filewriter)

    def _preprocess_single_startegy(self, strategy):
        """Downsamples given data by the defined levels and strategy.

        Preprocesses the raw data with the given downsanpling startegy.
        Raw data is downsampeld to a set of levels of different downsample rate,
        data of each level broken down to small slices of constant size.
        Number of levels is determined by if number of records in the highest level
        reaches minimum_number_level.
        Info regarding levels and slices is kept in a metadata json file.

        Args:
            strategy: A string representing downsampling strategy.
        """
        if len(self._metadata['levels']['names']) <= 1:
            return
        prev_level = self._metadata['levels']['names'][0]
        for curr_level in self._metadata['levels']['names'][1:]:
            level_dir = '/'.join([self._preprocess_dir, strategy, curr_level])
            utils.mkdir(level_dir)
            level_metadata = self._single_level_downsample(
                strategy, prev_level, curr_level)
            with open('/'.join([level_dir, METADATA]), 'w') as filewriter:
                dump(level_metadata, filewriter)
            prev_level = curr_level

    def _get_raw_meta_info(self):
        """Gets line number, start, and end time from the file.

        Returns:
            A tuple of integer, float, float, that represents number of lines,
                start time, and end time, respctively.
        """
        start = end = -1
        raw_number_records = 0
        with open(self._rawfile, 'r') as filereader:
            for line in filereader:
                if start == -1:
                    start = float(line[:UNIX_TIMESTAMP_LENGTH])
                raw_number_records += 1
                end = line
            end = float(end[:UNIX_TIMESTAMP_LENGTH])

        return raw_number_records, start, end

    def _get_levels_metadata(self, raw_number_records, duration):
        """Gets level meta infomation for each level.

        Args:
            raw_number_records: An int that represents the number of raw records.
            duration: An int that represents duration of the experiment.

        Returns:
            A tuple of length 2, that contains level meta info ojbject and level names.
        """
        assert self._number_per_slice > 0
        assert self._downsample_level_factor > 1

        levels = []
        level_names = []
        number_records = raw_number_records
        index = 0
        while index == 0 or number_records >= self._minimum_number_level:
            frequency = number_records / duration
            level_name = utils.get_level_name(index)
            number_slices = ceil(
                number_records / self._number_per_slice)
            slice_names = [utils.get_slice_name(
                level_name, index) for index in range(number_slices)]
            level = {
                "names": slice_names,
                "frequency": frequency,
                "number": number_records
            }
            levels.append(level)
            level_names.append(level_name)

            index += 1
            number_records = number_records // self._downsample_level_factor
        return levels, level_names

    def _single_level_downsample(self, strategy, prev_level, curr_level):
        """Downsamples for one single level.

        Args:
            strategy: A string representing downsampling strategy.
            prev_level: A string of the name of the current level.
            curr_level: A string of the name of the previous level.

        Returns:
            A dict of metadata for the current level.
        """
        level_metadata = dict()
        curr_slice_names = self._metadata['levels'][curr_level]['names']
        prev_slice_names = self._metadata['levels'][prev_level]['names']

        slice_index = 0
        curr_slice_path = utils.get_slice_path(self._preprocess_dir,
                                               curr_level, slice_index, strategy)
        curr_level_slice = LevelSlice(curr_slice_path)

        for prev_slice_name in prev_slice_names:
            prev_slice_path = utils.get_slice_path(self._preprocess_dir,
                                                   prev_level, prev_slice_name, strategy)
            prev_level_slice = LevelSlice(prev_slice_path)
            prev_level_slice.read()
            prev_level_downsample = prev_level_slice.downsample(
                strategy, self._downsample_level_factor)
            curr_level_slice.add_records(prev_level_downsample)
            if curr_level_slice.get_number_records() >= self._number_per_slice:
                curr_level_slice.save()
                level_metadata[curr_slice_names
                               [slice_index]] = curr_level_slice.get_start()
                slice_index += 1
                curr_slice_path = utils.get_slice_path(self._preprocess_dir,
                                                       curr_level, slice_index, strategy)
                curr_level_slice = LevelSlice(curr_slice_path)

        curr_level_slice.save()
        level_metadata[curr_slice_names
                       [slice_index]] = curr_level_slice.get_start()
        return level_metadata

    def _binary_search(self, data_list, value, reverse=False):
        """Searches the index of the left or right element closest to the given value from the list,
        if reverse is true, the list is decreasing.
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
