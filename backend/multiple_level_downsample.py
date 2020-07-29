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

"""Multiple-level downsampling module."""

from collections import defaultdict
from math import ceil
from json import dump
from json import load

from downsample import strategy_reducer
import utils

DOWNSAMPLE_LEVEL_FACTOR = 100
MINIMUM_NUMBER_OF_RECORDS_LEVEL = 600
NUMBER_OF_RECORDS_PER_SLICE = 200000
PREPROCESS_DIR = 'mld-prerpocess'
STRATEGIES = ['max', 'min', 'avg']
UNIX_TIMESTAMP_LENGTH = 16

TEST_FILENAME = 'rand.csv'


def _preprocess_single_startegy(filename,
                                strategy,
                                folder,
                                number_per_slice,
                                downsample_level_factor,
                                minimum_number_level):
    """Applies multiple-level downsampling on the given file.

    Preprocesses the raw data with the given downsanpling startegy.
    Raw data is downsampeld to a set of levels of different downsample rate,
    data of each level broken down to small slices of constant size.
    Number of levels is determined by if number of records in the highest level
    reaches minimum_number_level.
    Info regarding levels and slices is kept in a metadata json file.

    Args:
        filename: A string that represents raw data file name to be downsampled.
        strategy: A string that represents which downsampling strategy to use.
        folder: A string that represents the name of the folder containing the preprocess files.
        number_per_slice: An int that represents number of records for one slice.
        downsample_level_factor: An int that represents downsample factor between levels.
        minimum_number_level: An int that represents the minimum number of records for a level.
    """
    metadata = dict()

    raw_number_records, start, end = _get_basic_meta_info(filename)
    metadata['start'] = int(start)
    metadata['end'] = int(end)
    metadata['raw_number'] = raw_number_records
    metadata['raw_file'] = filename
    metadata['slices'] = dict()

    levels, level_names = _get_levels_metadata(
        raw_number_records, end - start,
        number_per_slice,
        downsample_level_factor,
        minimum_number_level)
    metadata['levels'] = dict()
    metadata['levels']['names'] = level_names
    for name, level in zip(level_names, levels):
        metadata["levels"][name] = level
    _levels_downsample(metadata, folder, strategy, number_per_slice,
                       downsample_level_factor)
    with open('/'.join([folder, strategy, 'metadata.json']), 'w') as filewriter:
        dump(metadata, filewriter)


def _levels_downsample(metadata, folder, strategy, number_per_slice, downsample_level_factor):
    """Downsamples given data by the defined levels.

    Args:
        metadata: A dict that has metadata for downsample levels in dict type.
        folder: A string that represents the name of the folder containing the preprocess files.
        strategy: A string representing downsampling strategy.
        number_per_slice: An int that represents number of records for one slice.
        downsample_level_factor: An int that represents downsample factor between levels.
    """
    prev_level = None
    for curr_level in metadata['levels']['names']:
        utils.mkdir('/'.join([folder, strategy, curr_level]))
        _single_level_downsample(
            metadata,
            '/'.join([folder, strategy]),
            strategy, prev_level,
            curr_level, number_per_slice,
            downsample_level_factor)
        prev_level = curr_level


def _single_level_downsample(metadata,
                             folder,
                             strategy,
                             prev_level,
                             curr_level,
                             number_per_slice,
                             downsample_level_factor):
    """Downsamples for one single level.

    Args:
        metadata: A dict that has metadata for downsample levels in dict type.
        folder: A string that represents the name of the folder containing the preprocess files.
        strategy: A string representing downsampling strategy.
        prev_level: A string of the name of the current level.
        curr_level: A string of the name of the previous level.
        number_per_slice: An int that represents number of records for one slice.
        downsample_level_factor: An int that represents downsample factor between levels.
    """
    # Level 0 for splitting raw data.
    if prev_level is None:
        raw_store = list()
        with open(metadata['raw_file']) as filereader:
            slice_index = 0
            for line in filereader:
                record = utils.parse_csv_line(line)
                raw_store.append(record)
                if len(raw_store) >= number_per_slice:
                    output_filename = '/'.join(
                        [folder, metadata['levels'][curr_level]['names'][slice_index]])
                    metadata['slices'][metadata['levels'][curr_level]
                                       ['names'][slice_index]] = raw_store[0][0]
                    _write_records_to_file(output_filename, raw_store)
                    raw_store = list()
                    slice_index += 1
            if raw_store and slice_index < len(metadata['levels'][curr_level]['names']):
                output_filename = '/'.join([folder, metadata['levels']
                                            [curr_level]['names'][slice_index]])
                metadata['slices'][metadata['levels'][curr_level]
                                   ['names'][slice_index]] = raw_store[0][0]
                _write_records_to_file(output_filename, raw_store)
        return

    # Level 1+ downsampling.
    prev_level_store = defaultdict(list)
    curr_level_store = defaultdict(list)
    slice_index = 0
    curr_slices = metadata['levels'][curr_level]['names']

    slice_start_time = None
    for prev_level_slice in metadata['levels'][prev_level]['names']:
        with open('/'.join([folder, prev_level_slice]), 'r') as filereader:
            for line in filereader:
                record = utils.parse_csv_line(line)
                prev_level_store[record[2]].append(record)
                if slice_start_time is None:
                    slice_start_time = record[0]
        for channel in prev_level_store.keys():
            curr_level_store[channel].extend(strategy_reducer(
                prev_level_store[channel], strategy, downsample_level_factor))
        prev_level_store = defaultdict(list)

        # Write to slice if number of records in current store is above threshold.
        if sum([len(channel) for channel in curr_level_store.values()]) >= number_per_slice:
            _write_records_to_file(
                '/'.join([folder, curr_slices[slice_index]]), curr_level_store)
            metadata['slices'][curr_slices[slice_index]] = slice_start_time
            curr_level_store = defaultdict(list)
            slice_start_time = None
            slice_index += 1
    if slice_index < len(curr_slices):
        _write_records_to_file(
            '/'.join([folder, curr_slices[slice_index]]), curr_level_store)
        metadata['slices'][curr_slices[slice_index]] = slice_start_time


def _write_records_to_file(filename, records):
    """Writes records to the given file.

    Args:
        filename: A string of the filename.
        records: A list of records in chronological order.
    """
    if not records:
        return
    records_list = records
    if isinstance(records, defaultdict):
        records_list = list()
        for channel in records.keys():
            records_list.extend(records[channel])
        records_list = sorted(records_list, key=lambda record: record[0])
    with open(filename, 'w') as filewriter:
        data_csv = utils.convert_to_csv(records_list)
        filewriter.write(data_csv)
        filewriter.flush()


def _get_basic_meta_info(filename):
    """Gets line number, start, and end time from the file.

    Args:
        filename: A string for the name of the file.

    Returns:
        A tuple of integer, float, float, that represents number of lines,
            start time, and end time, respctively.
    """
    start = end = -1
    raw_number_records = 0
    with open(filename, 'r') as filereader:
        for line in filereader:
            if start == -1:
                start = float(line[:UNIX_TIMESTAMP_LENGTH])
            raw_number_records += 1
            end = line
        end = float(end[:UNIX_TIMESTAMP_LENGTH])

    return raw_number_records, start, end


def _get_levels_metadata(raw_number_records,
                         duration,
                         number_per_slice,
                         downsample_level_factor,
                         minimum_number_level):
    """Gets level meta infomation for each level.

    Args:
        raw_number_records: An int that represents number of raw records.
        duration: An int that represents duration of the experiment.
        number_per_slice: An int that represents number of records for one slice.
        downsample_level_factor: An int that represents downsample factor between levels.
        minimum_number_level: An int that represents the minimum number of records for a level.

    Returns:
        A tuple of length 2, that contains level meta info ojbject and level names.
    """
    assert number_per_slice > 0
    assert downsample_level_factor > 1

    levels = []
    level_names = []
    number_records = raw_number_records
    index = 0
    while index == 0 or number_records > minimum_number_level:
        frequency = number_records / duration
        level_name = utils.get_level_name(index)
        number_slices = ceil(
            number_records / number_per_slice)
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
        number_records = number_records // downsample_level_factor
    return levels, level_names


def multilevel_preprocess(filename,
                          folder,
                          number_per_slice,
                          downsample_level_factor,
                          minimum_number_level):
    """Multiple level downsampling entry point.

    Downsamples the raw data from given filename with each of the strategy,
    in a hierarchical fation.

    Args:
        filename: A string that represents raw data file name to be downsampled.
        folder: A string that represents the name of the folder containing the preprocess files.
        number_per_slice: An int that represents number of records for one slice.
        downsample_level_factor: An int that represents downsample factor between levels.
        minimum_number_level: An int that represents the minimum number of records for a level.
    """
    experiment = utils.get_experiment_name(filename)
    preprocess_folder = '/'.join([folder, experiment])

    utils.mkdir(preprocess_folder)
    for strategy in STRATEGIES:
        _preprocess_single_startegy(filename, strategy, preprocess_folder,
                                    number_per_slice, downsample_level_factor, minimum_number_level)


def multilevel_inference(filename,
                         strategy,
                         number_records,
                         start,
                         end
                         ):
    """Reads the preprocessing file and downsample with the given strategy for HTTP request.

    Assume the records file is on local disk, read the records and downsample the records
    to be within max records.
    Optional arguments start and end to specify a timespan in which records must be laid.

    Args:
        filename: A string representing name of the records file.
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
    metadata = None
    downsampled_data = []

    experiment = utils.get_experiment_name(filename)
    preprocess_folder = '/'.join([PREPROCESS_DIR, experiment, strategy])
    metadata_path = '/'.join([preprocess_folder, 'metadata.json'])

    with open(metadata_path, 'r') as filereader:
        metadata = load(filereader)

    if start is None:
        start = metadata['start']
    if end is None:
        end = metadata['end']
    required_frequency = number_records / (end - start)

    target_level_index = binary_search(
        [metadata['levels'][level_name]['frequency']
         for level_name in metadata['levels']['names']],
        required_frequency, True)

    target_level = metadata['levels'][metadata['levels']
                                      ['names'][target_level_index]]
    first_slice = binary_search([metadata['slices'][slice]
                                 for slice in target_level['names']], start)
    last_slice = binary_search([metadata['slices'][slice]
                                for slice in target_level['names']], end)
    target_slices = target_level['names'][first_slice:last_slice+1]

    target_records = read_records(
        preprocess_folder, target_slices, start, end)
    for channel in target_records.keys():
        downsample_factor = ceil(len(target_records[channel]) / number_records)
        downsampled_one_channel = strategy_reducer(
            target_records[channel], strategy, downsample_factor)
        downsampled_data.append({
            'name': channel,
            'data': [[record[0], record[1]] for record in downsampled_one_channel]
        })
    average_number_target_records = sum([len(target_channel)for target_channel in
                                         target_records.values()]) / len(target_records.keys())
    average_number_result_records = sum([len(downsampeld_channel['data'])for downsampeld_channel in
                                         downsampled_data]) / len(downsampled_data)
    precision = average_number_result_records / \
        average_number_target_records * \
        (target_level['number']/metadata['raw_number'])
    return downsampled_data, precision


def read_records(folder, target_slices, start, end):
    data = defaultdict(list)
    for slice_name in target_slices:
        with open('/'.join([folder, slice_name])) as filereader:
            for line in filereader.readlines():
                record = utils.parse_csv_line(line)
                if record and (start is None or start <=
                               record[0]) and (end is None or record[0] <= end):
                    data[record[2]].append(record)
    return data


def binary_search(data_list, value, reverse=False):
    """Searches the left or right element closest to the given value from the list."""
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


if __name__ == '__main__':
    import time
    # Profiling
    starttime = time.time()
    multilevel_preprocess(TEST_FILENAME, PREPROCESS_DIR, NUMBER_OF_RECORDS_PER_SLICE,
                          DOWNSAMPLE_LEVEL_FACTOR, MINIMUM_NUMBER_OF_RECORDS_LEVEL)
    multilevel_inference(TEST_FILENAME, 'max', 600,
                         1573149336265888-6000000, None)

    print('time: ', (time.time() - starttime))
