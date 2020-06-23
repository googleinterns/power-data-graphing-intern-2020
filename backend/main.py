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
import random
from heapq import heappop
from heapq import heappush
from flask import request
from flask import jsonify
from flask import Flask
from flask_cors import CORS

NUMBER_OF_RECORDS_PER_REQUEST = 1000
NUMBER_OF_RECORDS_PER_SECOND = 2000
SECOND_TO_MICROSECOND = 1E6

app = Flask(__name__)
CORS(app)

def triangle_area(point1, point2, point3):
    """Calculate the area of triangle

        Calculate the area of triangle formed by the given three points.

        Args:
            point1: Index of the first point
            point2: Index of the second point
            point3: Index of the third point

        Returns:
            Area in float
    """
    return abs(point1[0] * point2[1] -
     point1[1] * point2[0] + point2[0] * point3[1] - 
     point2[1] * point3[0] + point3[0] * point1[1] - 
     point3[1] * point1[0]) / 2

def parse_line(line):
    if not line:
        return None
    data_point = line.strip('\n').split(',')
    data_point[0] = float(data_point[0])
    data_point[1] = float(data_point[1])
    return data_point

_
def max_min_downsample(records, method):
    timespan = len(records) // NUMBER_OF_RECORDS_PER_SECOND
    if method == 'max':
        return [max(records[i * timespan: (i+1)*timespan], key=lambda record:record[1]) 
        for i in range(NUMBER_OF_RECORDS_PER_SECOND)]
    if method == 'min':
        return [min(records[i * timespan: (i+1)*timespan], key=lambda record:record[1]) 
        for i in range(NUMBER_OF_RECORDS_PER_SECOND)]
    return None

def downsample(filename, num_records, max_records, strategy):
    data = list()

    with open(filename, 'r') as filereader:
        temp_store = list()
        start_time = 0
        for i, line in enumerate(filereader):
            temp_store.append(parse_line(line))
            if temptemp_store[-1] is None or temp_store[-1][0] - \
                start_time > SECOND_TO_MICROSECOND:
                start_time = temp_store[-1][0]
                if strategy == 'max':
                    res = max_downsample(temp_store)
                data.extend(res)
                temp_store = list()


def downsample_raw_data(filename, num_records, max_records, strategy):
    """Desample power data

        Read power data from given filename, desample and limit number of records
        to the given number.
        The desample strategy is to select one data point per certain number to ensure that output
        data points are kept under threshold.

        Args:
            filename: The filename of data csv
            num_records: Total number of data points
            max_records: Max number of data points to output
            strategy: Data downsampling strategy

        Returns:
            A list of power data. For example:
            [
                ['1532523212', '53', 'SYSTEM'],
                ['1532523242', '33', 'SYSTEM']
            ]
    """
    data = list()
    frequency = num_records // max_records

    with open(filename, 'r') as filereader:
        temp_store = list()
        for i, line in enumerate(filereader):
            data_point = line.strip('\n').split(',')
            data_point[0] = float(data_point[0])
            data_point[1] = float(data_point[1])
            heappush(temp_store, [data_point[1], data_point])
            if i == max_records or (i > 0 and i % frequency == 0):
                if strategy == 'max':
                    data.append(max(temp_store, key=lambda dp: dp[0])[1])
                elif strategy == 'min':
                    data.append(heappop(temp_store)[1])
                elif strategy == 'median':
                    median = None
                    position = len(temp_store) // 2
                    for _ in range(position):
                        median = heappop(temp_store)
                    data.append(median[1])
                elif strategy == 'avg':
                    average = [
                        sum([record[1][0]
                             for record in temp_store]) // len(temp_store),
                        sum([record[1][1]
                             for record in temp_store]) // len(temp_store),
                        temp_store[0][1][2]
                    ]
                    data.append(average)
                elif strategy == 'lttb':
                    print('Strategy not implemented')
                else:
                    print('Strategy not identified')
                temp_store = list()
    return data


@app.route('/data')
def get_data():
    """HTTP endpoint to get data

        Retrives all power data from local file given a limit on number of
        records from request body.
    """
    filename = './DMM_result_single_channel.csv'
    strategies = ['max', 'min', 'median', 'avg']

    num_records = 1000090  # assume number of records is accessible upon deployment
    max_records = request.args.get('number', default=6000, type=int)
    strategy = request.args.get('strategy', default='avg', type=str)
    if not strategy in strategies:
        return 'Incorrect Strategy', 400

    data = downsample_raw_data(filename, num_records, max_records, strategy)
    return jsonify(data)


if __name__ == '__main__':
    app.run(port=5000)
