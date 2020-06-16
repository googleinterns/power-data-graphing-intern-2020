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

app = Flask(__name__)
CORS(app)


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
                elif strategy == 'average':
                    average = [
                        sum([record[1][0]
                             for record in temp_store]) // len(temp_store),
                        sum([record[1][1]
                             for record in temp_store]) // len(temp_store),
                        temp_store[0][1][2]
                    ]
                    data.append(average)
                elif strategy == 'random':
                    data.append(
                        temp_store[random.randint(0, len(temp_store))][1])
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
    strategies = ['max', 'min', 'median', 'random', 'average']

    num_records = 1000090  # assume number of records is accessible upon deployment
    max_records = request.args.get('number', default=6000, type=int)
    strategy = request.args.get('strategy', default='avg', type=str)
    if not strategy in strategies:
        return 'Incorrect Strategy', 400

    data = downsample_raw_data(filename, num_records, max_records, strategy)
    return jsonify(data)


if __name__ == '__main__':
    app.run(port=5000)
