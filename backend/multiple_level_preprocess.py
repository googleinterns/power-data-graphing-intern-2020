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

from collections import defaultdict
from math import ceil
from json import dump
from json import load

from downsample import strategy_reducer
import utils

DOWNSAMPLE_LEVEL_FACTOR = 100
METADATA = 'metadata.json'
MINIMUM_NUMBER_OF_RECORDS_LEVEL = 600
NUMBER_OF_RECORDS_PER_SLICE = 200000
PREPROCESS_DIR = 'mld-prerpocess'
RAW_LEVEL_DIR = 'level0'
STRATEGIES = ['max', 'min', 'avg']
UNIX_TIMESTAMP_LENGTH = 16

TEST_FILENAME = 'rand.csv'


def multilevel_preprocess(filename,
                          parent_dir,
                          number_per_slice,
                          downsample_level_factor,
                          minimum_number_level):
    """Multiple level downsampling entry point.

    Downsamples the raw data from given filename with each of the strategy,
    in a hierarchical fation.

    Args:
        filename: A string that represents raw data file name to be downsampled.
        parent_dir: A string that represents the name of the parent_dir
            containing the preprocess files.
        number_per_slice: An int that represents number of records for one slice.
        downsample_level_factor: An int that represents downsample factor between levels.
        minimum_number_level: An int that represents the minimum number of records for a level.
    """
    metadata = dict()

    raw_number_records, start, end = _get_raw_meta_info(filename)
    metadata['start'] = int(start)
    metadata['end'] = int(end)
    metadata['raw_number'] = raw_number_records
    metadata['raw_file'] = filename

    levels, level_names = _get_levels_metadata(
        raw_number_records,
        end - start,
        number_per_slice,
        downsample_level_factor,
        minimum_number_level
    )

    metadata['levels'] = dict()
    metadata['levels']['names'] = level_names
    for name, level in zip(level_names, levels):
        metadata["levels"][name] = level

    experiment = utils.get_experiment_name(filename)
    preprocess_folder = '/'.join([parent_dir, experiment])

    utils.mkdir(preprocess_folder)
    raw_preprocess(metadata,
                   preprocess_folder, number_per_slice)
    with open('/'.join([preprocess_folder, METADATA]), 'w') as filewriter:
        dump(metadata, filewriter)
    for strategy in STRATEGIES:
        _preprocess_single_startegy(metadata, preprocess_folder, strategy,
                                    number_per_slice, downsample_level_factor)


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
    preprocess_folder = '/'.join([PREPROCESS_DIR, experiment])
    metadata_path = '/'.join([preprocess_folder, METADATA])

    with open(metadata_path, 'r') as filereader:
        metadata = load(filereader)

    if start is None:
        start = metadata['start']
    if end is None:
        end = metadata['end']

    if start > metadata['end'] or end < metadata['start']:
        return []

    required_frequency = number_records / (end - start)

    # Finds Downsample Level.
    target_level_index = binary_search(
        [metadata['levels'][level_name]['frequency']
         for level_name in metadata['levels']['names']],
        required_frequency, True)

    target_level = metadata['levels'][metadata['levels']
                                      ['names'][target_level_index]]
    if target_level_index == 0:
        metadata_dir = '/'.join([preprocess_folder, RAW_LEVEL_DIR, METADATA])
    else:
        metadata_dir = '/'.join([preprocess_folder, strategy,
                                 utils.get_level_name(target_level_index), METADATA])
    # Finds target slices.
    with open(metadata_dir, 'r') as filereader:
        level_metadata = load(filereader)
    first_slice = binary_search([level_metadata[single_slice]
                                 for single_slice in target_level['names']], start)
    last_slice = binary_search([level_metadata[single_slice]
                                for single_slice in target_level['names']], end)
    target_slices = target_level['names'][first_slice:last_slice+1]
    target_slice_paths = [utils.get_slice_path(
        preprocess_folder,
        target_level_index, single_slice, strategy) for single_slice in target_slices]
    # Reads records and downsamples.
    target_records = read_records(target_slice_paths, start, end)
    for channel in target_records.keys():
        downsample_factor = ceil(len(target_records[channel]) / number_records)
        downsampled_one_channel = strategy_reducer(
            target_records[channel], strategy, downsample_factor)
        downsampled_data.append({
            'name': channel,
            'data': [[record[0], record[1]] for record in downsampled_one_channel]
        })
    # Calculate precision.
    number_target_records = sum([len(target_channel)for target_channel in
                                 target_records.values()])
    number_result_records = sum([len(downsampeld_channel['data'])for downsampeld_channel in
                                 downsampled_data])
    if number_target_records == 0:
        precision = 0
    else:
        precision = number_result_records / \
            number_target_records * \
            (target_level['number']/metadata['raw_number'])
    return downsampled_data, precision


def _preprocess_single_startegy(metadata,
                                root_dir,
                                strategy,
                                number_per_slice,
                                downsample_level_factor):
    """Downsamples given data by the defined levels and strategy.

    Preprocesses the raw data with the given downsanpling startegy.
    Raw data is downsampeld to a set of levels of different downsample rate,
    data of each level broken down to small slices of constant size.
    Number of levels is determined by if number of records in the highest level
    reaches minimum_number_level.
    Info regarding levels and slices is kept in a metadata json file.

    Args:
        metadata: A dict that has metadata for downsample levels in dict type.
        root_dir: A string that represents the name of the directory containing
            the preprocess files.
        strategy: A string representing downsampling strategy.
        number_per_slice: An int that represents number of records for one slice.
        downsample_level_factor: An int that represents downsample factor between levels.
    """
    if len(metadata['levels']['names']) <= 1:
        return
    prev_level = metadata['levels']['names'][0]
    for curr_level in metadata['levels']['names'][1:]:
        level_dir = '/'.join([root_dir, strategy, curr_level])
        utils.mkdir(level_dir)
        level_metadata = _single_level_downsample(
            metadata,
            root_dir,
            strategy,
            prev_level,
            curr_level,
            number_per_slice,
            downsample_level_factor)
        with open('/'.join([level_dir, METADATA]), 'w') as filewriter:
            dump(level_metadata, filewriter)
        prev_level = curr_level


def _single_level_downsample(metadata,
                             parent_dir,
                             strategy,
                             prev_level,
                             curr_level,
                             number_per_slice,
                             downsample_level_factor):
    """Downsamples for one single level.

    Args:
        metadata: A dict that has metadata for downsample levels in dict type.
        parent_dir: A string that represents the name of the parent_dir
            containing the preprocess files.
        strategy: A string representing downsampling strategy.
        prev_level: A string of the name of the current level.
        curr_level: A string of the name of the previous level.
        number_per_slice: An int that represents number of records for one slice.
        downsample_level_factor: An int that represents downsample factor between levels.

    Returns:
        A dict of metadata for this level.
    """

    curr_level_store = defaultdict(list)
    prev_level_store = defaultdict(list)
    slice_start_time = None
    slice_index = 0

    curr_slices = metadata['levels'][curr_level]['names']
    level_metadata = dict()

    for prev_level_slice in metadata['levels'][prev_level]['names']:
        with open(utils.get_slice_path(parent_dir,
                                       prev_level, prev_level_slice, strategy), 'r') as filereader:
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
                utils.get_slice_path(parent_dir,
                                     curr_level, slice_index, strategy), curr_level_store)
            level_metadata[curr_slices[slice_index]] = slice_start_time
            curr_level_store = defaultdict(list)
            slice_start_time = None
            slice_index += 1
    if slice_index < len(curr_slices):
        _write_records_to_file(
            utils.get_slice_path(parent_dir, curr_level, slice_index, strategy), curr_level_store)
        level_metadata[curr_slices[slice_index]] = slice_start_time
    return level_metadata


def _write_records_to_file(filename, records):
    """Writes records to the given file.

    Args:
        filename: A string of the filename.
        records: A list or dict of records in chronological order.
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


def _get_raw_meta_info(filename):
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
    while index == 0 or number_records >= minimum_number_level:
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


def raw_preprocess(metadata,
                   root_dir,
                   number_per_slice):
    """Splits raw data into slices. keep start time of each slice in a json file.

    Args:
        metadata: A dict that has metadata for downsample levels in dict type.
        root_dir: A string that represents the directory of the raw data.
        number_per_slice: An int of records to keep for each slice.
    """
    raw_store = list()
    raw_slice_metadata = dict()
    utils.mkdir('/'.join([root_dir, RAW_LEVEL_DIR]))
    with open(metadata['raw_file']) as filereader:
        slice_index = 0
        for line in filereader:
            record = utils.parse_csv_line(line)
            raw_store.append(record)
            if len(raw_store) >= number_per_slice:
                output_filename = utils.get_slice_path(
                    root_dir, 0, slice_index)
                raw_slice_metadata[metadata['levels']
                                   [RAW_LEVEL_DIR]['names'][slice_index]] = raw_store[0][0]
                _write_records_to_file(output_filename, raw_store)
                raw_store = list()
                slice_index += 1
        if raw_store and slice_index < len(metadata['levels'][RAW_LEVEL_DIR]['names']):
            output_filename = utils.get_slice_path(
                root_dir, 0, slice_index)
            raw_slice_metadata[metadata['levels'][RAW_LEVEL_DIR]
                               ['names'][slice_index]] = raw_store[0][0]
            _write_records_to_file(output_filename, raw_store)
    with open('/'.join([root_dir, RAW_LEVEL_DIR, METADATA]), 'w') as filewriter:
        dump(raw_slice_metadata, filewriter)


def read_records(target_slices, start, end):
    """Reads records from given slices that are in the range.

    Args:
        target_slices: A list of string of slice names to read.
        start: An int of the start time.
        end: An int of the end time

    Returns:
        A list of records.
    """
    data = defaultdict(list)
    for slice_path in target_slices:
        with open(slice_path, 'r') as filereader:
            for line in filereader.readlines():
                record = utils.parse_csv_line(line)
                if record and (start is None or start <=
                               record[0]) and (end is None or record[0] <= end):
                    data[record[2]].append(record)
    return data


def binary_search(data_list, value, reverse=False):
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
